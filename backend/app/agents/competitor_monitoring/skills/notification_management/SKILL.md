---
name: notification_management
description: Configure continuous competitor monitoring with smart scheduling and notifications. USE THIS SKILL when user says monitor/track/watch/set up alerts/notify me, wants scheduled or recurring competitor updates (daily/weekly/continuous), after research when patterns suggest ongoing monitoring would be valuable, user asks about monitoring frequency/notification settings/alert preferences, or need to understand monitoring costs or scheduling options. Provides frequency recommendations (hourly to weekly), notification level guidance (always/significant_only/never), cost estimates, and setup workflow explanation.
metadata:
  category: configuration
  priority: medium
  version: "1.0"
  tools: create_monitoring_config
---

## When to use this skill

Use this skill when:
- User wants to set up continuous monitoring
- Configuring notification preferences
- Setting monitoring frequency and schedule
- Managing existing monitoring jobs

## Monitoring Configuration Guide

### Frequency Options

| Frequency  | Best for                             | Cost estimate        |
|------------|--------------------------------------|----------------------|
| Every hour | Fast-moving markets, crisis response | ~$3.60/month         |
| Every 2h   | Active monitoring, product launches  | ~$1.80/month         |
| Every 6h   | Standard monitoring                  | ~$0.60/month         |
| Every 12h  | Low-priority tracking                | ~$0.30/month         |
| Daily       | General awareness                   | ~$0.15/month         |

### Notification Preferences

- **always**: Send notification for every check (high volume)
- **significant_only**: Only notify when significance score >= 6 (recommended)
- **never**: Store results silently for later review

## Setup Flow

1. Ask user for competitor name
2. Ask what aspects to monitor (products, pricing, news, social)
3. Suggest appropriate frequency based on context
4. Confirm notification preference
5. Create monitoring config → HITL approval required
6. On approval → schedule cron job
