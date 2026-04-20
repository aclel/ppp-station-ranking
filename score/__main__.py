from pathlib import Path

from config import load_config
from .score import run

import click


@click.command()
@click.option("--config", "config", type=click.Path(exists=True, path_type=Path))
def main(config: Path) -> None:
    config = load_config(config)
    run(config)


if __name__ == "__main__":
    main()
