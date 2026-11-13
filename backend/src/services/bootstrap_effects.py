"""Pairwise win fractions (ties half-weighted) and a family-wise bootstrap interval.

Groups are resampled independently with replacement, each draw keeping the original
within-group sample size. One shared draw (the same bootstrap replicate index set)
covers every pair, so the replicate-level contrasts stay coupled. In each replicate we
take the largest absolute deviation of any pair's resampled win fraction from its
frozen estimate; the (1-alpha) quantile of that family-wide maximum is a single
simultaneous radius. This unstudentized max-deviation interval stays calibrated on
coarse, heavily tied ordinal grids where a studentized percentile-t interval is
unstable, and it needs no special case for pairs whose bootstrap standard error is
zero. The RNG seed and the number of replicates are frozen with the run; identical
inputs reproduce identical output.
"""
import math
from itertools import combinations
import numpy as np

DEFAULT_SEED = 20261113
DEFAULT_REPLICATES = 9999
MAX_REPLICATES = 100000

# np.quantile default: linear interpolation between adjacent order statistics.
_QUANTILE_METHOD = 'linear'
_METHOD_FAMILY = 'bootstrap-family-max-deviation-percentile'
_METHOD_DEGENERATE = 'point-estimate-degenerate-no-variation'


def win_fraction_matrix(values):
    """P(X_i > X_j) + 0.5 P(X_i = X_j) for every ordered group pair (row wins)."""
    k = len(values)
    mat = np.zeros((k, k), dtype=float)
    for i, j in combinations(range(k), 2):
        a = np.asarray(values[i], dtype=float)
        b = np.asarray(values[j], dtype=float)
        diff = a[:, None] - b[None, :]
        wins = float((diff > 0).sum())
        ties = float((diff == 0).sum())
        w = (wins + 0.5 * ties) / (a.size * b.size)
        mat[i, j] = w
        mat[j, i] = 1.0 - w
    return mat


def _grade_counts(a):
    """Counts over the validated 1-9 ordinal grid; index 0 holds grade 1."""
    return np.bincount(np.asarray(a, dtype=np.int64).ravel() - 1, minlength=9)


def _win_from_counts(ca, cb):
    """Exact win fraction from two 1-9 grade count vectors (ties half-weighted)."""
    cb_less = np.concatenate(([0], np.cumsum(cb)[:-1]))  # b observations below each grade
    wins = float((ca * cb_less).sum())
    ties = float((ca * cb).sum())
    return (wins + 0.5 * ties) / (float(ca.sum()) * float(cb.sum()))


def winner_bootstrap(groups, alpha, seed, replicates):
    """Simultaneous family-wise bootstrap intervals for pairwise winner fractions.

    Returns one row per pair with the frozen win fraction, its bootstrap standard
    error (descriptive), and a shared-radius interval. Degenerate families with no
    resampling variation collapse to the point estimate and are flagged.
    """
    if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed <= 2 ** 32 - 1:
        raise ValueError('bootstrap种子须为0–2^32-1的整数')
    if not isinstance(replicates, int) or isinstance(replicates, bool) or not 100 <= replicates <= MAX_REPLICATES:
        raise ValueError(f'bootstrap次数须为100–{MAX_REPLICATES}的整数')
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError('alpha须在0与1之间')
    arrays = [np.asarray(g, dtype=float) for g in groups]
    k = len(arrays)
    pairs = list(combinations(range(k), 2))
    base_counts = [_grade_counts(a) for a in arrays]
    # The count-based form is algebraically identical to the explicit pairwise
    # win_fraction_matrix (verified in tests); using it keeps the frozen estimate and
    # every bootstrap replicate on one statistic.
    theta = np.array([_win_from_counts(base_counts[i], base_counts[j]) for i, j in pairs], dtype=float)

    rng = np.random.default_rng(seed)
    m = len(pairs)
    boot = np.zeros((replicates, m), dtype=float)
    # Group-level resampling: every group is redrawn within each replicate, keeping
    # its original n. The replicate index is shared across all pairs in that column set.
    # Win fractions are aggregated on the fixed 1-9 grade counts, which is algebraically
    # identical to the pairwise comparison but independent of group sizes.
    for b in range(replicates):
        draw_counts = []
        for a in arrays:
            draw_counts.append(_grade_counts(a[rng.integers(0, a.size, size=a.size)]))
        boot[b, :] = [_win_from_counts(draw_counts[i], draw_counts[j]) for i, j in pairs]

    se = boot.std(axis=0, ddof=1)
    deviations = np.abs(boot - theta[None, :])
    family_max = deviations.max(axis=1)
    varying = int(np.count_nonzero(family_max > 0.0))
    degenerate = varying == 0

    rows = []
    if degenerate:
        radius = 0.0
        method = _METHOD_DEGENERATE
        critical = None
    else:
        critical = float(np.quantile(family_max, 1 - alpha, method=_QUANTILE_METHOD))
        radius = critical
        method = _METHOD_FAMILY
    for idx, (i, j) in enumerate(pairs):
        est = float(theta[idx])
        lo = max(0.0, est - radius)
        hi = min(1.0, est + radius)
        below = int((boot[:, idx] < 0.5).sum())
        equal = int((boot[:, idx] == 0.5).sum())
        above = int((boot[:, idx] > 0.5).sum())
        rows.append({
            'i': i,
            'j': j,
            'pair': f'{i}:{j}',
            'win_fraction': est,
            'bootstrap_se': float(se[idx]),
            'ci_lower': float(lo),
            'ci_upper': float(hi),
            'ci_covers_half': lo <= 0.5 <= hi,
            'interval_method': method,
            'replicates_below_half': below,
            'replicates_equal_half': equal,
            'replicates_above_half': above,
        })

    return {
        'effect': 'pairwise win fraction P(left>right)+0.5P(left=right); ties half-weighted',
        'parameterization': 'left group win fraction; complement 1-w reverses the direction',
        'seed': seed,
        'replicates': replicates,
        'family_alpha': alpha,
        'family_size': m,
        'resampling': ('group-level nonparametric bootstrap; resample each group with replacement '
                       'preserving its n; one shared replicate index set across all pairs'),
        'interval_construction': ('per replicate take max over pairs of |bootstrap win fraction - frozen '
                                  'estimate|; the (1-alpha) linear-interpolated quantile is one radius '
                                  'shared by every pair, clipped to [0,1]'),
        'quantile_method': _QUANTILE_METHOD,
        'family_critical_radius': critical,
        'zero_se_pairs': [rows[idx]['pair'] for idx in range(m) if se[idx] <= 0.0],
        'degenerate': degenerate,
        'replicates_with_family_variation': varying,
        'pairs': rows,
        'method_note': ('unstudentized family-wise max-deviation percentile interval; chosen because the '
                        '1-9 ordinal grid and heavy ties make studentized percentile-t intervals unstable. '
                        'Coverage is an approximate finite-sample simultaneous guarantee, not exact; the '
                        'discrete grid makes endpoints coarse and clipping to [0,1] can shorten intervals. '
                        'When resampling shows no variation the interval collapses to the frozen point '
                        'estimate, which means the data carry no observable bootstrap variation, not that '
                        'the groups are equal.'),
    }
