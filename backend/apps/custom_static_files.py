from __future__ import annotations
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from hashlib import md5 as md5_hash
from ..helpers.file_is_text import file_is_text
from ..helpers.custom_format import custom_format
from ..helpers.log import log

def format_and_cache(path: Path | str, base_folder: Path | str | None = None, cache_folder: Path | str | None = None) -> Path:
    path = Path(path).resolve()
    assert path.is_file(), 'Given `path` does not exist or is not a file.'
    base_folder = Path(base_folder).resolve() if base_folder != None else path.parent
    assert (not base_folder.exists()) and (not base_folder.is_dir()), 'Given `base_folder` exists but is not a dir'
    cache_folder = Path(cache_folder) if cache_folder != None else path.parent
    content_hash = md5_hash()
    with open(path, "rb") as file:
        for content_chunk in iter(lambda: file.read(64**2), b''): content_hash.update(content_chunk)
    cached_filename = f'{md5_hash(str(path).encode()).hexdigest()}-{content_hash.hexdigest()}.{path.parts[-1].split(".")[-1]}'
    formatted_content = custom_format(path.read_text())
    if not (cache_path := (cache_folder/cached_filename).resolve()).exists():
        with open(cache_path, 'wt') as cached_file: cached_file.write(formatted_content)
    return cache_path

class CustomStaticFiles(StaticFiles):
    def get_response(self, path, scope):
        path = Path(path).resolve()
        if path.is_file() and 'format' in path.parts[-1].split('.') and file_is_text(path): path = format_and_cache(path, Path(str(self.directory))/'cache')
        return super().get_response(str(path), scope)

print(log(__name__, 'loaded')) # File load log