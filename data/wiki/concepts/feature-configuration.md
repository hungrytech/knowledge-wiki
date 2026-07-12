---
type: Concept
title: Feature configuration and feature flags
description: Runtime configuration, progressive delivery, targeting, and experimentation control plane.
tags: [feature-flags, remote-config, experimentation, openfeature]
---

# Definition

Feature configuration is a runtime control plane that returns a typed value for a context: a Boolean release gate, a string/number/JSON configuration, or a multivariate experiment treatment. It differs from build-time configuration because a value can change without redeploying the application.

# Core evaluation model

1. A control plane stores flags, environments, rules, segments, and audit data.
2. SDKs or a relay evaluate a flag using an evaluation context such as `targetingKey`, account plan, region, app version, or traits.
3. The application must always supply a safe default and define failure behavior (cache, stale value, or default).

Typical controls are release toggles, percentage rollouts, kill switches, tenant/user targeting, typed remote configuration, and A/B experiment variations. A feature flag is not automatically an experiment: experiment analysis requires exposure logging and a metric/statistics system.

# Design and operations criteria

| Criterion | What to verify |
| --- | --- |
| Evaluation | server-side vs client-side, local cache/relay, offline/default behavior |
| Targeting | segments/traits, percentage hashing, exclusions, constraints |
| Configuration | Boolean only vs string/number/JSON/multivariate values |
| Experimentation | assignment only vs exposure and statistical analysis |
| Security | client/server key separation, PII in contexts, RBAC/audit, TLS/secrets |
| Lifecycle | owner, expiry, stale-flag cleanup, rollback/kill-switch procedure |
| Portability | [OpenFeature](/concepts/openfeature.md) provider and SDK maturity |

# Related

- [OpenFeature](/concepts/openfeature.md)
- [Feature flag platform comparison](/comparisons/feature-flag-platforms.md)

# Citations

- https://openfeature.dev/specification/
- https://docs.getunleash.io/sdks
- https://docs.flagsmith.com/integrating-with-flagsmith
- https://docs.growthbook.io/lib/build-your-own
- https://docs.flipt.io/
