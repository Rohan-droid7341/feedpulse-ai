import json
from pathlib import Path
from typing import List
from feedpulse.schemas.models import FeedbackItem, FeedbackSource, UrgencyLevel, SentimentType

DATASET = [
    # Theme 1: WebGL Canvas Crashes on M-Series MacBooks (Critical)
    {
        "id": "FB-1001",
        "text": "The design canvas completely crashes and goes pitch black whenever I zoom into a complex vector layout on my M2 MacBook Pro. WebGL context lost error in DevTools.",
        "source": "discord",
        "author": "sarah_designer@creative.io",
        "urgency": "critical",
        "sentiment": "negative",
        "sentiment_score": -0.88,
        "product_area": "Canvas",
        "timestamp": "2026-06-01T09:14:22Z",
        "metadata": {"os": "macOS 14.5", "chip": "Apple M2", "browser": "Chrome 125"}
    },
    {
        "id": "FB-1002",
        "text": "Major issue in production: our entire design team on Apple Silicon Macs is seeing repeated canvas freezes on multi-layer SVG artboards. Chrome tab consumes 4GB RAM then crashes.",
        "source": "zendesk",
        "author": "enterprise_admin@acme-design.com",
        "urgency": "critical",
        "sentiment": "negative",
        "sentiment_score": -0.92,
        "product_area": "Canvas",
        "timestamp": "2026-06-02T11:20:05Z",
        "metadata": {"ticket_id": "ZEN-8841", "tier": "Enterprise", "affected_seats": 42}
    },
    {
        "id": "FB-1003",
        "text": "1 star review: Canvas freezes constantly when rendering paths with custom clipping masks on Safari M3 Max. Unusable for professional graphics work right now.",
        "source": "app_store",
        "author": "PixelArtist_99",
        "urgency": "critical",
        "sentiment": "negative",
        "sentiment_score": -0.85,
        "product_area": "Canvas",
        "timestamp": "2026-06-03T14:45:19Z",
        "metadata": {"rating": 1, "app_version": "3.4.1"}
    },
    {
        "id": "FB-1004",
        "text": "Crash report: WebGL2 context loss on Metal backend during offscreen canvas buffer blit with high DPI display scaling (Retina 2x).",
        "source": "github",
        "author": "webgl-dev-contrib",
        "urgency": "critical",
        "sentiment": "negative",
        "sentiment_score": -0.76,
        "product_area": "Canvas",
        "timestamp": "2026-06-04T08:33:10Z",
        "metadata": {"issue_number": 1420, "label": "bug:rendering"}
    },
    {
        "id": "FB-1005",
        "text": "Is anyone else getting 'Canvas WebGL Context Discarded' error on Mac when switching between window tabs? Happens every 15 minutes.",
        "source": "discord",
        "author": "kevin_ui",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.71,
        "product_area": "Canvas",
        "timestamp": "2026-06-05T16:12:00Z",
        "metadata": {"channel": "#general-help"}
    },
    {
        "id": "FB-1006",
        "text": "Customer survey feedback: We love the pen tool, but the graphics engine black screen crash on macOS is forcing us to pause our enterprise rollout.",
        "source": "customer_survey",
        "author": "vp_product@fintechcorp.com",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.68,
        "product_area": "Canvas",
        "timestamp": "2026-06-06T10:05:44Z",
        "metadata": {"nps_score": 3, "account_value": "$60k ARR"}
    },

    # Theme 2: SAML 2.0 / Okta SSO Infinite Redirect Loop (Critical)
    {
        "id": "FB-2001",
        "text": "CRITICAL: Our entire company is locked out this morning. Logging in via Okta SAML triggers an endless redirect loop between auth.app.com and our identity provider.",
        "source": "zendesk",
        "author": "it_sec@globalfin.org",
        "urgency": "critical",
        "sentiment": "negative",
        "sentiment_score": -0.95,
        "product_area": "Authentication",
        "timestamp": "2026-06-07T08:02:11Z",
        "metadata": {"ticket_id": "ZEN-8912", "tier": "Enterprise", "blocked_users": 1200}
    },
    {
        "id": "FB-2002",
        "text": "Urgent auth regression: SAML ACS endpoint returns HTTP 302 without setting the session cookie when RelayState contains special characters.",
        "source": "github",
        "author": "devops_saml_lead",
        "urgency": "critical",
        "sentiment": "negative",
        "sentiment_score": -0.89,
        "product_area": "Authentication",
        "timestamp": "2026-06-07T09:40:55Z",
        "metadata": {"issue_number": 1428, "label": "security:auth"}
    },
    {
        "id": "FB-2003",
        "text": "We cannot sign in through Microsoft Entra ID (Azure AD). It loops back to the login screen 5 times then displays 'Authentication Timeout'.",
        "source": "zendesk",
        "author": "sysadmin@enterprisecloud.net",
        "urgency": "critical",
        "sentiment": "negative",
        "sentiment_score": -0.91,
        "product_area": "Authentication",
        "timestamp": "2026-06-08T07:15:20Z",
        "metadata": {"ticket_id": "ZEN-8920", "idp": "AzureAD"}
    },
    {
        "id": "FB-2004",
        "text": "G2 Review: Great product once inside, but their enterprise SSO broke twice this month, leaving our operations team blocked for hours.",
        "source": "g2_reviews",
        "author": "Verified IT Director",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.65,
        "product_area": "Authentication",
        "timestamp": "2026-06-09T13:22:15Z",
        "metadata": {"rating": 2, "company_size": "500-1000 employees"}
    },
    {
        "id": "FB-2005",
        "text": "Anyone know why the new SAML metadata cert update is rejecting SHA-256 signatures from PingFederate? Getting stuck on callback URL.",
        "source": "discord",
        "author": "cyber_matt",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.60,
        "product_area": "Authentication",
        "timestamp": "2026-06-10T15:50:30Z",
        "metadata": {"channel": "#enterprise-support"}
    },

    # Theme 3: Markdown Export Strips KaTeX Math Formulas (Medium)
    {
        "id": "FB-3001",
        "text": "When exporting research notebooks to standard Markdown (.md), all inline and block KaTeX math formulas are completely erased instead of preserved.",
        "source": "github",
        "author": "dr_physics_researcher",
        "urgency": "medium",
        "sentiment": "negative",
        "sentiment_score": -0.55,
        "product_area": "Export",
        "timestamp": "2026-06-11T12:00:10Z",
        "metadata": {"issue_number": 1435, "label": "export:markdown"}
    },
    {
        "id": "FB-3002",
        "text": "LaTeX equations disappear during markdown download. The document just shows empty spaces where math formulas like integrals and matrices were rendered.",
        "source": "discord",
        "author": "alicia_academic",
        "urgency": "medium",
        "sentiment": "negative",
        "sentiment_score": -0.52,
        "product_area": "Export",
        "timestamp": "2026-06-12T14:30:22Z",
        "metadata": {"channel": "#feature-requests"}
    },
    {
        "id": "FB-3003",
        "text": "Feature bug: Markdown exporter parser regex fails to escape dollar sign delimiters ($...$), stripping KaTeX blocks upon serialization.",
        "source": "github",
        "author": "markdown-ast-wizard",
        "urgency": "medium",
        "sentiment": "negative",
        "sentiment_score": -0.48,
        "product_area": "Export",
        "timestamp": "2026-06-13T16:10:04Z",
        "metadata": {"pull_request_suggestion": True}
    },
    {
        "id": "FB-3004",
        "text": "Our university STEM students are frustrated because exporting homework solutions to markdown deletes all mathematical equations.",
        "source": "zendesk",
        "author": "prof_hansen@stateuniversity.edu",
        "urgency": "medium",
        "sentiment": "negative",
        "sentiment_score": -0.58,
        "product_area": "Export",
        "timestamp": "2026-06-14T09:20:45Z",
        "metadata": {"ticket_id": "ZEN-8955", "tier": "Education"}
    },
    {
        "id": "FB-3005",
        "text": "Please fix math export! PDF export works fine, but GitHub-flavored markdown export removes all KaTeX formulas completely.",
        "source": "discord",
        "author": "math_ninja",
        "urgency": "low",
        "sentiment": "neutral",
        "sentiment_score": -0.25,
        "product_area": "Export",
        "timestamp": "2026-06-15T18:05:12Z",
        "metadata": {"channel": "#community-feedback"}
    },

    # Theme 4: Billing Currency Conversion & Duplicate Invoicing (High)
    {
        "id": "FB-4001",
        "text": "We were billed $2,400 USD instead of our contracted €2,200 EUR on annual renewal, and Stripe charged our corporate card twice.",
        "source": "zendesk",
        "author": "cfo_office@berlin-tech.de",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.84,
        "product_area": "Billing",
        "timestamp": "2026-06-16T11:15:33Z",
        "metadata": {"ticket_id": "ZEN-8980", "amount_disputed": "$4,800"}
    },
    {
        "id": "FB-4002",
        "text": "Invoice PDF shows wrong currency symbol. It printed Japanese Yen symbol (¥) for a British Pound (£) corporate subscription.",
        "source": "zendesk",
        "author": "finance_dept@londontrade.co.uk",
        "urgency": "medium",
        "sentiment": "negative",
        "sentiment_score": -0.62,
        "product_area": "Billing",
        "timestamp": "2026-06-17T13:40:02Z",
        "metadata": {"ticket_id": "ZEN-8989", "tier": "Business"}
    },
    {
        "id": "FB-4003",
        "text": "G2 Review: Pricing is fair, but their billing engine has currency conversion glitches that took 3 weeks of support back-and-forth to refund.",
        "source": "g2_reviews",
        "author": "FinOps Manager",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.73,
        "product_area": "Billing",
        "timestamp": "2026-06-18T15:02:18Z",
        "metadata": {"rating": 3, "disputed": True}
    },
    {
        "id": "FB-4004",
        "text": "Annual plan billing webhook fired duplicate charge events for multi-currency customers in Europe and Asia-Pacific regions.",
        "source": "github",
        "author": "stripe-webhook-guard",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.79,
        "product_area": "Billing",
        "timestamp": "2026-06-19T08:12:40Z",
        "metadata": {"issue_number": 1442, "label": "billing:stripe"}
    },

    # Theme 5: Mobile App Severe Battery Drain During Offline Sync (High)
    {
        "id": "FB-5001",
        "text": "App Store Review: The latest iOS update drains 35% battery in under 40 minutes because offline sync background worker never goes to sleep.",
        "source": "app_store",
        "author": "TravelerTechGuy",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.86,
        "product_area": "Mobile",
        "timestamp": "2026-06-20T10:14:55Z",
        "metadata": {"rating": 1, "device": "iPhone 15 Pro", "app_version": "2.8.0"}
    },
    {
        "id": "FB-5002",
        "text": "My phone gets uncomfortably hot whenever the mobile app syncs offline cached documents in the background. High CPU usage pegging all cores.",
        "source": "discord",
        "author": "ios_power_user",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.80,
        "product_area": "Mobile",
        "timestamp": "2026-06-21T12:45:00Z",
        "metadata": {"channel": "#mobile-app"}
    },
    {
        "id": "FB-5003",
        "text": "Android battery telemetry shows continuous SQLite database lock contention inside the background synchronization WorkManager service.",
        "source": "github",
        "author": "android_perf_engineer",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.74,
        "product_area": "Mobile",
        "timestamp": "2026-06-21T16:30:15Z",
        "metadata": {"issue_number": 1450, "label": "mobile:perf"}
    },
    {
        "id": "FB-5004",
        "text": "Customer survey: I had to delete the mobile app while traveling because it drained my battery down to 5% before lunch.",
        "source": "customer_survey",
        "author": "field_sales_rep@enterprises.com",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.82,
        "product_area": "Mobile",
        "timestamp": "2026-06-22T09:05:11Z",
        "metadata": {"nps_score": 2}
    },

    # Theme 6: Real-time Multi-User Collaboration Cursor Jitter (High)
    {
        "id": "FB-6001",
        "text": "When more than 30 team members join a live canvas workshop, the multiplayer cursor positions jitter erratically and lag by 2.5 seconds.",
        "source": "zendesk",
        "author": "workshop_lead@designspring.co",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.70,
        "product_area": "Collaboration",
        "timestamp": "2026-06-23T14:10:05Z",
        "metadata": {"ticket_id": "ZEN-9012", "concurrent_users": 45}
    },
    {
        "id": "FB-6002",
        "text": "WebSocket server drops broadcast frames when room occupancy exceeds 50 sockets, causing local CRDT state desyncs.",
        "source": "github",
        "author": "crdt-systems-hacker",
        "urgency": "high",
        "sentiment": "negative",
        "sentiment_score": -0.75,
        "product_area": "Collaboration",
        "timestamp": "2026-06-23T18:22:30Z",
        "metadata": {"issue_number": 1461, "label": "backend:realtime"}
    },
    {
        "id": "FB-6003",
        "text": "Our remote brainstorming session was chaotic today. Cursors were jumping across the screen and text entered by one person overwrote another.",
        "source": "discord",
        "author": "agile_coach_dan",
        "urgency": "medium",
        "sentiment": "negative",
        "sentiment_score": -0.65,
        "product_area": "Collaboration",
        "timestamp": "2026-06-24T10:15:42Z",
        "metadata": {"channel": "#user-lounge"}
    },
    {
        "id": "FB-6004",
        "text": "Collaboration is silky smooth with 5 users, but scales poorly during large all-hands product design sprints.",
        "source": "customer_survey",
        "author": "head_of_ux@saasco.io",
        "urgency": "medium",
        "sentiment": "neutral",
        "sentiment_score": -0.20,
        "product_area": "Collaboration",
        "timestamp": "2026-06-24T15:40:00Z",
        "metadata": {"nps_score": 6}
    },

    # Theme 7: Search Index Stale for Newly Created Workspace Documents (Medium)
    {
        "id": "FB-7001",
        "text": "Newly created workspace pages take over 45 minutes to appear in search results. Team members assume documents are lost.",
        "source": "zendesk",
        "author": "knowledge_manager@techfirm.net",
        "urgency": "medium",
        "sentiment": "negative",
        "sentiment_score": -0.59,
        "product_area": "Search",
        "timestamp": "2026-06-25T11:00:25Z",
        "metadata": {"ticket_id": "ZEN-9035", "tier": "Business"}
    },
    {
        "id": "FB-7002",
        "text": "Search indexing queue backlog: Elasticsearch worker consumer group stalls when ingesting batch updates over 500 documents.",
        "source": "github",
        "author": "search_infra_engineer",
        "urgency": "medium",
        "sentiment": "negative",
        "sentiment_score": -0.61,
        "product_area": "Search",
        "timestamp": "2026-06-25T14:44:10Z",
        "metadata": {"issue_number": 1470, "label": "infra:search"}
    },
    {
        "id": "FB-7003",
        "text": "Quick search modal (Cmd+K) misses files created in the last hour. I have to manually paste URLs to share notes with my team.",
        "source": "discord",
        "author": "notion_switcher_katie",
        "urgency": "medium",
        "sentiment": "negative",
        "sentiment_score": -0.45,
        "product_area": "Search",
        "timestamp": "2026-06-25T17:12:00Z",
        "metadata": {"channel": "#feedback"}
    },

    # Theme 8: Dark Mode Contrast Ratio Fails WCAG AA Compliance (Low / Polish)
    {
        "id": "FB-8001",
        "text": "Accessibility issue: In dark mode, secondary action buttons have a contrast ratio of only 2.4:1 against the dark background, failing WCAG AA.",
        "source": "github",
        "author": "a11y_auditor_pro",
        "urgency": "low",
        "sentiment": "neutral",
        "sentiment_score": -0.25,
        "product_area": "UI/UX",
        "timestamp": "2026-06-26T09:20:15Z",
        "metadata": {"issue_number": 1482, "label": "accessibility:wcag"}
    },
    {
        "id": "FB-8002",
        "text": "The dark theme looks sleek, but the muted gray text on tag labels (#64748B on #0F172A) is impossible to read in bright daylight.",
        "source": "discord",
        "author": "sunny_designer",
        "urgency": "low",
        "sentiment": "neutral",
        "sentiment_score": -0.15,
        "product_area": "UI/UX",
        "timestamp": "2026-06-26T13:05:40Z",
        "metadata": {"channel": "#ui-polish"}
    },

    # Positive / Praise / Delight feedback (For balanced distribution)
    {
        "id": "FB-9001",
        "text": "The AI summary feature saved our product team 5 hours of manual customer feedback review this week. Super impressed with accuracy!",
        "source": "g2_reviews",
        "author": "Director of Product Management",
        "urgency": "low",
        "sentiment": "positive",
        "sentiment_score": 0.94,
        "product_area": "Analytics",
        "timestamp": "2026-06-26T15:30:10Z",
        "metadata": {"rating": 5, "verified": True}
    },
    {
        "id": "FB-9002",
        "text": "Customer survey: The lightning-fast keyboard shortcuts and clean workspace layout make this our favorite knowledge management tool.",
        "source": "customer_survey",
        "author": "lead_architect@startup.io",
        "urgency": "low",
        "sentiment": "positive",
        "sentiment_score": 0.88,
        "product_area": "UI/UX",
        "timestamp": "2026-06-26T16:45:00Z",
        "metadata": {"nps_score": 10}
    }
]

def generate_seed_data(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(DATASET, f, indent=2)
    print(f"Successfully generated {len(DATASET)} seed feedback items at {output_path}")

if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "seed_feedback.json"
    generate_seed_data(target)
