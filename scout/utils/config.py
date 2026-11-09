import pathlib

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


DEFAULT_CONFIG_PATH = pathlib.Path(__file__).parent.parent / "server" / "config.toml"


def load_config(config_file=None, cli_options=None) -> dict:
    """Load defaults, an optional TOML config file, and CLI options in priority order."""
    with DEFAULT_CONFIG_PATH.open("rb") as config_handle:
        config = tomllib.load(config_handle)

    if config_file:
        config_path = pathlib.Path(config_file).absolute()
        with config_path.open("rb") as config_handle:
            config.update(tomllib.load(config_handle))

    if cli_options:
        config.update({k.upper(): v for k, v in cli_options.items() if v is not None})

    return config
