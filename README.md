# FastAPI Product Recommendation MVP

This project is a lightweight product recommendation system built with FastAPI and SQLite for Visa-style customer portfolios.

It focuses on simple, explainable recommendations for cross-sell and upsell opportunities by combining:
- product metadata and pricing
- regional availability and solution features
- customer product usage and feedback
- customer business challenges mapped to relevant products

## Project Description

The current MVP helps relationship teams identify which product should be recommended next for an existing customer and why the recommendation is relevant.

It uses two SQLite databases:
- one for products, solution features, pricing, regions, and challenge mappings
- one for customers, current product usage, feedback, and business challenges

Seed initialization creates a larger mock dataset for realistic testing:
- 100 products in the product catalog database
- 100 customers in the customer interaction database

## Documentation

- Overview: [docs/project-overview.md](docs/project-overview.md)
- Architecture: [docs/architecture.md](docs/architecture.md)

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
pytest
```

## Endpoint

- `GET /health`
- `GET /customers/{customer_id}/recommendations`

## Databases

- `data/products.db`
  - stores products, pricing, descriptions, supported regions, solution features, and challenge mappings
  - seeded with 100 mock products
- `data/customer_interactions.db`
  - stores customers, current product usage, feedback summaries, and business challenges
  - seeded with 100 mock customers

## Recommendation Logic

- Cross-sell excludes products the customer already owns.
- Upsell currently supports `AML Basic` to `AML Premium`.
- Product-to-challenge mapping boosts relevance for customers facing matching business challenges.