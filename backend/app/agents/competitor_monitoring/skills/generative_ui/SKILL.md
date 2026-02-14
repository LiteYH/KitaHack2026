---
name: generative_ui
description: Generate rich, interactive UI components to visualize competitor data beautifully. USE THIS SKILL when comparing 2+ competitors (competitor_comparison), displaying metrics/KPIs/performance data (metrics card), showing trends/time-series data (trend_chart), creating feature/pricing comparison tables (feature_table), presenting strategic insights (insight card), user asks for visual/beautiful view/chart/comparison/dashboard, or data is complex and multi-dimensional. DO NOT USE for simple text responses, when no structured data exists, or for error messages. REMEMBER to always include text context before and after UI blocks.
metadata:
  category: presentation
  priority: high
  version: "1.0"
---

## When to use this skill

Use Generative UI when:
- Presenting competitor comparison data (side-by-side comparisons)
- Displaying metrics, trends, or analytics (charts, graphs)
- Creating structured reports with multiple sections
- Showing tabular data (pricing comparisons, feature matrices)
- Building interactive dashboards or summary cards
- User explicitly requests visual or formatted output

**DO NOT USE** for:
- Simple text responses or conversational replies
- Single data points or brief updates
- Error messages or confirmations

## Available UI Components

### 1. CompetitorComparisonCard
**Use for**: Side-by-side competitor analysis

**Data Structure** (ALL FIELDS REQUIRED):
```json
{
  "type": "competitor_comparison",
  "competitors": [
    {
      "name": "Competitor Name",
      "strengths": ["strength 1", "strength 2"],
      "weaknesses": ["weakness 1", "weakness 2"],
      "pricing": "pricing info",
      "market_position": "description"
    }
  ],
  "recommendation": "Strategic recommendation text"
}
```

**IMPORTANT**: Each competitor object MUST have all 5 fields:
- `name` (string) - Company/brand name
- `strengths` (array) - Use empty array [] if none known
- `weaknesses` (array) - Use empty array [] if none known  
- `pricing` (string) - Use "N/A" or "Unknown" if not available
- `market_position` (string) - Use "Market position not available" if unknown

### 2. MetricsCard
**Use for**: Key performance indicators and metrics

**Data Structure**:
```json
{
  "type": "metrics",
  "title": "Metrics Title",
  "metrics": [
    {
      "label": "Metric Name",
      "value": "123",
      "change": "+12%",
      "trend": "up"
    }
  ],
  "period": "Last 30 days"
}
```

### 3. TrendChart
**Use for**: Time-series data and trends

**Data Structure**:
```json
{
  "type": "trend_chart",
  "title": "Chart Title",
  "data": [
    {"date": "2026-01-01", "value": 100},
    {"date": "2026-01-08", "value": 120}
  ],
  "metric_name": "Metric being tracked"
}
```

### 4. FeatureComparisonTable
**Use for**: Feature or pricing matrices

**Data Structure**:
```json
{
  "type": "feature_table",
  "title": "Feature Comparison",
  "headers": ["Feature", "Your Product", "Competitor A", "Competitor B"],
  "rows": [
    ["Feature 1", "✓", "✓", "✗"],
    ["Feature 2", "✓", "✗", "✓"]
  ]
}
```

### 5. InsightCard
**Use for**: Strategic insights and recommendations

**Data Structure**:
```json
{
  "type": "insight",
  "title": "Key Insight",
  "description": "Detailed insight explanation",
  "impact": "high|medium|low",
  "actions": ["Action 1", "Action 2"],
  "urgency": "immediate|soon|monitor"
}
```

## How to Generate UI

### Step 1: Decide if UI is appropriate
Evaluate if the response would benefit from visual formatting:
- Is the data complex or multi-dimensional?
- Would tables/charts make it clearer?
- Is there a comparison to make?
- Would the user benefit from interactive elements?

### Step 2: Choose the right component
Select from available components based on data type and use case.

### Step 3: Structure your data
Format your data according to the component's schema.

### Step 4: Signal UI generation
Include a special marker in your response to trigger UI rendering:

```
[GENUI:component_type]
{json_data}
[/GENUI]
```

### Example Usage

**User Query**: "Compare Nike and Adidas pricing strategies"

**Agent Response**:
```
Based on recent research, here's a detailed comparison:

[GENUI:competitor_comparison]
{
  "type": "competitor_comparison",
  "competitors": [
    {
      "name": "Nike",
      "strengths": ["Premium positioning", "Strong brand loyalty", "Innovation focus"],
      "weaknesses": ["Higher price points", "Limited budget options"],
      "pricing": "Premium tier ($80-$200 per item)",
      "market_position": "Market leader in athletic footwear"
    },
    {
      "name": "Adidas",
      "strengths": ["Fashion collaborations", "Sustainability focus", "Diverse range"],
      "weaknesses": ["Brand perception vs Nike", "Inconsistent pricing"],
      "pricing": "Mid to premium tier ($60-$180 per item)",
      "market_position": "Strong #2 player with fashion edge"
    }
  ],
  "recommendation": "Consider positioning between Nike's premium and Adidas's fashion-forward approach to capture the value-conscious athletic consumer."
}
[/GENUI]

Both competitors are focusing heavily on sustainability messaging in 2026, which should inform your own marketing strategy.
```

## Best Practices

1. **Always include text context**: Never use UI components alone - provide written explanation
2. **Keep data focused**: Don't overwhelm with too much information
3. **Use appropriate components**: Match component to data type
4. **Validate JSON**: Ensure JSON is properly formatted
5. **Consider mobile**: Keep designs simple and readable on small screens
6. **Accessibility**: Ensure all important info is in text too

## Limitations

- UI components render on frontend - not all clients may support them
- Always provide text fallback for key information
- Complex interactions should be saved for separate tools
- File uploads/downloads not supported via UI components
- Real-time updates require separate mechanisms

## Integration with Other Skills

GenUI works best when combined with:
- **competitor_analysis**: Visualize analysis results
- **competitor_search**: Present search findings in structured format
- **notification_management**: Create rich notification summaries

## Error Handling

If UI generation fails:
- Frontend will show text fallback
- Agent should always provide complete info in text
- Use simple markdown formatting as backup
- Log errors for debugging

## Future Enhancements (Roadmap)

- Interactive filtering and sorting
- Drill-down capabilities
- Export to PDF/Excel
- Real-time data updates
- Custom theming per user
