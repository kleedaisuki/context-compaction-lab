"""Published engineering anchors, separate from unmeasured distribution assumptions.

The available case study reports medians, not raw recovery observations.
This profile represents a concentrated scenario anchored at those medians;
it does not estimate population means, variances, or an unidentified split.
"""

from .config import PositiveSpec, RecoverySpec, Workload

STUDY_URL = "https://langwatch.ai/research/finding-the-optimal-context-window"
"""Primary single-engineer Claude Code case study, accessed 2026-10-06."""


def engineering_workload(calls: int = 400) -> Workload:
    """Build a total-context, cold-reset scenario anchored to published medians.

    Example: ``simulate(engineering_workload(), 150_000, marks)``.
    The 61,206-token residual is constructed from two medians, not measured
    documents. Initial state represents a just-rebuilt cold context. Growth
    uses the study's high-context delta scale; its Gamma CV and all gap/output
    parameters remain synthetic controls. No rediscovery steps are added.
    """
    return Workload(
        calls=calls,
        initial_context=65_588,
        warm_start=False,
        growth=PositiveSpec("gamma", mean=1_470, cv=0.8),
        recovery=RecoverySpec(
            summary_base=4_382,
            documents=PositiveSpec("constant", mean=0),
            restored_input_tokens=65_588 - 4_382,
        ),
    )


def engineering_evidence() -> dict[str, object]:
    """Return provenance without misrepresenting scenario parameters as fitted data."""
    return {
        "source_url": STUDY_URL,
        "accessed": "2026-10-06",
        "population": "single engineer; Claude Code; 2451 sessions; 873 compactions",
        "published_anchors": {
            "post_compaction_full_input_median_tokens": 65_588,
            "generated_summary_median_tokens": 4_382,
            "growth_delta_scale_above_200k_tokens": 1_470,
            "growth_delta_scale_below_50k_tokens": 3_200,
        },
        "constructed_residual_tokens": 61_206,
        "residual_status": "difference_of_medians_not_median_of_difference_not_document_volume",
        "unidentified": ["system_tools", "preserved_history", "reread_documents", "warm_boundary"],
        "synthetic_controls": [
            "constant_recovery_at_median_anchors", "gamma_growth_cv_0.8",
            "independent_lognormal_gaps_mean_90s_cv_1.5", "output_fraction_0.25",
            "400_normal_calls_unless_overridden", "all_cold_recovery", "fixed_illustrative_prices",
        ],
        "scope": "conditional_expected_invoice_not_empirical_expected_invoice_or_task_utility",
    }
