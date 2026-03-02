from . import apps, models, seeders, helpers, run_schema_and_seed, senders

def load_env():
    from dotenv import load_dotenv as env
    from .helpers.get_package_path import get_package_path
    return env(get_package_path(__name__, __file__)/'.env')