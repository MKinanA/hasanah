from fastapi import APIRouter, Request
from ...helpers.api_response import api_response as mkresp

router = APIRouter()

@router.post('/post')
async def body(request: Request): return mkresp('success', '', '', body=(await request.body()).decode())