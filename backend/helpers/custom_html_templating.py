from __future__ import annotations
from pathlib import Path
from lxml import etree
from lxml.html import parse
from ..helpers.file_is_text import file_is_text
from ..helpers.log import log

FLAG = 'plis formatkan dulu le'
RECOGNIZED_HTML_EXTENSIONS = [
    'html',
]

def file_is_templatable_html(path: Path | str) -> bool:
    if not file_is_text(path := Path(path)): return False
    if not path.suffix[1:] in RECOGNIZED_HTML_EXTENSIONS: return False
    with open(path) as file:
        for line in file:
            if (line := ' '.join(line.split()).strip().lower()) != '': return FLAG in line
    return False

def custom_html_templating(path: Path | str) -> str:
    html = parse(path)

print(log(__name__, 'loaded')) # File load log