from inspect import isawaitable

async def maybe_await(obj): return (await obj) if isawaitable(obj) else obj