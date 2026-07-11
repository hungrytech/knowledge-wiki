---
type: Concept
title: LINE Central Dogma
description: Git-backed, highly available dynamic service-configuration repository from LINE/LY Corporation.
tags: [remote-config, line, java, gitops]
---

# Role

Central Dogma is LINE's Apache-2.0 service-configuration system, not a complete feature-flag control plane. It centrally versions JSON/YAML/XML configuration, exposes REST, Java client, and CLI access, and notifies consumers so configuration can change without process restart.

# Architecture

Its documented architecture combines Git-backed history, ZooKeeper, HTTP/2, and multi-master replication. Git mirroring and pull-request review support configuration-as-code workflows. A team must define its own flag schema, targeting evaluator, identity bucketing, audit policy, and client fallback semantics on top of it.

# When it fits

Use for strongly versioned service configuration and Git review. Do not assume it supplies Unleash/Flagsmith-style segments, percentage rollout, browser SDKs, experiment measurement, or OpenFeature evaluation by itself.

# Related

- [Feature configuration](/concepts/feature-configuration.md)
- [LINE Flagship and OpenFlagr](/concepts/line-flagship-openflagr.md)
- [JVM and Python feature configuration](/comparisons/jvm-python-feature-config.md)

# Citations

- https://github.com/line/centraldogma
- https://line.github.io/centraldogma/
- https://engineering.linecorp.com/en/opensource
