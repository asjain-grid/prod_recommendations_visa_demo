# Project Overview

## Description

This project is a lightweight FastAPI-based product recommendation system for Visa-style customer portfolios.

It helps identify:
- cross-sell opportunities for products a customer does not currently use
- upsell opportunities for higher-tier products when current usage suggests readiness
- customer-to-product fit using business challenges, product eligibility, region support, and current product usage

## Current MVP Scope

- SQLite-backed mock product catalog
- SQLite-backed customer interaction and feedback data
- product-to-challenge mapping for explainable recommendations
- FastAPI endpoint for customer-specific recommendations
- seeded sample data for local validation
- pytest coverage for the recommendation API

## Business Value

The system is designed to help account teams answer two simple questions:
- what should be recommended next
- why that product is a relevant recommendation

## Main Documents

- Root README explains setup, run steps, and current API surface.
- The architecture reference is in [docs/architecture.md](docs/architecture.md).
- This overview summarizes scope and intent for quick onboarding.
