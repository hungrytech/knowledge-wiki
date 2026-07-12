---
type: Concept
title: OpenFeature
description: Vendor-neutral feature-flag evaluation API and provider specification.
tags: [feature-flags, openfeature, sdk, portability]
---

# What it is

OpenFeature is a CNCF Incubating, vendor-neutral API and specification; it is not a flag database, dashboard, targeting engine, or self-hosted control plane. Applications call typed evaluation APIs while a Provider translates those calls to a selected flag system.

# Contract

The common evaluation types are Boolean, String, Number, and Structure/Object. `EvaluationContext` carries a `targetingKey` plus custom targeting attributes. Hooks can run around evaluation for telemetry, policy, or context enrichment. With no Provider configured, the no-op provider returns the caller's default value.

# Architecture consequence

Use OpenFeature when a project needs to reduce application-level dependency on Unleash, Flagsmith, Flipt, or GrowthBook. It does not make provider semantics identical: targeting, analytics, caching, and error behavior still require provider-specific integration tests.

# Related

- [Feature configuration](/concepts/feature-configuration.md)
- [Feature flag platform comparison](/comparisons/feature-flag-platforms.md)

# Citations

- https://openfeature.dev/
- https://openfeature.dev/specification/
- https://openfeature.dev/docs/reference/concepts/provider/
- https://github.com/open-feature/spec/blob/main/LICENSE
