---
name: notification_management
description: "🔔 LOAD THIS for monitoring configuration! Expert guidance on: (1) Frequency selection (daily vs weekly vs custom intervals), (2) Notification level optimization (all_updates vs significant_only vs critical_only), (3) Aspect selection strategy (which competitor dimensions to track), (4) Alert fatigue prevention, (5) Configuration best practices for different business contexts. Ensures monitoring setups are valuable, not spammy."
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
