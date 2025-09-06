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


@router.post('/{institution_id}/profile_image', status_code=HTTPStatus.CREATED)
async def upload_institution_profile_image(
    institution_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    SCRIPT_SELECT = """
        SELECT profile_image_url
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

    if institution['profile_image_url']:
        old_filename = os.path.basename(institution['profile_image_url'])
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
        SET profile_image_url = %(public_path)s
        WHERE institution_id = %(institution_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'institution_id': institution_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/{institution_id}/profile_image', status_code=HTTPStatus.OK)
async def delete_institution_profile_image(institution_id: str, conn: Conn):
    SCRIPT_SELECT = """
        SELECT profile_image_url
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

    if not institution['profile_image_url']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem geral para excluir.',
        )

    filename = os.path.basename(institution['profile_image_url'])
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE institution
        SET profile_image_url = NULL
        WHERE institution_id = %(institution_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'institution_id': institution_id},
    )
    return {'message': 'Imagem geral excluída com sucesso.'}


@router.post(
    '/{institution_id}/background_image', status_code=HTTPStatus.CREATED
)
async def upload_institution_background_image(
    institution_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    SCRIPT_SELECT = """
        SELECT background_image_url
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

    if institution['background_image_url']:
        old_filename = os.path.basename(institution['background_image_url'])
        old_file_path = os.path.join(UPLOAD_DIR, old_filename)
        try:
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        except OSError as e:
            print(
                f'Erro ao deletar o arquivo de fundo antigo {old_file_path}: {e}'
            )

    filename = f'{uuid4()}{os.path.splitext(file.filename)[1]}'
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, 'wb') as f:
        f.write(await file.read())

    public_path = f'/institution/uploads/{institution_id}/{filename}'
    SCRIPT_SQL = """
        UPDATE institution
        SET background_image_url = %(public_path)s
        WHERE institution_id = %(institution_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'institution_id': institution_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/{institution_id}/background_image', status_code=HTTPStatus.OK)
async def delete_institution_background_image(institution_id: str, conn: Conn):
    SCRIPT_SELECT = """
        SELECT background_image_url
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

    if not institution['background_image_url']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de fundo para excluir.',
        )

    filename = os.path.basename(institution['background_image_url'])
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE institution
        SET background_image_url = NULL
        WHERE institution_id = %(institution_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'institution_id': institution_id},
    )
    return {'message': 'Imagem de fundo excluída com sucesso.'}
