---
name: competitor_search
description: Search and research competitors using Tavily Search API. Finds recent news, product launches, pricing changes, and social media activity for any given competitor or brand. Use for monitoring, tracking, and competitive intelligence gathering.
metadata:
  category: research
  version: "1.0"
  tools: search_competitor, search_competitor_news
---

## When to use this skill

Use this skill when:
- User asks to research or look up a competitor
- User wants to monitor a specific company or brand
- User asks about competitor news, product launches, or pricing
- Any request involving competitive intelligence gathering

## How to use this skill

1. **Identify the target competitor** from the user's request
2. **Determine which aspects** to research:
   - `news` — Recent news mentions and press releases
   - `products` — Product launches, updates, and feature changes
   - `pricing` — Pricing changes, promotions, and offers
   - `social` — Social media activity and sentiment
   - `general` — Broad competitive overview
3. **Execute search** using Tavily Search tool with targeted queries
4. **Summarize findings** with clear bullet points and source links

## Output Guidelines

- Always include the date/time range of findings
- Link to original sources where possible
- Highlight significant changes or developments
- Rate the significance of each finding (low / medium / high)
- If nothing notable is found, say so clearly

## Example Queries

- "Research what Nike has been doing lately"
- "Monitor Grab's pricing changes"
- "What's new with Shopee this week"
- "Track Samsung product launches"
