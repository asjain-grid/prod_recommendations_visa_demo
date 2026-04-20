# Product Recommendation System Plan

## Goal
- Build a Python FastAPI service that recommends Visa products to customers and exposes analytics for cross-sell and upsell opportunities.
- Support two customer relationship types: acquirer and issuer.
- Start with an explainable, testable recommendation engine before introducing heavier ML.

## Working Assumptions
- Products include AML solution, Fraud detection, Currency handling, and similar Visa offerings.
- Existing customers already have a known relationship type, current product usage, and basic business profile.
- The first version should prioritize accuracy, explainability, and speed of delivery over complex modeling.
- Recommendations should answer two questions:
	- What product should be recommended next?
	- Why is this recommendation being made?

## MVP Scope
- Customer and product master data ingestion.
- Current product usage tracking.
- Recommendation generation for existing customers.
- Opportunity analytics for cross-sell and upsell.
- REST APIs for recommendation retrieval and analytics summaries.
- Audit-friendly scoring output with reasons.

## Out Of Scope For MVP
- Real-time event streaming.
- Deep learning models.
- Fully automated CRM integration.
- UI application beyond API docs and test payloads.

## Recommended Architecture

### 1. API Layer
- Framework: FastAPI
- Purpose: expose endpoints for customers, products, recommendations, analytics, and model health.
- Output: JSON responses with recommendation score, rank, and explanation.

### 2. Recommendation Service Layer
- Encapsulates recommendation logic.
- Starts with a hybrid scoring engine:
	- rule-based eligibility filters
	- similarity-based scoring using customer/product features
	- simple weighted business rules for cross-sell and upsell
- Keeps logic deterministic and easy to test.

### 3. Analytics Service Layer
- Computes opportunity summaries such as:
	- product adoption by customer segment
	- white-space opportunities by issuer/acquirer segment
	- upsell candidates based on product maturity or usage intensity
- Returns aggregated metrics for dashboards or downstream BI tools.

### 4. Data Layer
- Recommended database: PostgreSQL
- Core tables:
	- customers
	- customer_relationships
	- products
	- customer_products
	- recommendation_runs
	- recommendations
- Keep schema relational for clear joins, traceability, and SQL-based analytics.

### 5. Batch Scoring Job
- Initial recommendation generation should run as a scheduled batch job.
- Reason: easier to validate than real-time scoring and sufficient for account-planning workflows.
- FastAPI can still expose on-demand scoring for a single customer when needed.

## Domain Model

### Customer
- customer_id
- name
- segment
- region
- annual_volume
- relationship_type: issuer, acquirer, or both

### Product
- product_id
- name
- category
- tier
- eligibility_rules
- upsell_parent_product

### CustomerProductUsage
- customer_id
- product_id
- adoption_status
- start_date
- usage_level
- revenue_contribution

### Recommendation
- customer_id
- product_id
- recommendation_type: cross_sell or upsell
- score
- rank
- reasons
- generated_at

## Recommendation Logic For MVP

### Cross-Sell
- Recommend products not currently used by the customer.
- Score based on:
	- relationship type fit
	- peer adoption within similar customers
	- product affinity with already-used products
	- segment and region fit

### Upsell
- Recommend higher-tier or adjacent products where a base product already exists.
- Score based on:
	- current product ownership
	- usage intensity
	- revenue or volume thresholds
	- maturity signals defined by business rules

### Explainability
- Every recommendation should include 2-4 explicit reasons.
- Example:
	- Uses Fraud detection and AML solution
	- Peer issuers in same segment often adopt Currency handling
	- Annual transaction volume exceeds threshold for premium tier

## API Design

### Core Endpoints
- GET /health
- POST /customers
- POST /products
- POST /customer-products
- GET /customers/{customer_id}/recommendations
- POST /recommendations/run
- GET /analytics/opportunities
- GET /analytics/products/{product_id}

### Example Response Shape
```json
{
	"customer_id": "C1001",
	"recommendations": [
		{
			"product_id": "P2003",
			"product_name": "Currency Handling",
			"recommendation_type": "cross_sell",
			"score": 0.88,
			"rank": 1,
			"reasons": [
				"Customer is an issuer with high transaction volume",
				"Similar issuer customers adopted this product after Fraud Detection"
			]
		}
	]
}
```

## Delivery Plan

### Phase 1: Foundation
- Define schema and sample data.
- Build FastAPI app skeleton.
- Add data models, validation, and health endpoint.

### Phase 2: Recommendation Engine
- Implement eligibility filters.
- Implement weighted scoring for cross-sell and upsell.
- Add recommendation persistence.

### Phase 3: Analytics
- Add opportunity summary endpoints.
- Add segment-level aggregation queries.
- Validate business outputs with sample scenarios.

### Phase 4: Hardening
- Add auth if needed.
- Add logging, config, and batch scheduling.
- Add test fixtures and API contract tests.

## Test Strategy
- Unit tests for scoring rules and eligibility filters.
- API tests for endpoint contracts.
- Seeded integration tests using a small fixed dataset.
- Golden test cases for key scenarios:
	- issuer with Fraud detection gets Currency handling recommendation
	- acquirer with AML solution gets no ineligible issuer-only products
	- customer with base tier gets upsell recommendation only after threshold is met

## Suggested Repo Layout
```text
app/
	main.py
	api/
	core/
	models/
	schemas/
	services/
	repositories/
	analytics/
	jobs/
tests/
	unit/
	integration/
data/
	seed/
```

## Implementation Recommendation
- Use a rule-first engine for MVP.
- Add ML later only after enough historical recommendation and conversion data exists.
- This reduces delivery risk and makes stakeholder review easier.

## Clarifications Needed Before Coding
1. Are the “two sets of customers” strictly issuer and acquirer, or do you also want support for customers that belong to both?
2. What customer attributes are available in the source data: segment, geography, transaction volume, revenue, risk tier, current products?
3. Do you want recommendations only for existing customers, or also for net-new prospects?
4. Is the first version expected to use only business rules, or do you already have historical sales/product adoption data for ML-based scoring?
5. Should analytics be API-only, or do you expect export-ready outputs such as CSV/Excel summaries?

## Proposed Next Step
- After you answer the clarifications, the next deliverable should be a minimal FastAPI project skeleton with schema, sample seed data, deterministic recommendation rules, and automated tests.
