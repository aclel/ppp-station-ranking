from functools import partial

from .base import build_df
from .postfit_residuals import (
    PATTERN as RESIDUALS_PATTERN,
    residuals_sql,
    empty_frame as _residuals_empty,
)
from .ambiguity_resets import (
    PATTERN as AMB_PATTERN,
    amb_resets_sql,
    amb_resets_no_kf_sql,
    empty_frame as _amb_empty,
)
from .observations import (
    PATTERN as OBS_PATTERN,
    observations_sql,
    empty_frame as _obs_empty,
)
from .position import (
    PATTERN as POS_PATTERN,
    position_sql,
    empty_frame as _pos_empty,
)
from .linear_combinations import (
    PATTERN as LC_PATTERN,
    linear_combinations_sql,
    empty_frame as _lc_empty,
)
from .satellite_gaps import (
    PATTERN as GAPS_PATTERN,
    satellite_gaps_sql,
    empty_frame as _gaps_empty,
)

BUILDERS = {
    "postfit_residuals": partial(
        build_df, residuals_sql, RESIDUALS_PATTERN, _residuals_empty
    ),
    "amb_resets": partial(build_df, amb_resets_sql, AMB_PATTERN, _amb_empty),
    "amb_resets_no_kf": partial(
        build_df, amb_resets_no_kf_sql, AMB_PATTERN, _amb_empty
    ),
    "observations": partial(build_df, observations_sql, OBS_PATTERN, _obs_empty),
    "position": partial(build_df, position_sql, POS_PATTERN, _pos_empty),
    "linear_combinations": partial(
        build_df, linear_combinations_sql, LC_PATTERN, _lc_empty
    ),
    "satellite_gaps": partial(build_df, satellite_gaps_sql, GAPS_PATTERN, _gaps_empty),
}
