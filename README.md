# FastAPI Product Recommendation MVP

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
- `data/customer_interactions.db`
  - stores customers, current product usage, feedback summaries, and business challenges

## Recommendation Logic

- Cross-sell excludes products the customer already owns.
- Upsell currently supports `AML Basic` to `AML Premium`.
- Product-to-challenge mapping boosts relevance for customers facing matching business challenges.