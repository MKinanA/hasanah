from fastapi import Request
from ..models.user import User

async def auth(request: Request) -> 'User | None': return await User.get_by_session_auth(token) if type(token := (await request.json()).get('token')) == str else None