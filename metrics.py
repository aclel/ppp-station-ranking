from typing import Literal
from dataclasses import dataclass

# USed to define whether a metric is better when it's higher or lower
Direction = Literal["min", "max"]


@dataclass(frozen=True)
class Metric:
    name: str
    units: str
    direction: Direction  # Is higher better?
    extreme_min: float | None = (
        None  # Drop anything less than this from dataset - for extreme outliers only
    )
    extreme_max: float | None = (
        None  # Drop anything more than this from the metric - for extreme outliers only
    )
    log_transform: bool = False  # Run log transform on a metric to fix skew (like ambiguity resets where most stations are good but some have lots)


METRICS: dict[str, Metric] = {
    m.name: m
    for m in (
        Metric(
            "phase_wrms", direction="min", units="mm", extreme_min=-100, extreme_max=100
        ),
        Metric(
            "code_wrms", direction="min", units="cm", extreme_min=-500, extreme_max=500
        ),
        Metric("h_conv", direction="min", units="min"),
        Metric("v_conv", direction="min", units="min"),
        Metric("uptime", direction="max", units="%"),
        Metric("active_uptime", direction="max", units="%"),
        Metric("outage_gaps", direction="min", units="count"),
        Metric(
            "amb_resets",
            direction="min",
            units="count per day",
            extreme_min=0,
            extreme_max=20000,
            log_transform=True,
        ),
        Metric("cn0", direction="max", units="dB-Hz"),
        Metric("mp1", direction="min", units="m"),
        Metric("mp2", direction="min", units="m"),
    )
}


def extremes(metric_name: str) -> tuple[float, float]:
    """Minimum and maximum thresholds for extreme value detection when querying."""
    m = METRICS[metric_name]
    return (
        m.extreme_min if m.extreme_min is not None else float("-inf"),
        m.extreme_max if m.extreme_max is not None else float("inf"),
    )
