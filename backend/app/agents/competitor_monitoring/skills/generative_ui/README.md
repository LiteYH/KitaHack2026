# Generative UI Skill

This skill teaches the agent how to generate rich, interactive UI components for better data presentation.

## Components Overview

1. **CompetitorComparisonCard** - Side-by-side competitor comparisons
2. **MetricsCard** - KPIs and key metrics visualization
3. **TrendChart** - Time-series trends and historical data
4. **FeatureComparisonTable** - Feature/pricing matrices
5. **InsightCard** - Strategic insights and recommendations

## Usage Pattern

The agent uses special GENUI markers to signal UI component rendering:

```
[GENUI:component_type]
{json_data}
[/GENUI]
```

## Frontend Integration

Frontend components should:
1. Parse GENUI markers in agent responses
2. Extract JSON data
3. Render appropriate React component
4. Handle parsing errors gracefully
5. Show text fallback if component unavailable

## Development Notes

- Keep JSON schemas simple and validated
- Always provide text context around UI components
- Never rely solely on UI - text versions must be comprehensible
- Test across different screen sizes
- Ensure accessibility compliance
