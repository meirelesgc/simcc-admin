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


@router.post('/icon', status_code=HTTPStatus.CREATED)
async def upload_icon_image(
    conn: Conn,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    if current_user.icon_url:
        old_filename = os.path.basename(current_user.icon_url)
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
        SET icon_url = %(public_path)s
        WHERE user_id = %(user_id)s
        """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'user_id': current_user.user_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/icon', status_code=HTTPStatus.OK)
async def delete_icon_image(conn: Conn, current_user: CurrentUser):
    if not current_user.icon_url:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhum ícone para excluir.',
        )

    filename = os.path.basename(current_user.icon_url)
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE users
        SET icon_url = NULL
        WHERE user_id = %(user_id)s
        """
    await conn.exec(
        SCRIPT_SQL,
        params={'user_id': current_user.user_id},
    )
    return {'message': 'Ícone excluído com sucesso.'}


@router.post('/cover', status_code=HTTPStatus.CREATED)
async def upload_cover_image(
    conn: Conn,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    if current_user.cover_url:
        old_filename = os.path.basename(current_user.cover_url)
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

    public_path = f'/uploads/{filename}'
    SCRIPT_SQL = """
        UPDATE users
        SET cover_url = %(public_path)s
        WHERE user_id = %(user_id)s
        """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'user_id': current_user.user_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/cover', status_code=HTTPStatus.OK)
async def delete_cover_image(conn: Conn, current_user: CurrentUser):
    if not current_user.cover_url:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de capa para excluir.',
        )

    filename = os.path.basename(current_user.cover_url)
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE users
        SET cover_url = NULL
        WHERE user_id = %(user_id)s
        """
    await conn.exec(
        SCRIPT_SQL,
        params={'user_id': current_user.user_id},
    )
    return {'message': 'Imagem de capa excluída com sucesso.'}
