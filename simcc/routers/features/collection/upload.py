import os
from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from simcc.core.connection import Connection
from simcc.core.database import get_conn

UPLOAD_DIR = 'simcc/storage/upload'

router = APIRouter(prefix='/collection/upload')

Conn = Annotated[Connection, Depends(get_conn)]


async def get_collection_and_check_existence(collection_id: str, conn: Conn):
    """
    Função utilitária para buscar a coleção e verificar sua existência.
    """
    SCRIPT_SELECT = """
        SELECT *
        FROM feature.collection
        WHERE collection_id = %(collection_id)s
    """
    collection = await conn.select(
        SCRIPT_SELECT, params={'collection_id': collection_id}, one=True
    )
    if not collection:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Coleção não encontrada.',
        )
    return collection


@router.post('/{collection_id}/cover', status_code=HTTPStatus.CREATED)
async def upload_collection_cover(
    collection_id: str,
    conn: Conn,
    file: UploadFile = File(...),
):
    """
    Faz o upload da imagem de capa de uma coleção.
    """
    collection = await get_collection_and_check_existence(collection_id, conn)

    if collection['cover_url']:
        old_filename = os.path.basename(collection['cover_url'])
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

    public_path = f'/collection/uploads/{collection_id}/{filename}'
    SCRIPT_SQL = """
        UPDATE feature.collection
        SET cover_url = %(public_path)s
        WHERE collection_id = %(collection_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'public_path': public_path, 'collection_id': collection_id},
    )
    return {'filename': file.filename, 'path': public_path}


@router.delete('/{collection_id}/cover', status_code=HTTPStatus.OK)
async def delete_collection_cover(collection_id: str, conn: Conn):
    """
    Deleta a imagem de capa de uma coleção.
    """
    collection = await get_collection_and_check_existence(collection_id, conn)

    if not collection['cover_url']:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Nenhuma imagem de capa para excluir.',
        )

    filename = os.path.basename(collection['cover_url'])
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f'Erro ao deletar o arquivo {file_path}: {e}')

    SCRIPT_SQL = """
        UPDATE feature.collection
        SET cover_url = NULL
        WHERE collection_id = %(collection_id)s
    """
    await conn.exec(
        SCRIPT_SQL,
        params={'collection_id': collection_id},
    )
    return {'message': 'Imagem de capa excluída com sucesso.'}
