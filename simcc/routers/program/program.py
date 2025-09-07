from fastapi import APIRouter

from simcc.services import program_service

router = APIRouter(prefix='/graduate-program')


@router.post('/')
async def create_program():
    return await program_service.create_program(b)
