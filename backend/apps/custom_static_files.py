from __future__ import annotations
from os import listdir
from fastapi.staticfiles import StaticFiles
from fastapi import Response
from starlette.background import BackgroundTask
from pathlib import Path
from random import choice as random
from ..helpers.custom_html_templating import custom_html_templating, file_is_templatable_html
from ..helpers.log import log

# CACHED_FILE_NAME_COMBINATION = 'abcdefghijklmnopqrstuvwxyz0123456789'
# CACHED_FILE_NAME_LENGTH = 16

# class CustomStaticFiles(StaticFiles):
#     def get_path(self, scope) -> str:
#         path = super().get_path(scope)
#         return path

#     async def get_response(self, path, scope) -> Response:
#         path = Path(path).resolve()
#         cached = False
#         if file_is_templatable_html(path):
#             with open(cache_path := Path(str(self.directory))/f'cache/{str().join(random(CACHED_FILE_NAME_COMBINATION) for _ in range(CACHED_FILE_NAME_LENGTH))}{path.suffix}', 'wt') as cache_file: cache_file.write(custom_html_templating(path.read_text()))
#             path = cache_path
#             cached = True
#         response = await super().get_response(str(path), scope)
#         if cached: response.background = BackgroundTask(lambda: path.unlink(True))
#         return response

CustomStaticFiles = StaticFiles

print(log(__name__, 'loaded')) # File load log