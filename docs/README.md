# Project Documentation — Wind Forecast & Accuracy Portal

> **Status: design specification (pre-implementation).**
> This documentation describes the intended design. As of this writing no application
> code is implemented and nothing is deployed. Statements here are the planned design,
> not claims of working functionality. Each document distinguishes **planned** from
> **implemented** work, and no live URL is published until deployment is verified.

A web application for a UK energy utility's **day-ahead electricity purchasing team**. It helps them:

1. See the **latest eligible national wind generation forecast** available at the point a purchasing decision is made.
2. **Quantify wind forecast accuracy** by comparing forecasts against actual generation.

Scope is deliberately limited to **Elexon national wind** actuals (FUELHH) and forecasts (WINDFOR), for purchasing decisions made in **January 2026**.

## Documentation map

| # | Document | Covers |
|---|---|---|
| 01 | [Overview](01-overview.md) | Business objective, users, what the product does and explicitly does **not** do |
| 02 | [Architecture](02-architecture.md) | Components, responsibilities, data flow, directory layout |
| 03 | [Data Sources](03-data-sources.md) | Elexon FUELHH & WINDFOR endpoints, fields, units, time conventions |
| 04 | [Methodology](04-methodology.md) | Forecast selection (point-in-time correctness), error metrics |
| 05 | [API Reference](05-api-reference.md) | Endpoints, parameters, response schemas, error codes |
| 06 | [Frontend](06-frontend.md) | Views, components, state, UI states |
| 07 | [Testing](07-testing.md) | Test strategy, cases, how to run |
| 08 | [Deployment](08-deployment.md) | Hosting architecture, env vars, steps (decision pending) |
| 09 | [Local Development](09-local-development.md) | Docker, build/run/test commands, configuration |
| 10 | [Edge Cases & Data Quality](10-edge-cases-and-data-quality.md) | Missing/duplicate/misaligned data, failure handling |
| 11 | [Assumptions & Limitations](11-assumptions-and-limitations.md) | Open questions, scope limits, future work |

## Core principles carried through all docs

- **Point-in-time correctness.** Only use forecast data that was published on or before a *configurable* purchasing cutoff. Never use a later forecast to score an earlier decision (look-ahead bias).
- **No silent zero-filling.** Missing data is handled explicitly and excluded from metrics; it is never treated as `0 MW`.
- **Scope honesty.** The datasets cover national wind only. The app quantifies *wind forecast uncertainty*; it does **not** compute a definitive electricity shortfall or purchase quantity.
- **Precise claims.** Implemented functionality is distinguished from planned work throughout.
