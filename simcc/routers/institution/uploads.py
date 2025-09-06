import os
from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from simcc.core.connection import Connection
from simcc.core.database import get_conn

UPLOAD_DIR = 'simcc/storage/upload'

router = APIRouter(prefix='/institution/upload')

Conn = Annotated[Connection, Depends(get_conn)]


async def get_institution_and_check_existence(institution_id: str, conn: Conn):
    """
    Função utilitária para buscar a instituição e verificar sua existência.
    """
    SCRIPT_SELECT = """
        SELECT *
        FROM institution
        WHERE institution_id = %(institution_id)s
    """
    institution = await conn.select(
        SCRIPT_SELECT, params={'institution_id': institution_id}, one=True
    )
    if not institution:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Instituição não encontrada.',
        )
    return institution


@router.post('/{institution_id}/icon', status_code=HTTPStatus.CREATED)
async def upload_institution_icon(
    institution_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    institution = await get_institution_and_check_existence(
        institution_id, conn
    )

    if institution['icon_url']:
        old_filename = os.path.basename(institution['icon_url'])
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

    public_path = f'/institution/uploads/{institution_id}/{filename}'
    SCRIPT_SQL = """
        UPDATE institution
        SET icon_url = %(public_path)s
        WHERE institution_id = %(institution_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'institution_id': institution_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/{institution_id}/icon', status_code=HTTPStatus.OK)
async def delete_institution_icon(institution_id: str, conn: Conn):
    institution = await get_institution_and_check_existence(
        institution_id, conn
    )

    if not institution['icon_url']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhum ícone para excluir.',
        )

    filename = os.path.basename(institution['icon_url'])
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE institution
        SET icon_url = NULL
        WHERE institution_id = %(institution_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'institution_id': institution_id},
    )
    return {'message': 'Ícone excluído com sucesso.'}


@router.post('/{institution_id}/cover', status_code=HTTPStatus.CREATED)
async def upload_institution_cover(
    institution_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    institution = await get_institution_and_check_existence(
        institution_id, conn
    )

    if institution['cover_url']:
        old_filename = os.path.basename(institution['cover_url'])
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

    public_path = f'/institution/uploads/{institution_id}/{filename}'
    SCRIPT_SQL = """
        UPDATE institution
        SET cover_url = %(public_path)s
        WHERE institution_id = %(institution_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'institution_id': institution_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/{institution_id}/cover', status_code=HTTPStatus.OK)
async def delete_institution_cover(institution_id: str, conn: Conn):
    institution = await get_institution_and_check_existence(
        institution_id, conn
    )

    if not institution['cover_url']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de capa para excluir.',
        )

    filename = os.path.basename(institution['cover_url'])
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE institution
        SET cover_url = NULL
        WHERE institution_id = %(institution_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'institution_id': institution_id},
    )
    return {'message': 'Imagem de capa excluída com sucesso.'}
