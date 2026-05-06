from pathlib import Path
import logging

from config import load_config
from .score import run

import click

log = logging.getLogger("query")


@click.command()
@click.option("--config", "config", type=click.Path(exists=True, path_type=Path))
def main(config: Path) -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    log.info("Running scoring and ranking")
    config = load_config(config)
    run(config)


if __name__ == "__main__":
    main()
