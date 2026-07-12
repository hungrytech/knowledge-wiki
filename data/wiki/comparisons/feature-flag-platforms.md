---
type: Comparison
title: Self-hosted feature configuration platforms
description: Decision-oriented comparison of Unleash, Flagsmith, GrowthBook, Flipt, and OpenFeature.
tags: [feature-flags, remote-config, self-hosting, experimentation]
---

# Scope

This comparison covers open-source/self-hostable control planes. Version and license terms must be verified again before deployment; in particular Flipt v1/v2 and enterprise/pro features have different terms.

# Comparison

| Platform | License / control plane | Strengths | Trade-offs / cautions | Best fit |
| --- | --- | --- | --- | --- |
| Unleash | AGPL-3.0-or-later server; Node + PostgreSQL | Mature release flags, strategies, segments, broad SDK set, local backend evaluation and Edge relay | AGPL implications for modified network service; Postgres/Edge operation; distinguish OSS from enterprise features | Product teams needing mature progressive delivery |
| Flagsmith | BSD-3-Clause; Django API/UI + PostgreSQL | Flags + typed remote config, traits/segments, identity overrides, percentage and multivariate values; broad OpenFeature support | Protect environment/client keys and identity traits; experiments require external analytics | Straightforward self-hosted flags/config |
| GrowthBook | MIT core/open-core product; MongoDB | Strong experimentation, metrics and warehouse-native analysis plus feature flags | Warehouse credentials/metrics governance are central; more data/operations scope | Teams where experiment statistics are primary |
| Flipt | Version-sensitive: verify v1/v2 license and Pro terms | Lightweight Go service, flags/segments/rollouts, GitOps-oriented workflows and OpenFeature providers | Do not assume v1 license applies to v2; lock down metrics/debug endpoints and CORS | Small teams valuing simple self-host/GitOps |
| OpenFeature | Apache-2.0 spec/API | Provider abstraction, typed evaluation/context/hooks, reduces SDK vendor coupling | Not a management UI, database, relay, or experimentation platform | Application portability layer alongside a provider |

# Decision rules

- Choose **Flagsmith** for a permissive-license, conventional self-hosted flag plus remote-config platform.
- Choose **Unleash** for a mature release-management workflow only after reviewing AGPL and feature-tier boundaries.
- Choose **GrowthBook** when experiment design, metrics, and statistical analysis are first-class requirements.
- Choose **Flipt** only after pinning the intended major version and validating its exact license/features.
- Use **OpenFeature** in application code when provider portability is worth its abstraction cost.

# Security baseline

Never expose a server/admin SDK key to browser clients. Minimize PII in evaluation context, restrict dashboard/API access with RBAC, use TLS and secret rotation, audit flag changes, and set owners/expiry dates so temporary flags are removed.

# Related

- [Feature configuration](/concepts/feature-configuration.md)
- [OpenFeature](/concepts/openfeature.md)
- [Personal Knowledge System](/projects/personal-knowledge-system.md)

# Citations

- https://github.com/Unleash/unleash
- https://docs.getunleash.io/deploy/getting-started
- https://github.com/Flagsmith/flagsmith
- https://docs.flagsmith.com/deployment-self-hosting
- https://github.com/growthbook/growthbook
- https://docs.growthbook.io/self-host
- https://github.com/flipt-io/flipt
- https://docs.flipt.io/
- https://openfeature.dev/specification/
