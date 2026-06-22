from typing import List
from feedpulse.schemas.models import EvalCase, UrgencyLevel

BENCHMARK_CASES: List[EvalCase] = [
    EvalCase(
        case_id="EVAL-001",
        query="Apple M2 Mac canvas WebGL context lost crashes and black screen",
        expected_theme="WebGL Canvas Metal Backend Crashes",
        expected_item_ids=["FB-1001", "FB-1002", "FB-1003", "FB-1004", "FB-1005", "FB-1006"],
        ground_truth_summary="WebGL context lost error and black screen crash on Apple Silicon M-series MacBooks during high-DPI canvas zooming.",
        ground_truth_urgency=UrgencyLevel.CRITICAL
    ),
    EvalCase(
        case_id="EVAL-002",
        query="Okta SAML 2.0 infinite redirect loop locked out enterprise login",
        expected_theme="SAML 2.0 / Okta SSO Infinite Redirect Loops",
        expected_item_ids=["FB-2001", "FB-2002", "FB-2003", "FB-2004", "FB-2005"],
        ground_truth_summary="Endless HTTP 302 redirect loop between auth endpoint and IdP locking out enterprise accounts on Okta and Azure AD.",
        ground_truth_urgency=UrgencyLevel.CRITICAL
    ),
    EvalCase(
        case_id="EVAL-003",
        query="Markdown export deletes LaTeX KaTeX math equations formulas",
        expected_theme="Markdown Exporter Stripping Math Equations",
        expected_item_ids=["FB-3001", "FB-3002", "FB-3003", "FB-3004", "FB-3005"],
        ground_truth_summary="Markdown file download erases inline and display KaTeX math equations due to regex delimiter unescaping.",
        ground_truth_urgency=UrgencyLevel.MEDIUM
    ),
    EvalCase(
        case_id="EVAL-004",
        query="Stripe duplicate billing currency conversion EUR USD",
        expected_theme="Multi-Currency Stripe Billing & Duplicate Invoices",
        expected_item_ids=["FB-4001", "FB-4002", "FB-4003", "FB-4004"],
        ground_truth_summary="Double charging and currency conversion mismatches on annual renewal invoices for European customers.",
        ground_truth_urgency=UrgencyLevel.HIGH
    ),
    EvalCase(
        case_id="EVAL-005",
        query="iOS mobile app battery drain background offline sync hot CPU",
        expected_theme="Mobile Background Sync CPU & Battery Drain",
        expected_item_ids=["FB-5001", "FB-5002", "FB-5003", "FB-5004"],
        ground_truth_summary="High CPU usage and 35% battery depletion caused by SQLite thread lock contention during background offline document sync.",
        ground_truth_urgency=UrgencyLevel.HIGH
    ),
    EvalCase(
        case_id="EVAL-006",
        query="Realtime multiplayer cursor jitter 50 users lag workshop",
        expected_theme="Multiplayer Canvas Cursor Jitter & Latency",
        expected_item_ids=["FB-6001", "FB-6002", "FB-6003", "FB-6004"],
        ground_truth_summary="Erratic cursor jitter and dropped WebSocket frames during multi-user sessions exceeding 30 participants.",
        ground_truth_urgency=UrgencyLevel.HIGH
    )
]
