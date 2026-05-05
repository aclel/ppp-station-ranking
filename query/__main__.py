import argparse
import logging
import sys
from pathlib import Path

from .base import make_connection, write_month
from .builders import BUILDERS

from utils import year_months

log = logging.getLogger("query")


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="query")
    p.add_argument("family", choices=BUILDERS.keys())
    p.add_argument("start", help="YYYY-MM (inclusive)")
    p.add_argument("end", help="YYYY-MM (inclusive)")
    p.add_argument("--raw-root", type=Path, default=Path("/data/parquet"))
    p.add_argument("--out-root", type=Path, default=Path("cache/query"))
    p.add_argument("--skip-existing", action="store_true")
    p.add_argument("--threads", type=int, required=True, help="DuckDB thread count")
    p.add_argument(
        "--mem",
        default=None,
        required=True,
        help="DuckDB memory limit, e.g. '64GB'",
    )
    return p.parse_args(argv)


def main(argv=None) -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    args = parse_args(argv)
    import time

    builder = BUILDERS[args.family]

    conn = make_connection(memory_limit=args.mem, threads=args.threads)

    # Build the query cache for each month for the given family
    for year_month in year_months(args.start, args.end):
        out_path = args.out_root / args.family / f"{year_month}.parquet"
        if args.skip_existing and out_path.exists():
            log.info("skip %s (exists)", out_path)
            continue

        year, month = (int(x) for x in year_month.split("-"))
        t_build0 = time.perf_counter()
        df = builder(year, month, args.raw_root, conn)
        t_build1 = time.perf_counter()
        n = len(df)
        t_build2 = time.perf_counter()
        write_month(df, args.family, year_month, args.out_root)
        t_build3 = time.perf_counter()
        log.info(
            "%s %s: build=%.2fs mat=%.2fs write=%.2fs rows=%d",
            args.family,
            year_month,
            t_build1 - t_build0,
            t_build2 - t_build1,
            t_build3 - t_build2,
            n,
        )
        log.info("%s %s: %d rows", args.family, year_month, len(df))

    return 0


if __name__ == "__main__":
    sys.exit(main())
