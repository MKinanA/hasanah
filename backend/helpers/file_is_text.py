from __future__ import annotations
from pathlib import Path
from ..helpers.log import log

def file_is_text(path: Path | str) -> bool:
    if not (path := Path(path)).exists(): return False
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(64**2), b''):
            try: chunk.decode()
            except UnicodeDecodeError: return False
    return True