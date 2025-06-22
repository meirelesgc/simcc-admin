from http import HTTPStatus

from fastapi import HTTPException

ForbiddenException = HTTPException(
    status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
)
