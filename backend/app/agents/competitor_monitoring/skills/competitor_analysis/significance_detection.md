# Significance Detection Rules

This document defines automated rules for detecting significant competitor changes.
Used by the MonitoringService to determine if findings warrant user notification.

## Scoring System

Significance score ranges from 0-100:
- **0-39**: Low significance (routine updates)
- **40-59**: Medium significance (notable changes)
- **60-79**: High significance (major strategic moves)
- **80-100**: Critical significance (industry-disrupting events)

## Detection Rules

### Product Launches (Weight: 30 points)

**Trigger Keywords:**
- launch, release, announce, unveil, introduce
- "new product", "product launch", "coming soon"
- version, v2.0, next-generation

**Modifiers:**
- Major launch (in title or first paragraph): +30 points
- Minor update (buried in content): +15 points
- Beta/preview: +10 points

**Examples:**
- "Nike announces Air Max 2026" → +30 points
- "Adidas updates app features" → +15 points

---

### Pricing Changes (Weight: 20 points)

**Trigger Keywords:**
- price, pricing, cost, discount, promotion, sale
- "price cut", "price increase", "new pricing"
- percentage off, % discount, limited time

**Modifiers:**
- Price increase mentioned: +20 points
- Discount/sale: +15 points
- Pricing strategy change: +20 points

**Examples:**
- "Spotify raises subscription price" → +20 points
- "Amazon Prime Day sale" → +15 points

---

### News Coverage (Weight: 25 points)

**Article Count:**
- 5+ articles in last 7 days: +25 points
- 3-4 articles: +15 points
- 1-2 articles: +5 points

**Source Authority (additional points):**
- Major outlets (WSJ, Bloomberg, TechCrunch): +10 points
- Industry publications: +5 points

---

### Major Events (Weight: 20 points each)

**Strategic Events:**
- acquisition, merger, acqui-hire
- partnership, collaboration, joint venture
- funding, raise, valuation, IPO

**Business Changes:**
- expansion, new market, international
- layoff, restructuring, shutdown
- leadership change, CEO, founder

**Market Impact:**
- breakthrough, innovation, patent
- award, recognition, milestone
- scandal, lawsuit, controversy, fine

**Modifiers:**
- Event in headline: +20 points
- Event in content: +15 points
- Multiple events: +10 per additional event (max +30)

**Examples:**
- "Stripe raises $6B at $50B valuation" → +20 points
- "Uber acquires Postmates competitor" → +20 points
- "Tesla CEO announces new product line" → +15 points

---

### Social Sentiment (Weight: 15 points)

**Sentiment Indicators:**
- Viral content (>10k engagements): +15 points
- Trending topic or hashtag: +10 points
- Influencer coverage: +10 points
- Customer complaints/praise: +5 points

**Note:** Social sentiment analysis requires API access to social platforms.
Currently not implemented but reserved for future enhancement.

---

## Combination Rules

### Multipliers

When multiple significant indicators are found:
- 2 indicators: 1.1x multiplier
- 3+ indicators: 1.2x multiplier

**Example:**
- Product launch (30) + News coverage (25) = 55 × 1.1 = 60.5 points

### Maximum Score

- Cap final score at 100 points
- Critical threshold (80+) indicates immediate action needed

---

## Notification Thresholds

Based on user preference and significance score:

| Preference    | Notification Trigger                           |
|---------------|-----------------------------------------------|
| Always        | Any monitoring result (score >= 0)            |
| Significant   | Score >= 50                                   |
| High Only     | Score >= 70                                   |
| Critical Only | Score >= 80                                   |
| Never         | No notifications                              |

---

## Implementation Notes

### False Positive Reduction

To avoid false positives:
1. Require keywords in title OR first 200 characters for max points
2. Reduce points for keywords buried deep in content
3. Deduplicate similar articles (check content similarity)
4. Filter out promotional spam and low-quality sources

### Recency Weighting

Recent findings are more significant:
- Content from today: 1.0x weight
- Content from 1-3 days ago: 0.9x weight
- Content from 4-7 days ago: 0.8x weight
- Content older than 7 days: 0.5x weight

### Context-Aware Scoring

Future enhancement - adjust significance based on:
- User's industry (competitor in same industry = higher significance)
- User's business size (large competitor vs small = different significance)
- Historical patterns (recurring promotions = lower significance)
- Competitive positioning (direct competitor vs tangential = different weight)

---

## Usage Example

```python
# Pseudo-code for significance detection
def calculate_significance(findings):
    score = 0
    reasons = []
    
    # Product launch check
    if has_product_keywords(findings, in_title=True):
        score += 30
        reasons.append("New product launch detected")
    
    # Pricing check
    if has_pricing_keywords(findings):
        score += 20
        reasons.append("Pricing information found")
    
    # News coverage
    article_count = count_articles(findings, days=7)
    if article_count >= 5:
        score += 25
        reasons.append(f"High news coverage ({article_count} articles)")
    
    # Major events
    events = detect_major_events(findings)
    score += len(events) * 20
    reasons.extend([f"Major event: {e}" for e in events])
    
    # Apply multiplier if multiple indicators
    if len(reasons) >= 2:
        score *= 1.1
    
    # Cap at 100
    score = min(100, score)
    
    return {
        'score': int(score),
        'is_significant': score >= 50,
        'reasons': reasons
    }
```

---

## Revision History

- v1.0 (2026-02-14): Initial rules based on Anthropic's Agent Skills specification
