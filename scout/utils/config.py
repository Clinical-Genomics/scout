import copy
import importlib.util
import pathlib

DEFAULT_CONFIG = {
    "MONGO_DBNAME": "scout",
}


def load_config(cli_options=None, cli_config=None, flask_conf=None) -> dict:
    """Merge CLI options, YAML config, Flask config file, and defaults into one dict.

    Priority (lowest → highest):
        1. Defaults
        2. Flask config file
        3. YAML config (deprecated but supported)
        4. CLI options
    """
    # 1. Defaults
    config = copy.deepcopy(DEFAULT_CONFIG)

    # 2. Flask config file (.py with uppercase vars)
    if flask_conf:
        flask_conf_path = pathlib.Path(flask_conf).absolute()
        spec = importlib.util.spec_from_file_location("flask_conf", flask_conf_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        flask_conf_dict = {k: getattr(module, k) for k in dir(module) if k.isupper()}
        config.update(flask_conf_dict)

    # 3. YAML config (deprecated, but still supported)
    if cli_config:
        config.update({k.upper(): v for k, v in cli_config.items() if v is not None})

    # 4. CLI options (highest priority)
    if cli_options:
        config.update({k.upper(): v for k, v in cli_options.items() if v is not None})

    return config
