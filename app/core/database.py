from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
PRODUCTS_DB_PATH = DATA_DIR / "products.db"
CUSTOMER_DB_PATH = DATA_DIR / "customer_interactions.db"


def get_products_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(PRODUCTS_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_customer_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(CUSTOMER_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_databases() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _init_products_database()
    _init_customer_database()


def _init_products_database() -> None:
    with get_products_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                pricing REAL NOT NULL,
                regions TEXT NOT NULL,
                category TEXT NOT NULL,
                eligible_customer_types TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS product_solution_features (
                feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                feature_name TEXT NOT NULL,
                feature_description TEXT NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(product_id)
            );

            CREATE TABLE IF NOT EXISTS product_challenge_mapping (
                mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                challenge_code TEXT NOT NULL,
                relevance_score REAL NOT NULL,
                rationale TEXT NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(product_id)
            );
            """
        )

        connection.execute("DELETE FROM product_challenge_mapping")
        connection.execute("DELETE FROM product_solution_features")
        connection.execute("DELETE FROM products")

        products, features, challenge_mappings = _build_product_seed()
        connection.executemany(
            """
            INSERT INTO products (
                product_id, name, description, pricing, regions, category, eligible_customer_types
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            products,
        )

        connection.executemany(
            """
            INSERT INTO product_solution_features (product_id, feature_name, feature_description)
            VALUES (?, ?, ?)
            """,
            features,
        )

        connection.executemany(
            """
            INSERT INTO product_challenge_mapping (product_id, challenge_code, relevance_score, rationale)
            VALUES (?, ?, ?, ?)
            """,
            challenge_mappings,
        )


def _init_customer_database() -> None:
    with get_customer_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_type TEXT NOT NULL,
                segment TEXT NOT NULL,
                region TEXT NOT NULL,
                annual_volume REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS customer_product_usage (
                usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                usage_level TEXT NOT NULL,
                usage_score REAL NOT NULL,
                feedback_summary TEXT NOT NULL,
                feedback_sentiment TEXT NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
            );

            CREATE TABLE IF NOT EXISTS customer_business_challenges (
                challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                challenge_code TEXT NOT NULL,
                challenge_description TEXT NOT NULL,
                priority_score REAL NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
            );
            """
        )

        connection.execute("DELETE FROM customer_business_challenges")
        connection.execute("DELETE FROM customer_product_usage")
        connection.execute("DELETE FROM customers")

        customers, usage_rows, challenge_rows = _build_customer_seed()
        connection.executemany(
            """
            INSERT INTO customers (
                customer_id, customer_name, customer_type, segment, region, annual_volume
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            customers,
        )

        connection.executemany(
            """
            INSERT INTO customer_product_usage (
                customer_id, product_id, usage_level, usage_score, feedback_summary, feedback_sentiment
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            usage_rows,
        )

        connection.executemany(
            """
            INSERT INTO customer_business_challenges (
                customer_id, challenge_code, challenge_description, priority_score
            ) VALUES (?, ?, ?, ?)
            """,
            challenge_rows,
        )


def _build_product_seed():
    products = [
        (
            "P001",
            "AML Basic",
            "Entry-level anti-money-laundering monitoring for transaction screening and alert review.",
            15000.0,
            "NA,EU,APAC",
            "risk",
            "issuer,acquirer",
        ),
        (
            "P002",
            "AML Premium",
            "Advanced AML solution with deeper rule configuration, case workflows, and enhanced alert triage.",
            35000.0,
            "NA,EU,APAC,LATAM",
            "risk",
            "issuer,acquirer",
        ),
        (
            "P003",
            "Fraud Detection",
            "Real-time fraud monitoring across card transactions with configurable detection rules.",
            28000.0,
            "NA,EU,APAC",
            "fraud",
            "issuer,acquirer",
        ),
        (
            "P004",
            "Currency Handling",
            "Cross-border currency handling and conversion support for international payment operations.",
            22000.0,
            "EU,APAC,LATAM",
            "payments",
            "issuer",
        ),
        (
            "P005",
            "Chargeback Intelligence",
            "Dispute analytics and chargeback trend visibility for operational optimization.",
            18000.0,
            "NA,EU",
            "operations",
            "acquirer",
        ),
        (
            "P006",
            "Merchant Insights",
            "Portfolio analytics for merchant performance, transaction trends, and acceptance optimization.",
            24000.0,
            "NA,EU,APAC,LATAM",
            "analytics",
            "acquirer",
        ),
        (
            "P007",
            "Token Vault",
            "Secure tokenization service for storing payment credentials and reducing card data exposure.",
            26000.0,
            "NA,EU,APAC",
            "security",
            "issuer,acquirer",
        ),
        (
            "P008",
            "Authorization Optimizer",
            "Decisioning support to improve approval rates while controlling risk across issuer portfolios.",
            31000.0,
            "NA,EU,APAC",
            "payments",
            "issuer",
        ),
    ]

    features = [
        ("P001", "Sanctions Screening", "Checks transactions against sanctions and watch lists."),
        ("P001", "Alert Review", "Provides basic queue-based alert investigation workflow."),
        ("P002", "Workflow Automation", "Routes alerts through configurable case workflows."),
        ("P002", "Advanced Rules", "Supports sophisticated AML rule tuning for complex portfolios."),
        ("P003", "Real-Time Scoring", "Scores payment events quickly for suspicious activity."),
        ("P003", "Rule Tuning", "Adjusts fraud logic based on emerging transaction patterns."),
        ("P004", "FX Conversion", "Handles currency conversion for cross-border payment flows."),
        ("P004", "Settlement Support", "Improves settlement handling for multi-currency transactions."),
        ("P005", "Dispute Insights", "Highlights chargeback drivers and recurring dispute patterns."),
        ("P005", "Operational Dashboard", "Tracks case outcomes and dispute recovery progress."),
        ("P006", "Portfolio Analytics", "Surfaces merchant-level trends, segments, and performance patterns."),
        ("P006", "Acceptance Insights", "Highlights approval bottlenecks and conversion opportunities."),
        ("P007", "Network Tokenization", "Replaces sensitive PAN data with secure payment tokens."),
        ("P007", "Credential Lifecycle", "Manages token provisioning, rotation, and secure storage."),
        ("P008", "Approval Lift Rules", "Optimizes issuer authorization decisions with configurable strategies."),
        ("P008", "Risk-Approval Balance", "Improves approvals without materially increasing fraud exposure."),
    ]

    challenge_mappings = [
        ("P001", "regulatory_monitoring", 0.90, "AML Basic addresses baseline compliance and screening needs."),
        ("P002", "high_alert_volume", 0.95, "AML Premium reduces manual effort for customers handling many alerts."),
        ("P002", "regulatory_monitoring", 0.85, "AML Premium extends AML controls for mature programs."),
        ("P003", "fraud_spikes", 0.95, "Fraud Detection directly targets suspicious transaction spikes."),
        ("P003", "false_declines", 0.80, "Fraud controls can reduce unnecessary declines with better rules."),
        ("P004", "cross_border_growth", 0.92, "Currency Handling helps customers expanding internationally."),
        ("P004", "settlement_complexity", 0.86, "Currency Handling simplifies multi-currency settlement problems."),
        ("P005", "chargeback_increase", 0.94, "Chargeback Intelligence improves dispute visibility and actioning."),
        ("P005", "operational_efficiency", 0.76, "Chargeback analytics can reduce manual operational effort."),
        ("P006", "operational_efficiency", 0.82, "Merchant Insights exposes workflows and merchant segments that need attention."),
        ("P006", "false_declines", 0.71, "Merchant analytics can reveal acceptance friction and unnecessary declines."),
        ("P007", "regulatory_monitoring", 0.68, "Token Vault reduces sensitive card-data handling and strengthens security controls."),
        ("P007", "fraud_spikes", 0.73, "Tokenization limits credential abuse vectors tied to fraud growth."),
        ("P008", "false_declines", 0.93, "Authorization Optimizer directly targets issuer approval-rate issues."),
        ("P008", "fraud_spikes", 0.60, "Decisioning optimization helps manage risk while improving approvals."),
    ]

    generated_templates = [
        (
            "Compliance Guard",
            "Enhanced compliance monitoring for institutions that need stronger analyst workflows and oversight.",
            21000.0,
            "NA,EU,APAC",
            "risk",
            "issuer,acquirer",
            [
                ("Alert Prioritization", "Highlights the most urgent compliance alerts first."),
                ("Analyst Console", "Provides a consolidated workspace for compliance investigations."),
            ],
            [
                ("regulatory_monitoring", 0.78, "Compliance Guard supports organizations strengthening monitoring controls."),
                ("high_alert_volume", 0.74, "Compliance Guard reduces friction when alert queues become difficult to manage."),
            ],
        ),
        (
            "Fraud Shield",
            "Fraud prevention controls for payment portfolios facing higher attack rates and transaction anomalies.",
            25500.0,
            "NA,EU,APAC,LATAM",
            "fraud",
            "issuer,acquirer",
            [
                ("Anomaly Detection", "Flags transaction behaviors that deviate from expected activity."),
                ("Rule Studio", "Supports quick fraud-rule adjustments during active incidents."),
            ],
            [
                ("fraud_spikes", 0.83, "Fraud Shield helps teams respond to rising suspicious activity."),
                ("false_declines", 0.69, "Fraud Shield can reduce unnecessary good-customer declines with better controls."),
            ],
        ),
        (
            "Dispute Navigator",
            "Operational tooling for resolving disputes, tracking recovery, and improving merchant servicing.",
            20500.0,
            "NA,EU,LATAM",
            "operations",
            "acquirer",
            [
                ("Case Tracking", "Keeps dispute operations aligned around current case status."),
                ("Recovery Insights", "Highlights recovery trends and dispute leakage."),
            ],
            [
                ("chargeback_increase", 0.88, "Dispute Navigator directly addresses rising dispute volume."),
                ("operational_efficiency", 0.79, "Dispute Navigator reduces manual case handling overhead."),
            ],
        ),
        (
            "Issuer Growth Hub",
            "Portfolio tools for issuers looking to improve approvals and scale card-program performance.",
            29500.0,
            "NA,EU,APAC",
            "payments",
            "issuer",
            [
                ("Approval Insights", "Shows approval-rate patterns across issuer segments."),
                ("Decision Support", "Supports faster refinement of authorization strategies."),
            ],
            [
                ("false_declines", 0.82, "Issuer Growth Hub helps teams improve approval-rate performance."),
                ("fraud_spikes", 0.58, "Issuer Growth Hub balances approval growth with risk controls."),
            ],
        ),
        (
            "Merchant Operations Cloud",
            "Merchant analytics and workflow support for large acquirer service and operations teams.",
            24500.0,
            "NA,EU,APAC,LATAM",
            "analytics",
            "acquirer",
            [
                ("Merchant Segmentation", "Groups merchants by operational and performance patterns."),
                ("Workflow Dashboard", "Centralizes activity across operations teams and merchant portfolios."),
            ],
            [
                ("operational_efficiency", 0.84, "Merchant Operations Cloud highlights where operational effort is being lost."),
                ("chargeback_increase", 0.64, "Merchant Operations Cloud helps identify merchant cohorts driving disputes."),
            ],
        ),
        (
            "Credential Protect",
            "Security tooling for protecting payment credentials and tightening exposure controls.",
            23250.0,
            "NA,EU,APAC",
            "security",
            "issuer,acquirer",
            [
                ("Credential Safeguards", "Reduces direct card-data exposure across payment systems."),
                ("Lifecycle Policies", "Applies governance to credential provisioning and rotation."),
            ],
            [
                ("regulatory_monitoring", 0.66, "Credential Protect improves security posture for regulated portfolios."),
                ("fraud_spikes", 0.61, "Credential Protect reduces exposure from compromised payment credentials."),
            ],
        ),
    ]

    for product_number in range(9, 101):
        template = generated_templates[(product_number - 9) % len(generated_templates)]
        product_id = f"P{product_number:03d}"
        name = f"{template[0]} {product_number:03d}"
        description = f"{template[1]} Mock product variant {product_number:03d} for seeded recommendation scenarios."
        pricing = template[2] + float((product_number % 6) * 1250)
        products.append(
            (
                product_id,
                name,
                description,
                pricing,
                template[3],
                template[4],
                template[5],
            )
        )

        for feature_name, feature_description in template[6]:
            features.append(
                (
                    product_id,
                    feature_name,
                    f"{feature_description} Included in seeded variant {product_number:03d}.",
                )
            )

        for challenge_code, relevance_score, rationale in template[7]:
            challenge_mappings.append(
                (
                    product_id,
                    challenge_code,
                    relevance_score,
                    f"{rationale} Variant {product_number:03d} keeps the same business fit.",
                )
            )

    return products, features, challenge_mappings


def _build_customer_seed():
    customers = [
        ("C001", "Northwind Bank", "issuer", "enterprise", "EU", 2500000.0),
        ("C002", "Harbor Payments", "acquirer", "mid_market", "NA", 900000.0),
        ("C003", "Skyline Credit", "issuer", "enterprise", "APAC", 3200000.0),
        ("C004", "Pioneer Commerce", "acquirer", "enterprise", "LATAM", 1800000.0),
        ("C005", "Summit Card Services", "issuer", "mid_market", "NA", 1400000.0),
        ("C006", "Atlas Pay Network", "acquirer", "enterprise", "EU", 4100000.0),
    ]

    usage_rows = [
        ("C001", "P003", "high", 0.89, "Fraud monitoring works well but cross-border support is limited.", "positive"),
        ("C001", "P001", "medium", 0.67, "AML alerts are manageable but workflows are manual.", "neutral"),
        ("C002", "P001", "low", 0.42, "Needs better operational visibility and lower manual effort.", "neutral"),
        ("C003", "P001", "high", 0.91, "Strong AML coverage but alert volume is rising quickly.", "positive"),
        ("C004", "P005", "medium", 0.74, "Dispute analytics help, but merchant visibility is still fragmented.", "positive"),
        ("C004", "P007", "low", 0.38, "Tokenization rollout is early and not yet scaled across merchants.", "neutral"),
        ("C005", "P003", "medium", 0.71, "Fraud controls are useful, though approval rates are still inconsistent.", "neutral"),
        ("C006", "P005", "high", 0.87, "Chargeback tooling is valuable but operations still rely on manual reporting.", "positive"),
        ("C006", "P006", "medium", 0.65, "Merchant analytics are helping identify outliers across the portfolio.", "positive"),
    ]

    challenge_rows = [
        ("C001", "cross_border_growth", "Customer is expanding international card programs.", 0.96),
        ("C001", "settlement_complexity", "Customer wants better multi-currency settlement support.", 0.80),
        ("C002", "chargeback_increase", "Chargebacks have increased in the last two quarters.", 0.93),
        ("C002", "operational_efficiency", "Operations team spends too much time on dispute handling.", 0.72),
        ("C003", "high_alert_volume", "Investigators are overloaded by AML alert volume.", 0.95),
        ("C003", "fraud_spikes", "Fraud incidents are increasing in one market corridor.", 0.65),
        ("C004", "chargeback_increase", "Several merchant cohorts are showing rising dispute rates.", 0.89),
        ("C004", "operational_efficiency", "Relationship managers need a clearer view of merchant portfolio performance.", 0.83),
        ("C005", "false_declines", "Approval rates have softened and good customers are being declined too often.", 0.94),
        ("C005", "fraud_spikes", "Issuer risk teams are watching elevated fraud in card-not-present channels.", 0.58),
        ("C006", "operational_efficiency", "Dispute and merchant operations are spread across too many manual processes.", 0.91),
        ("C006", "chargeback_increase", "Cross-border merchants are driving more complex disputes.", 0.81),
    ]

    name_prefixes = [
        "Aurora",
        "Beacon",
        "Crest",
        "Delta",
        "Evergreen",
        "Frontier",
        "Granite",
        "Harbor",
        "Ion",
        "Juniper",
        "Keystone",
        "Liberty",
        "Meridian",
        "Nova",
        "Orion",
        "Praxis",
        "Quantum",
        "Radius",
        "Sterling",
        "Trident",
    ]
    regions = ["NA", "EU", "APAC", "LATAM"]
    segments = ["enterprise", "mid_market", "growth"]
    issuer_owned_products = ["P001", "P003", "P007"]
    acquirer_owned_products = ["P001", "P005", "P006", "P007"]
    issuer_challenges = ["high_alert_volume", "false_declines", "fraud_spikes", "regulatory_monitoring"]
    acquirer_challenges = ["chargeback_increase", "operational_efficiency", "false_declines", "regulatory_monitoring"]
    usage_levels = ["low", "medium", "high"]
    usage_scores = [0.44, 0.63, 0.81]
    sentiments = ["neutral", "positive", "neutral"]

    for customer_number in range(7, 101):
        customer_id = f"C{customer_number:03d}"
        customer_type = "issuer" if customer_number % 2 else "acquirer"
        segment = segments[customer_number % len(segments)]
        region = regions[customer_number % len(regions)]
        annual_volume = float(650000 + (customer_number * 47000))
        name_root = name_prefixes[(customer_number - 7) % len(name_prefixes)]
        if customer_type == "issuer":
            customer_name = f"{name_root} Card Bank {customer_number:03d}"
        else:
            customer_name = f"{name_root} Merchant Payments {customer_number:03d}"

        customers.append((customer_id, customer_name, customer_type, segment, region, annual_volume))

        owned_products = issuer_owned_products if customer_type == "issuer" else acquirer_owned_products
        primary_product = owned_products[customer_number % len(owned_products)]
        usage_index = customer_number % len(usage_levels)
        usage_rows.append(
            (
                customer_id,
                primary_product,
                usage_levels[usage_index],
                usage_scores[usage_index],
                f"Customer {customer_id} is using {primary_product} and wants stronger portfolio outcomes with less manual effort.",
                sentiments[usage_index],
            )
        )

        if customer_number % 4 == 0:
            secondary_product = owned_products[(customer_number + 1) % len(owned_products)]
            if secondary_product != primary_product:
                secondary_usage_index = (customer_number + 1) % len(usage_levels)
                usage_rows.append(
                    (
                        customer_id,
                        secondary_product,
                        usage_levels[secondary_usage_index],
                        usage_scores[secondary_usage_index],
                        f"Customer {customer_id} is expanding adoption of {secondary_product} across additional teams.",
                        sentiments[secondary_usage_index],
                    )
                )

        customer_challenges = issuer_challenges if customer_type == "issuer" else acquirer_challenges
        primary_challenge = customer_challenges[customer_number % len(customer_challenges)]
        secondary_challenge = customer_challenges[(customer_number + 1) % len(customer_challenges)]
        challenge_rows.append(
            (
                customer_id,
                primary_challenge,
                f"Customer {customer_id} is prioritizing {primary_challenge.replace('_', ' ')} improvements this quarter.",
                round(0.65 + ((customer_number % 5) * 0.06), 2),
            )
        )
        challenge_rows.append(
            (
                customer_id,
                secondary_challenge,
                f"Customer {customer_id} also needs progress on {secondary_challenge.replace('_', ' ')}.",
                round(0.52 + ((customer_number % 4) * 0.05), 2),
            )
        )

    return customers, usage_rows, challenge_rows
