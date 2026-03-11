from typing import Literal
from dataclasses import dataclass

# USed to define whether a metric is better when it's higher or lower
Direction = Literal["min", "max"]


@dataclass(frozen=True)
class Metric:
    name: str
    units: str
    direction: Direction  # Is higher better?
    thresh_min: float | None = (
        None  # Drop anything less than this from dataset - for extreme outliers only
    )
    thresh_max: float | None = (
        None  # Drop anything more than this from the metric - for extreme outliers only
    )
    log_transform: bool = False  # Run log transform on a metric to fix skew (like ambiguity resets where most stations are good but some have lots)


METRICS: dict[str, Metric] = {
    m.name: m
    for m in (
        Metric(
            "phase_wrms", direction="min", units="mm", thresh_min=-10, thresh_max=10
        ),
        Metric(
            "code_wrms", direction="min", units="cm", thresh_min=-150, thresh_max=150
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
            thresh_min=0,
            thresh_max=11000,
            log_transform=True,
        ),
        Metric("cn0", direction="max", units="dB-Hz"),
        Metric("mp1", direction="min", units="m"),
        Metric("mp2", direction="min", units="m"),
    )
}


def thresholds(metric_name: str) -> tuple[float, float]:
    """Minimum and maximum thresholds for extreme value detection when querying."""
    m = METRICS[metric_name]
    return (
        m.thresh_min if m.thresh_min is not None else float("-inf"),
        m.thresh_max if m.thresh_max is not None else float("inf"),
    )
