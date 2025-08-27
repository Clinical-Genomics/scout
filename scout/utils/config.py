import pathlib

DEFAULT_CONFIG = {
    "MONGO_DBNAME": "scout",
}


def load_config(cli_options=None, cli_config=None, flask_conf=None) -> dict:
    """Merge CLI options, YAML config, Flask config file, and defaults into one dict."""
    config = DEFAULTS.copy()

    # 1. CLI options (highest priority)
    if cli_options:
        config.update({k.upper(): v for k, v in cli_options.items() if v is not None})

    # 2. YAML config (deprecated, but still supported for backward compatibility)
    if cli_config:
        config.update({k.upper(): v for k, v in cli_config.items() if v is not None})

    # 3. Flask config file (.py with uppercase vars)
    if flask_conf:
        flask_conf_path = pathlib.Path(flask_conf).absolute()
        flask_conf_dict = {}
        with open(flask_conf_path) as f:
            code = compile(f.read(), str(flask_conf_path), "exec")
            exec(code, flask_conf_dict)
        flask_conf_dict = {k: v for k, v in flask_conf_dict.items() if k.isupper()}
        config.update(flask_conf_dict)

    return config
