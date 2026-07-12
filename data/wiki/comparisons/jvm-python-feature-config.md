---
type: Comparison
title: JVM and Python embedded feature configuration
summary: Embedded application libraries compared with centralized feature-flag control planes.
tags: [feature-flags, spring, python, django, self-hosting]
---

# Architectural distinction

Togglz, FF4J, django-waffle, and django-flags run primarily inside an application and use its database/cache/admin model. They are different from centralized multi-language control planes such as Unleash or Flagsmith. Embedded libraries reduce infrastructure for one service, but duplicate governance, flag lifecycle, and targeting behavior across services.

# JVM / Spring

| Project | License and model | Capabilities | Limits / adoption notes |
| --- | --- | --- | --- |
| Togglz | Apache-2.0; Java `FeatureManager` plus pluggable state repository and optional console | Boolean feature toggles, user activation strategy, Spring/Servlet/JUnit/CDI/Kotlin modules | Embedded per application; no official OpenFeature provider established in this research; not a central experiment platform |
| FF4J | Apache-2.0; Java framework with feature/property stores, web console and integrations | Feature toggles, typed properties, permissions/roles, audit/event model, REST/CLI-style integrations | Latest GitHub release cited by research is 2023-02-07; validate dependency compatibility and maintenance before adoption |
| LINE Flagship4j | Apache-2.0 OpenFeature/OpenFlagr client + Spring Boot starter | On/off, whitelist, canary and A/B evaluator integration | Requires OpenFlagr server; SDK is not a control plane |

# Python / Django

| Project | License and model | Targeting / rollout | Limits |
| --- | --- | --- | --- |
| django-waffle | BSD-3-Clause Django app backed by models, cache and admin | users/groups/staff/login/language and percentage/cookie rollout; Flag, Switch and random Sample | Boolean-centric; Sample is not stable experiment assignment and there is no experiment statistics system |
| django-flags | CC0/public-domain dedication with third-party exceptions; settings/DB condition sources | username, anonymous state, query parameter, URL regex, date and custom conditions | Built-ins do not provide stable percentage buckets or experiment analysis; settings-file change may require restart |
| Dynaconf | MIT application configuration loader | none: not a user-targeted flag system | Good for files/env/Vault/Redis settings, not an experiment or rollout control plane |

# Decision

Choose embedded tools for a small, single-language service where deployment simplicity wins. Choose a central plane for cross-service/multi-language targeting, remote control, audit/RBAC, stable rollout, and provider portability. Use [OpenFeature](/concepts/openfeature.md) only as an API abstraction; it cannot add missing control-plane or analytics capabilities.

# Related

- [Feature configuration](/concepts/feature-configuration.md)
- [LINE Central Dogma](/concepts/line-central-dogma.md)
- [Self-hosted feature configuration platforms](/comparisons/feature-flag-platforms.md)

# Citations

- https://github.com/togglz/togglz
- https://github.com/togglz/togglz/wiki/Architecture
- https://github.com/ff4j/ff4j
- https://github.com/django-waffle/django-waffle
- https://waffle.readthedocs.io/en/stable/
- https://github.com/cfpb/django-flags
- https://github.com/dynaconf/dynaconf
