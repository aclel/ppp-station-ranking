from typing import Literal
from dataclasses import dataclass

# USed to define whether a metric is better when it's higher or lower
Direction = Literal["min", "max"]


@dataclass(frozen=True)
class Metric:
    name: str
    units: str
    direction: Direction
    thresh_min: float | None = None
    thresh_max: float | None = None


METRICS: dict[str, Metric] = {
    m.name: m
    for m in (
        Metric(
            "phase_wrms", direction="min", units="mm", thresh_min=-50, thresh_max=50
        ),
        Metric("code_wrms", direction="min", units="cm", thresh_min=-1000, thresh_max=1000),
        Metric("h_conv", direction="min", units="min"),
        Metric("v_conv", direction="min", units="min"),
        Metric("uptime", direction="max", units="%"),
        Metric("active_uptime", direction="max", units="%"),
        Metric("outage_gaps", direction="min", units="count"),
        Metric("amb_resets", direction="min", units="count per day"),
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
