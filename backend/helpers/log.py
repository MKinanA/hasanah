from __future__ import annotations
from datetime import datetime
from colorama import Fore, Back, Style
# This `log.py` file MUST NOT import any other helpers or files as they all import this file

strftime = '%Y-%m-%d %H:%M:%S:%f'
level_colors = {
    'DEBUG': Fore.RESET + Back.RESET,
    'INFO': Fore.GREEN + Back.RESET,
    'WARNING': Fore.YELLOW + Back.RESET,
    'ERROR': Fore.RED + Back.RESET,
    'CRITICAL': Fore.RESET + Back.RED,
}
default_level = 'INFO'
prefix = ''
suffix = '.'
nothing = ''

def log(name: str, message: str, level: str = default_level, level_color: str | None = None) -> str: return f'{Style.RESET_ALL + Style.DIM + datetime.now().strftime(strftime) + Style.RESET_ALL} [{Fore.BLUE + Style.BRIGHT + name + Style.RESET_ALL}] [{Style.BRIGHT + (level_colors[level_color.upper() if level_color != None and level_color.upper() in level_colors else level.upper() if level.upper() in level_colors else default_level]) + level + Style.RESET_ALL}] {((message[0].upper() + message[1:]) if len(message) > 0 else message) + (suffix if not message.endswith(suffix) else nothing)}'

print(log(__name__, 'loaded')) # log