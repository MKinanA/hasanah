from fastapi import APIRouter

router = APIRouter()

@router.get('')
async def root(): return 'test endpoint'

@router.get('/error')
async def error(): raise Exception