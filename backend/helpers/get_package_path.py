from pathlib import Path

def get_package_path(__name__: str, __file__: str) -> Path:
    path = Path(__file__)
    if __name__.count('.') > 0:
        for _ in range(__name__.count('.')): path = path.parent
    else: path = path.parent
    return path