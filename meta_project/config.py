import tomllib
from pathlib import Path


def load_config(config_file=None):
    if not config_file or not Path(config_file).exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    # Load the TOML configuration file
    with open(config_file, "rb") as f:
        return tomllib.load(f)