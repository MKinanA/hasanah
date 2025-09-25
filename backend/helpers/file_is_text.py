from __future__ import annotations
from pathlib import Path
from ..helpers.log import log

def file_is_text(path: Path | str) -> bool:
    path = Path(path)
    is_text = True
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(64**2), b''):
            try: chunk.decode()
            except UnicodeDecodeError:
                is_text = False
                break
    return is_text

print(log(__name__, 'loaded')) # log