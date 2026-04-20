# Product Recommendation System Architecture

## Objective

Build a simple, testable product recommendation system using Python and FastAPI for Visa customers.

The system should:
- store customers and products
- track existing product usage
- recommend cross-sell and upsell opportunities
- expose analytics through API endpoints

This design assumes the smallest practical MVP.

## Minimal Assumptions

- Customer types are `issuer` and `acquirer`.
- A customer belongs to exactly one type in MVP.
- Recommendations are generated only for existing customers.
- Product catalog is small and managed manually.
- Business rules are enough for version 1.
- Historical ML training data does not exist yet.
- Analytics are exposed through APIs only.
- A relational database may be added later, but MVP can start with seeded local storage for fast validation.

## Design Principles

- Keep the logic deterministic.
- Keep recommendations explainable.
- Keep components easy to unit test.
- Prefer simple scoring over complex ML.
- Separate API, business logic, and storage.

## High-Level Architecture

```text
Client
  |
  v
FastAPI Application
  |
  +-- API Routes
  |
  +-- Recommendation Service
  |
  +-- Analytics Service
  |
  +-- Repository Layer
         |
         +-- Seed Data / JSON / SQLite for MVP
```

## Core Components

### 1. FastAPI Application

Responsible for:
- exposing REST endpoints
- validating requests and responses
- coordinating service calls

Main responsibility is transport only. It should not contain recommendation logic.

### 2. Recommendation Service

Responsible for:
- checking product eligibility
- identifying cross-sell candidates
- identifying upsell candidates
- scoring and ranking recommendations
- returning recommendation reasons

This is the core business layer.

### 3. Analytics Service

Responsible for:
- counting opportunity totals by customer type
- aggregating product recommendation frequency
- summarizing cross-sell and upsell opportunities

This service should operate on the same recommendation outputs used by the API.

### 4. Repository Layer

Responsible for:
- reading customers
- reading products
- reading customer product usage
- saving recommendation results if persistence is enabled

For MVP, this can use simple seeded files or SQLite.
For later versions, this can move to PostgreSQL with minimal service changes.

## Recommended MVP Data Model

### Customer

- `customer_id`
- `name`
- `customer_type` (`issuer` or `acquirer`)
- `segment`
- `region`
- `annual_volume`

### Product

- `product_id`
- `name`
- `category`
- `eligible_customer_types`
- `tier`
- `upsell_from_product_id` (optional)

### CustomerProduct

- `customer_id`
- `product_id`
- `status`
- `usage_level`

### Recommendation

- `customer_id`
- `product_id`
- `recommendation_type` (`cross_sell` or `upsell`)
- `score`
- `rank`
- `reasons`

## Recommendation Strategy

### Cross-Sell Logic

Recommend products the customer does not already have.

Basic scoring inputs:
- customer type eligibility
- product category affinity
- customer segment fit
- simple business priority weight

Example:
- if customer uses `Fraud Detection`, recommend `Currency Handling`
- if customer is `issuer`, avoid `acquirer`-only products

### Upsell Logic

Recommend a higher-tier product only when the customer already owns the base product.

Basic scoring inputs:
- existing product ownership
- usage level
- annual volume threshold

Example:
- if customer has `AML Basic` and usage is high, recommend `AML Premium`

### Score Model

Use a simple weighted score from `0.0` to `1.0`.

Example weights:
- eligibility match: required gate
- product affinity: `0.3`
- segment fit: `0.2`
- usage/volume fit: `0.3`
- business priority: `0.2`

This does not need to be mathematically perfect in MVP. It only needs to be consistent and testable.

### Explainability

Each recommendation should include a short list of reasons.

Example:
- `Customer type is eligible for this product`
- `Customer already uses a related fraud product`
- `Annual volume is above upsell threshold`

## API Endpoints

### Health

- `GET /health`

Purpose:
- confirm service is alive

### Customer Endpoints

- `GET /customers`
- `GET /customers/{customer_id}`

Purpose:
- retrieve customer information

### Recommendation Endpoints

- `GET /customers/{customer_id}/recommendations`
- `POST /recommendations/run`

Purpose:
- return current recommendations for one customer
- trigger recommendation generation for all customers

### Analytics Endpoints

- `GET /analytics/opportunities`
- `GET /analytics/products`

Purpose:
- show cross-sell and upsell opportunity counts
- show most recommended products

## Request and Response Shape

### Example Recommendation Response

```json
{
  "customer_id": "C001",
  "recommendations": [
    {
      "product_id": "P003",
      "product_name": "Currency Handling",
      "recommendation_type": "cross_sell",
      "score": 0.84,
      "rank": 1,
      "reasons": [
        "Customer type is eligible for this product",
        "Customer already uses a related fraud product"
      ]
    }
  ]
}
```

## Execution Flow

### Option 1: On-Demand For Single Customer

1. API receives customer recommendation request.
2. Customer and current products are loaded.
3. Eligible products are identified.
4. Cross-sell and upsell candidates are scored.
5. Top recommendations are ranked and returned.

### Option 2: Batch Run For All Customers

1. API or scheduled job starts recommendation run.
2. System iterates through all customers.
3. Recommendations are generated and stored.
4. Analytics service reads stored results.

For MVP, support both but implement batch as a simple loop.

## Storage Choice For MVP

### Recommended Start

Use SQLite or seeded JSON files.

Reason:
- fast to build
- easy to test locally
- low setup overhead

### Later Upgrade

Move repository layer to PostgreSQL when:
- data grows
- concurrent writes matter
- reporting complexity increases

## Suggested Project Structure

```text
app/
  main.py
  api/
    routes/
      customers.py
      recommendations.py
      analytics.py
      health.py
  schemas/
    customer.py
    product.py
    recommendation.py
  services/
    recommendation_service.py
    analytics_service.py
  repositories/
    customer_repository.py
    product_repository.py
    recommendation_repository.py
  core/
    config.py
tests/
  unit/
  integration/
data/
  seed/
```

## Test Strategy

### Unit Tests

Test:
- eligibility filtering
- cross-sell scoring
- upsell scoring
- ranking order
- explanation generation

### Integration Tests

Test:
- API responses
- recommendation endpoint behavior
- analytics aggregation behavior

### Minimum Test Scenarios

1. Issuer with `Fraud Detection` gets `Currency Handling` as cross-sell.
2. Acquirer does not receive issuer-only products.
3. Customer already owning base AML product with high usage gets AML upsell.
4. Customer never receives a product already owned.
5. Analytics endpoint returns correct counts from seeded data.

## Non-Functional Requirements

- Fast response for single-customer recommendation requests.
- Clear error messages for missing customers or invalid inputs.
- Consistent output format across endpoints.
- Easy local startup and repeatable test execution.

## Risks And Constraints

- Rule-based scoring may be simplistic at first.
- Product affinity rules must be defined manually.
- Analytics value depends on quality of seed or source data.

These are acceptable for MVP because the goal is a working, explainable system.

## Recommended Build Sequence

1. Create FastAPI skeleton and health endpoint.
2. Add schemas and seed data.
3. Implement repository layer.
4. Implement recommendation service.
5. Implement recommendation API.
6. Implement analytics service and API.
7. Add automated tests.

## Summary

The simplest architecture is a layered FastAPI service with deterministic recommendation logic and a lightweight storage layer.

This approach is:
- easy to implement
- easy to test
- easy to explain to business stakeholders
- easy to evolve later into a more advanced ML-backed system