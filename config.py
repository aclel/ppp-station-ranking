import yaml
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from metrics import METRICS


@dataclass(frozen=True)
class Variant:
    name: str
    aggregator: str  # How a score is built from the metrics (TOPSIS, weighted sum etc)


@dataclass(frozen=True)
class ScoreConfig:
    name: str
    output_dir: Path
    cache_dir: Path
    start_date: date
    end_date: date
    weights: dict[str, float]
    variants: tuple[Variant, ...]
    window_days: int | None = None
    peer_relative: bool = (
        True  # Metric minus network median to remove effects of PPP product improvement
    )


def _read_yaml(path) -> dict:
    with open(path, "r") as file:
        data = yaml.safe_load(file)

    return data


def _build_config(raw: dict, base_dir: Path) -> ScoreConfig:
    return ScoreConfig(
        name=raw["name"],
        output_dir=(base_dir / raw["output_dir"]).resolve(),
        cache_dir=Path(raw["cache_dir"]).resolve(),
        start_date=date.fromisoformat(raw["start_date"]),
        end_date=date.fromisoformat(raw["end_date"]),
        weights={name: float(w) for name, w in raw["weights"].items()},
        variants=tuple(Variant(**v) for v in raw["variants"]),
        window_days=int(raw["window_days"]) if raw["window_days"] else None,
        peer_relative=raw["peer_relative"],
    )


def _validate(config: ScoreConfig) -> None:
    errors: list[str] = []
    if config.start_date >= config.end_date:
        errors.append("start date is before end date")
    unknown = set(config.weights) - METRICS.keys()
    if unknown:
        errors.append(f"weights for unconfigured metrics: {unknown}")

    # TODO: Validate scoring variant names
    if errors:
        raise ValueError("invalid config:\n  - " + "\n  - ".join(errors))


def load_config(path: Path) -> ScoreConfig:
    """Parse a config file (typically stored in scenarios/), build, validate"""
    raw = _read_yaml(path)
    config = _build_config(raw, base_dir=path.parent)
    _validate(config)
    return config
