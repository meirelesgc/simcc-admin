import glob
import os
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.schemas import user_model
from simcc.security import get_current_user

UPLOAD_DIR = 'simcc/storage/upload'

router = APIRouter(prefix='/user/upload')

Conn = Annotated[Connection, Depends(get_conn)]
CurrentUser = Annotated[user_model.User, Depends(get_current_user)]


async def check_user_existence(user_id: str, conn: Conn):
    SCRIPT_SELECT = """
        SELECT user_id FROM public.user WHERE user_id = %(user_id)s
    """
    user = await conn.select(
        SCRIPT_SELECT, params={'user_id': user_id}, one=True
    )
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado.',
        )
    return user


async def _get_generic_file_response(entity_id: str, file_type: str):
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


@router.get('/my/icon', response_class=FileResponse, summary='Obter meu ícone')
async def get_my_icon(current_user: CurrentUser):
    return await _get_generic_file_response(str(current_user.user_id), 'icon')


@router.get(
    '/{user_id}/icon',
    response_class=FileResponse,
    summary='Obter ícone de um usuário',
)
async def get_user_icon_by_id(user_id: UUID, conn: Conn):
    await check_user_existence(str(user_id), conn)
    return await _get_generic_file_response(str(user_id), 'icon')


@router.post(
    '/icon', status_code=HTTPStatus.CREATED, summary='Fazer upload de ícone'
)
async def upload_user_icon(
    current_user: CurrentUser, file: UploadFile = File(...)
):
    return await _upload_generic_file(str(current_user.user_id), 'icon', file)


@router.delete('/icon', status_code=HTTPStatus.OK, summary='Excluir meu ícone')
async def delete_user_icon(current_user: CurrentUser):
    if not await _delete_generic_file(str(current_user.user_id), 'icon'):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhum ícone para excluir.',
        )
    return {'message': 'Ícone excluído com sucesso.'}


@router.get(
    '/my/cover', response_class=FileResponse, summary='Obter minha capa'
)
async def get_my_cover(current_user: CurrentUser):
    return await _get_generic_file_response(str(current_user.user_id), 'cover')


@router.get(
    '/{user_id}/cover',
    response_class=FileResponse,
    summary='Obter capa de um usuário',
)
async def get_user_cover_by_id(user_id: UUID, conn: Conn):
    await check_user_existence(str(user_id), conn)
    return await _get_generic_file_response(str(user_id), 'cover')


@router.post(
    '/cover', status_code=HTTPStatus.CREATED, summary='Fazer upload de capa'
)
async def upload_user_cover(
    current_user: CurrentUser, file: UploadFile = File(...)
):
    return await _upload_generic_file(str(current_user.user_id), 'cover', file)


@router.delete(
    '/cover', status_code=HTTPStatus.OK, summary='Excluir minha capa'
)
async def delete_user_cover(current_user: CurrentUser):
    if not await _delete_generic_file(str(current_user.user_id), 'cover'):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de capa para excluir.',
        )
    return {'message': 'Imagem de capa excluída com sucesso.'}
