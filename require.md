# Requirements and Technical Documentation Notes

## 1. Project Objective

Build a web application for a UK energy utility's day-ahead electricity purchasing team. The application will help users:

1. Understand the latest eligible national wind generation forecasts available when purchasing decisions are made.
2. Quantitatively evaluate wind forecast accuracy by comparing forecasts with actual generation.

The scope is limited to Elexon national wind actuals and forecasts. Only data relevant to purchasing decisions made in **January 2026** should be considered.

## 2. Technology Stack

- **Frontend:** React
- **Backend:** Python using Flask or FastAPI
- **Data sources:** Elexon BMRS API
- **Containers:** Docker and Docker Compose
- **Deployment:** Vercel or Heroku, subject to the selected hosting architecture
- **Testing:** Unit tests and integration tests
- **Version control and automation:** Git, CI/CD where practical

## 3. Data Sources

### Actual wind generation

Endpoint: https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream

Use records where `fuelType = WIND`.

Relevant fields:
- `startTime`: Target delivery interval, at 30-minute resolution
- `generation`: Actual wind generation

### Forecast wind generation

Endpoint: https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream

Relevant fields:
- `startTime`: Target delivery interval
- `publishTime`: Time the forecast was published
- `generation`: Forecast wind generation

The application should use only these Elexon datasets for its core forecast and accuracy analysis.

## 4. Core Features

### Feature 1: Wind Generation Forecast Dashboard

- Display forecast wind generation in MW for each 30-minute delivery interval.
- Show delivery time (`startTime`) and forecast publication time (`publishTime`).
- Select the latest eligible forecast available by the configured purchasing decision cutoff.
- Allow users to inspect earlier forecast versions where available.
- Provide date and interval filters restricted to relevant January 2026 purchase decisions.
- Show loading, empty-data, stale-data, and API-error states.

### Feature 2: Forecast Accuracy and Error Analysis

- Compare forecast wind generation against actual wind generation.
- Plot forecast and actual values on the same chart.
- Provide a table containing delivery time, forecast, actual, signed error, and absolute error.
- Calculate:
  - Mean Absolute Error (MAE)
  - Root Mean Squared Error (RMSE)
  - Mean forecast bias
- Show the number of matched intervals used for each metric.
- Allow users to inspect accuracy across January 2026 purchase dates.

## 5. Forecast Evaluation Methodology

For each delivery interval, define forecast error as:

`error = forecast_generation - actual_generation`

Under this convention:
- Positive error means wind generation was overforecast.
- Negative error means wind generation was underforecast.

Metrics:
- **MAE:** Mean absolute error across matched intervals.
- **RMSE:** Square root of the mean squared error; larger errors have greater influence.
- **Bias:** Mean signed error, indicating systematic overforecasting or underforecasting.

All metrics should be reported in MW.

### Point-in-time correctness

Forecast selection must reflect what was available when the purchasing decision was made. For a given delivery interval, select the most recently published forecast whose `publishTime` is no later than the configured purchasing cutoff.

Do not use a forecast published after the cutoff. Doing so creates **look-ahead bias** and overstates the forecast quality that could have been known at decision time.

The exact operational cutoff has not been supplied. Confirm it with the client or make it configurable; do not silently assume that midnight is the cutoff.

## 6. Domain Terms

- **Day-ahead market:** Electricity is purchased ahead of the delivery day.
- **Forecast vintage:** A particular forecast version identified by its publication timestamp.
- **Forecast cutoff:** The deadline by which a forecast must have been published to be eligible for a purchasing decision.
- **Delivery interval:** The 30-minute period to which a forecast or actual value applies.
- **Point-in-time correctness:** Using only information available at the time of the decision.
- **Look-ahead bias:** Using information published after the decision time in historical evaluation.
- **Forecast error:** Forecast generation minus actual generation.
- **Forecast bias:** Average signed forecast error.
- **Data completeness:** Whether expected intervals have usable data.

## 7. API and Backend Requirements

- Design clear, versionable REST API endpoints.
- Validate request parameters and data schemas.
- Return consistent error responses.
- Handle missing data, upstream API failures, timeouts, and malformed responses gracefully.
- Keep forecast selection and metric calculation logic separate from HTTP route handlers.
- Document endpoint paths, parameters, response schemas, and error codes.
- Avoid exposing secrets or credentials in source control.

Possible endpoint structure:
- `GET /api/health` — health check
- `GET /api/forecasts` — eligible forecasts for a requested purchase/delivery date
- `GET /api/forecasts/history` — available forecast vintages for selected intervals
- `GET /api/accuracy` — forecast-versus-actual data and accuracy metrics

These paths are proposed and may be adjusted during implementation.

## 8. Frontend Requirements

- Use reusable React components.
- Provide clear date and interval selection.
- Display interactive forecast and actual charts.
- Present metric summaries and a detailed error table.
- Represent loading, empty, stale, and error states clearly.
- Keep client-side state manageable and avoid unnecessary re-renders.
- Make the interface usable on common desktop screen sizes and reasonably responsive on smaller screens.

## 9. Testing Requirements

Include tests for:
- Selecting the latest eligible forecast by `publishTime`.
- Excluding forecasts published after the purchasing cutoff.
- Calculating MAE, RMSE, and bias correctly.
- Joining forecasts and actuals by delivery interval.
- Missing, duplicate, or mismatched timestamps.
- Missing forecasts and unavailable actuals.
- Invalid query parameters and out-of-scope dates.
- Elexon API timeouts, failures, and malformed data.
- API response contracts and key frontend states.

Use unit tests for isolated logic and integration tests for API/data workflows.

## 10. Data Quality and Edge Cases

Handle and document:
- Multiple forecasts for one delivery interval.
- No eligible forecast before the cutoff.
- Actual generation not yet available.
- Duplicate or missing 30-minute intervals.
- Forecast and actual timestamps that do not align.
- Missing or invalid generation values.
- Unexpected units or timestamp conventions.
- Elexon API outages or schema changes.
- Purchase dates outside January 2026.

Do not silently treat missing values as zero. Make missing-data handling explicit and exclude unmatched intervals from accuracy metrics unless a documented method says otherwise.

## 11. Performance and Reliability

Document practical choices for:
- API timeouts and retry behavior.
- Caching and data freshness, if implemented.
- Efficient data processing using pandas/NumPy where useful.
- Logging of ingestion and request failures.
- Data validation and observability.
- Avoiding unnecessary chart rendering and frontend re-renders.

Do not claim performance targets or monitoring capabilities unless they are implemented and verified.

## 12. Docker and Local Development

Provide:
- A `Dockerfile` for the application components as appropriate.
- A `docker-compose.yml` for local development.
- Environment-variable configuration.
- Clear build and run commands.
- Instructions for running tests in the development environment.

Docker is required for reproducible local development. Confirm the hosting platform's container support and deployment model before deciding how the production deployment will run.

## 13. Deployment

The brief allows deployment on Vercel or Heroku.

Document:
- The chosen hosting platform and deployment architecture.
- Frontend and backend deployment steps.
- Required environment variables.
- How the frontend connects to the backend API.
- The live application URL after deployment.
- Any platform limitations relevant to Python services or Docker.

Do not describe the application as deployed until deployment succeeds and the URL has been verified.

## 14. README Requirements

The README should include:
1. Project overview and business objective.
2. Features and screenshots, if available.
3. Architecture and data flow.
4. Data sources and field definitions.
5. Forecast selection and accuracy methodology.
6. API reference.
7. Local setup and Docker instructions.
8. Test execution instructions.
9. Deployment instructions and live URL.
10. Assumptions, limitations, and future improvements.
11. **AI tool disclosure:** explicitly name any AI tools used and describe how they assisted with development. If no AI tools were used, state that accurately.

## 15. Scope Limitations

The provided datasets contain national wind generation forecasts and actuals only. They do not provide consumer demand or all other generation availability needed to calculate a definitive additional procurement quantity.

Therefore:
- The application may quantify wind forecast uncertainty.
- It must not claim to calculate the actual electricity shortfall or recommended purchase quantity without additional validated inputs.
- If an illustrative procurement estimate is added, clearly label it as illustrative and identify the extra inputs required.

## 16. Documentation and Engineering Standards

The project documentation should cover:
- Architecture and component responsibilities.
- API contracts and data schemas.
- Data assumptions and time handling.
- Testing strategy and known edge cases.
- Git/version-control practices.
- CI/CD setup, if implemented.
- Logging and error handling.
- Performance and reliability considerations.
- Known limitations and future work.

Use precise, verifiable statements. Distinguish implemented functionality from planned work.
