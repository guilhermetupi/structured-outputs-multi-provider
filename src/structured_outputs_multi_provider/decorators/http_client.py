from typing import Callable

import httpx


def http_client(timeout: float | None = 10.0) -> Callable:
    def wrapper(func):
        async def main_wrapper(*args, **kwargs):
            async with httpx.AsyncClient(timeout=timeout) as client:
                return await func(args[0], client, *args[1:], **kwargs)

        return main_wrapper

    return wrapper
