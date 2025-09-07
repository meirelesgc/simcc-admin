import os
from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from simcc.core.connection import Connection
from simcc.core.database import get_conn

UPLOAD_DIR = 'simcc/storage/upload'

router = APIRouter(prefix='/group/upload')

Conn = Annotated[Connection, Depends(get_conn)]


async def get_group_and_check_existence(group_id: str, conn: Conn):
    SCRIPT_SELECT = """
        SELECT *
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


@router.post('/{group_id}/icon', status_code=HTTPStatus.CREATED)
async def upload_group_icon(
    group_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    group = await get_group_and_check_existence(group_id, conn)

    if group['icon_url']:
        old_filename = os.path.basename(group['icon_url'])
        old_file_path = os.path.join(UPLOAD_DIR, old_filename)
        try:
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        except OSError as e:
            print(f'Erro ao deletar o arquivo antigo {old_file_path}: {e}')

    filename = f'{uuid4()}{os.path.splitext(file.filename)[1]}'
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, 'wb') as f:
        f.write(await file.read())

    public_path = f'/group/uploads/{group_id}/{filename}'
    SCRIPT_SQL = """
        UPDATE research_group
        SET icon_url = %(public_path)s
        WHERE id = %(group_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'group_id': group_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/{group_id}/icon', status_code=HTTPStatus.OK)
async def delete_group_icon(group_id: str, conn: Conn):
    group = await get_group_and_check_existence(group_id, conn)

    if not group['icon_url']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhum ícone para excluir.',
        )

    filename = os.path.basename(group['icon_url'])
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE research_group
        SET icon_url = NULL
        WHERE id = %(group_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'group_id': group_id},
    )
    return {'message': 'Ícone excluído com sucesso.'}


@router.post('/{group_id}/cover', status_code=HTTPStatus.CREATED)
async def upload_group_cover(
    group_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    group = await get_group_and_check_existence(group_id, conn)

    if group['cover_url']:
        old_filename = os.path.basename(group['cover_url'])
        old_file_path = os.path.join(UPLOAD_DIR, old_filename)
        try:
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        except OSError as e:
            print(
                f'Erro ao deletar o arquivo de capa antigo {old_file_path}: {e}'
            )

    filename = f'{uuid4()}{os.path.splitext(file.filename)[1]}'
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, 'wb') as f:
        f.write(await file.read())

    public_path = f'/group/uploads/{group_id}/{filename}'
    SCRIPT_SQL = """
        UPDATE research_group
        SET cover_url = %(public_path)s
        WHERE id = %(group_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'group_id': group_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/{group_id}/cover', status_code=HTTPStatus.OK)
async def delete_group_cover(group_id: str, conn: Conn):
    group = await get_group_and_check_existence(group_id, conn)

    if not group['cover_url']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de capa para excluir.',
        )

    filename = os.path.basename(group['cover_url'])
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE research_group
        SET cover_url = NULL
        WHERE id = %(group_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'group_id': group_id},
    )
    return {'message': 'Imagem de capa excluída com sucesso.'}
