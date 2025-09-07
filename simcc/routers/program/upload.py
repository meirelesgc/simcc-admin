import os
from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from simcc.core.connection import Connection
from simcc.core.database import get_conn

UPLOAD_DIR = 'simcc/storage/upload'

router = APIRouter(prefix='/graduate-program/upload')

Conn = Annotated[Connection, Depends(get_conn)]


async def get_program_and_check_existence(program_id: str, conn: Conn):
    """
    Função utilitária para buscar o programa de pós-graduação e verificar sua existência.
    """
    SCRIPT_SELECT = """
        SELECT *
        FROM graduate_program
        WHERE graduate_program_id = %(program_id)s
    """
    program = await conn.select(
        SCRIPT_SELECT, params={'program_id': program_id}, one=True
    )
    if not program:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Programa de pós-graduação não encontrado.',
        )
    return program


@router.post('/{program_id}/icon', status_code=HTTPStatus.CREATED)
async def upload_program_icon(
    program_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    program = await get_program_and_check_existence(program_id, conn)

    if program['icon_url']:
        old_filename = os.path.basename(program['icon_url'])
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

    public_path = f'/graduate-program/uploads/{program_id}/{filename}'
    SCRIPT_SQL = """
        UPDATE graduate_program
        SET icon_url = %(public_path)s
        WHERE graduate_program_id = %(program_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'program_id': program_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/{program_id}/icon', status_code=HTTPStatus.OK)
async def delete_program_icon(program_id: str, conn: Conn):
    program = await get_program_and_check_existence(program_id, conn)

    if not program['icon_url']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhum ícone para excluir.',
        )

    filename = os.path.basename(program['icon_url'])
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE graduate_program
        SET icon_url = NULL
        WHERE graduate_program_id = %(program_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'program_id': program_id},
    )
    return {'message': 'Ícone excluído com sucesso.'}


@router.post('/{program_id}/cover', status_code=HTTPStatus.CREATED)
async def upload_program_cover(
    program_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    program = await get_program_and_check_existence(program_id, conn)

    if program['cover_url']:
        old_filename = os.path.basename(program['cover_url'])
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

    public_path = f'/graduate-program/uploads/{program_id}/{filename}'
    SCRIPT_SQL = """
        UPDATE graduate_program
        SET cover_url = %(public_path)s
        WHERE graduate_program_id = %(program_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'program_id': program_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/{program_id}/cover', status_code=HTTPStatus.OK)
async def delete_program_cover(program_id: str, conn: Conn):
    program = await get_program_and_check_existence(program_id, conn)

    if not program['cover_url']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de capa para excluir.',
        )

    filename = os.path.basename(program['cover_url'])
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE graduate_program
        SET cover_url = NULL
        WHERE graduate_program_id = %(program_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'program_id': program_id},
    )
    return {'message': 'Imagem de capa excluída com sucesso.'}
