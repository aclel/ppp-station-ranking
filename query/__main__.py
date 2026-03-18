import argparse
import logging
import sys
from pathlib import Path

from .base import make_connection, write_month
from .postfit_residuals import build_residuals
from .ambiguity_resets import build_amb_resets
from .observations import build_observations
from .position import build_position

from utils import year_months

log = logging.getLogger("query")

BUILDERS = {
    "postfit_residuals": build_residuals,
    "amb_resets": build_amb_resets,
    "observations": build_observations,
    "position": build_position,
}


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="query")
    p.add_argument("family", choices=BUILDERS.keys())
    p.add_argument("start", help="YYYY-MM (inclusive)")
    p.add_argument("end", help="YYYY-MM (inclusive)")
    p.add_argument("--raw-root", type=Path, default=Path("/data/parquet"))
    p.add_argument("--out-root", type=Path, default=Path("cache/query"))
    p.add_argument("--skip-existing", action="store_true")
    return p.parse_args(argv)


def main(argv=None) -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    args = parse_args(argv)
    builder = BUILDERS[args.family]
    conn = make_connection()

    # Build the query cache for each month for the given family
    for year_month in year_months(args.start, args.end):
        out_path = args.out_root / args.family / f"{year_month}.parquet"
        if args.skip_existing and out_path.exists():
            log.info("skip %s (exists)", out_path)
            continue

        year, month = (int(x) for x in year_month.split("-"))
        df = builder(year, month, args.raw_root, conn)
        write_month(df, args.family, year_month, args.out_root)
        log.info("%s %s: %d rows", args.family, year_month, len(df))

    return 0


if __name__ == "__main__":
    sys.exit(main())
