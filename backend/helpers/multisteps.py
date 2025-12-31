from typing import Callable
from .maybe_await import maybe_await

def multisteps(*callables: Callable):
    step = 0
    last_result = None
    for callable in callables: last_result = callable(last_result) if (step := step + 1) > 1 else callable()
    return last_result

async def multisteps_async(*callables: Callable):
    step = 0
    last_result = None
    for callable in callables: last_result = await maybe_await(callable(last_result) if (step := step + 1) > 1 else callable())
    return last_result