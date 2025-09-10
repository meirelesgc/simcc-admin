import glob
import os
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from simcc.core.connection import Connection
from simcc.core.database import get_conn

UPLOAD_DIR = 'simcc/storage/upload'

router = APIRouter(prefix='/group/upload')

Conn = Annotated[Connection, Depends(get_conn)]


async def get_group_and_check_existence(group_id: str, conn: Conn):
    SCRIPT_SELECT = """
        SELECT id
        FROM research_group
        WHERE id = %(group_id)s
    """
    group = await conn.select(
        SCRIPT_SELECT, params={'group_id': group_id}, one=True
    )
    if not group:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Grupo de pesquisa não encontrado.',
        )
    return group


# --- Funções Genéricas Reutilizáveis ---


async def _get_generic_file_response(entity_id: str, file_type: str):
    """Busca e retorna um arquivo genérico como resposta."""
    friendly_name_map = {'icon': 'Ícone', 'cover': 'Capa'}
    friendly_name = friendly_name_map.get(file_type, 'Arquivo')

    search_pattern = os.path.join(UPLOAD_DIR, f'{file_type}_{entity_id}.*')
    found_files = glob.glob(search_pattern)

    if not found_files:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'{friendly_name} não encontrado.',
        )

    file_path = found_files[0]
    return FileResponse(path=file_path)


async def _delete_generic_file(entity_id: str, file_type: str):
    """Deleta arquivos genéricos existentes."""
    search_pattern = os.path.join(UPLOAD_DIR, f'{file_type}_{entity_id}.*')
    existing_files = glob.glob(search_pattern)

    if not existing_files:
        return False

    for file_path in existing_files:
        try:
            os.remove(file_path)
        except OSError as e:
            print(f'Erro ao deletar o arquivo antigo {file_path}: {e}')

    return True


async def _upload_generic_file(
    entity_id: str, file_type: str, file: UploadFile
):
    """Salva um arquivo genérico, substituindo o antigo se existir."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    await _delete_generic_file(entity_id, file_type)

    extension = os.path.splitext(file.filename)[1]
    filename = f'{file_type}_{entity_id}{extension}'
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
    except IOError as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Não foi possível salvar o arquivo: {e}',
        )

    return {'filename': filename}


# --- Endpoints para ÍCONE ---


@router.get('/{group_id}/icon', response_class=FileResponse)
async def get_group_icon(group_id: str, conn: Conn):
    await get_group_and_check_existence(group_id, conn)
    return await _get_generic_file_response(group_id, 'icon')


@router.post('/{group_id}/icon', status_code=HTTPStatus.CREATED)
async def upload_group_icon(
    group_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    await get_group_and_check_existence(group_id, conn)
    return await _upload_generic_file(group_id, 'icon', file)


@router.delete('/{group_id}/icon', status_code=HTTPStatus.OK)
async def delete_group_icon(group_id: str, conn: Conn):
    await get_group_and_check_existence(group_id, conn)

    if not await _delete_generic_file(group_id, 'icon'):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhum ícone para excluir.',
        )

    return {'message': 'Ícone excluído com sucesso.'}


@router.get('/{group_id}/cover', response_class=FileResponse)
async def get_group_cover(group_id: str, conn: Conn):
    await get_group_and_check_existence(group_id, conn)
    return await _get_generic_file_response(group_id, 'cover')


@router.post('/{group_id}/cover', status_code=HTTPStatus.CREATED)
async def upload_group_cover(
    group_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    await get_group_and_check_existence(group_id, conn)
    return await _upload_generic_file(group_id, 'cover', file)


@router.delete('/{group_id}/cover', status_code=HTTPStatus.OK)
async def delete_group_cover(group_id: str, conn: Conn):
    await get_group_and_check_existence(group_id, conn)

    if not await _delete_generic_file(group_id, 'cover'):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de capa para excluir.',
        )

    return {'message': 'Imagem de capa excluída com sucesso.'}
