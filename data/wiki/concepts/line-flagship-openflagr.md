---
type: Concept
title: LINE Flagship and OpenFlagr
description: LINE OpenFeature client SDKs for OpenFlagr evaluation, not an independent flag control plane.
tags: [feature-flags, line, openfeature, spring, javascript]
---

# Relationship

LINE Flagship4j and Flagshipjs are Apache-2.0 client SDK projects that connect applications to OpenFlagr/Flagr and follow OpenFeature. They are adapters/evaluation clients, not a dashboard, persistence layer, or standalone control plane.

# JVM and web integration

Flagship4j provides Java/OpenFeature libraries and Spring Boot starter modules. Its documented examples cover on/off, A/B testing, canary release, and whitelist decisions. Flagshipjs provides the corresponding JavaScript-side SDK examples. Both need an OpenFlagr evaluator endpoint and application-level timeout/default/failure policy.

# Operational judgment

This stack is useful when a Java/Spring or JavaScript application wants an OpenFeature-shaped API over OpenFlagr. Validate release cadence, endpoint resilience, and the OpenFlagr server's ownership separately; SDK maturity does not prove the backend supplies all enterprise governance controls.

# Related

- [LINE Central Dogma](/concepts/line-central-dogma.md)
- [OpenFeature](/concepts/openfeature.md)
- [Self-hosted feature configuration platforms](/comparisons/feature-flag-platforms.md)

# Citations

- https://github.com/line/Flagship4j
- https://github.com/line/Flagshipjs
- https://github.com/openflagr/flagr
