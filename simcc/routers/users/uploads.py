import os
from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from simcc.core.connection import Connection
from simcc.core.database import get_conn
from simcc.schemas import user_model
from simcc.security import get_current_user

UPLOAD_DIR = 'simcc/storage/upload'

router = APIRouter(prefix='/user/upload')

Conn = Annotated[Connection, Depends(get_conn)]
CurrentUser = Annotated[user_model.User, Depends(get_current_user)]


@router.post('/profile_image', status_code=HTTPStatus.CREATED)
async def upload_profile_image(
    conn: Conn,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    if current_user.profile_image_url:
        old_filename = os.path.basename(current_user.profile_image_url)
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

    public_path = f'/uploads/{filename}'
    SCRIPT_SQL = """
        UPDATE users
        SET profile_image_url = %(public_path)s
        WHERE user_id = %(user_id)s
        """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'user_id': current_user.user_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/profile_image', status_code=HTTPStatus.OK)
async def delete_profile_image(conn: Conn, current_user: CurrentUser):
    if not current_user.profile_image_url:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de perfil para excluir.',
        )

    filename = os.path.basename(current_user.profile_image_url)
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE users
        SET profile_image_url = NULL
        WHERE user_id = %(user_id)s
        """
    await conn.exec(
        SCRIPT_SQL,
        params={'user_id': current_user.user_id},
    )
    return {'message': 'Imagem de perfil excluída com sucesso.'}


@router.post('/background_image', status_code=HTTPStatus.CREATED)
async def upload_background_image(
    conn: Conn,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    if current_user.background_image_url:
        old_filename = os.path.basename(current_user.background_image_url)
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

    public_path = f'/uploads/{filename}'
    SCRIPT_SQL = """
        UPDATE users
        SET background_image_url = %(public_path)s
        WHERE user_id = %(user_id)s
        """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'user_id': current_user.user_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/background_image', status_code=HTTPStatus.OK)
async def delete_background_image(conn: Conn, current_user: CurrentUser):
    if not current_user.background_image_url:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de fundo para excluir.',
        )

    filename = os.path.basename(current_user.background_image_url)
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE users
        SET background_image_url = NULL
        WHERE user_id = %(user_id)s
        """
    await conn.exec(
        SCRIPT_SQL,
        params={'user_id': current_user.user_id},
    )
    return {'message': 'Imagem de fundo excluída com sucesso.'}
