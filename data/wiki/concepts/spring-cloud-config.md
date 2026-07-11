---
type: Concept
title: Spring Cloud Config
description: Apache-2.0 Spring Cloud server/client for centrally serving externalized Spring application configuration.
tags: [spring, java, remote-config, config-server, gitops]
resource: https://github.com/spring-cloud/spring-cloud-config
timestamp: '2026-07-11T03:04:14Z'
---

# What it is

Spring Cloud Config is an Apache-2.0 Spring Cloud project that exposes external configuration through an HTTP resource-based API and can be embedded in a Spring Boot application with `@EnableConfigServer`. Its upstream README describes name/value or equivalent YAML content, encryption/decryption support, and a Spring client that initializes the Spring `Environment` from remote property sources. [The captured README](/sources/spring-cloud-config-readme-2026-07-11.md) is the immutable local provenance record.

The official reference site observed on 2026-07-11 identifies its current stable documentation as **5.0.4**. Version-specific compatibility and backend availability must be checked against the selected release rather than assumed from this page.

# Architecture/evaluation model

The server implements an `EnvironmentRepository`: a request is parameterized by application, profile, and label, and the response contains ordered property sources. The official 5.0.4 documentation lists Git/version-control, filesystem, Vault, JDBC, Redis, S3, cloud-secret-manager, CredHub, MongoDB, composite, and custom repository paths; exact configuration and operational prerequisites vary by backend.

This is configuration distribution and Spring property resolution, not a per-request flag evaluator. A consuming service receives configuration at startup (or through a deliberate refresh path); application code still decides how a received property controls behavior.

# Spring/JVM integration

On the server, add the Config Server capability to a Spring Boot application and enable it with `@EnableConfigServer`. On a client, the documented default integration is Spring Boot Config Data: `spring.config.import=optional:configserver:`; removing `optional:` makes an unavailable server fail startup. A legacy bootstrap path remains documented but must be explicitly enabled.

The client supports `@RefreshScope`; the upstream README also lists Actuator management endpoints such as `/env` and `/refresh`. Refreshing configuration can reinitialize eligible beans, so teams should test consistency, idempotence, and safe defaults instead of treating a property change as an atomic distributed rollout.

# Targeting/config/experimentation capabilities

Config values can be organized by application, Spring profile, and server-side label/version. These selectors are useful for environment and service configuration, but the official sources reviewed here do not describe a built-in end-user/tenant segment engine, deterministic percentage bucketing, experiment exposure telemetry, metric analysis, or an OpenFeature provider.

Therefore Spring Cloud Config can supply a flag-like input only when an application defines the flag contract and evaluation behavior itself. It should not be conflated with [OpenFeature](/concepts/openfeature.md), which is an evaluation API/provider abstraction, or with a feature-configuration control plane that manages targeting and experiments.

# Operations/security

For production Git storage, the official server guide says to host configuration repositories on a server rather than rely on a local filesystem repository, which it describes as testing-only. The guide also warns that binary/large files can delay the first configuration request or cause server out-of-memory errors.

The security guide states that the Config Server can be secured using Spring Security/Spring Boot-supported arrangements, including HTTP Basic and OAuth2 bearer tokens; it recommends configuring and encrypting a practical password rather than relying on the generated default. The server/client documentation also covers encryption/decryption and key management. Deployment still requires concrete TLS, repository credential, authorization, secret-rotation, audit, availability, and client failure-policy decisions.

# Limitations/trade-offs

- It is Spring/JVM-centric configuration infrastructure, not a full self-hosted feature-flag or experimentation control plane.
- Client bootstrap/config import and refresh behavior add a central runtime dependency; choose fail-fast, optional import, retry, caching, and outage behavior intentionally.
- Dynamic refresh is not universal: only appropriately scoped/configured beans are refreshed, and code may need redesign to safely observe new values.
- Git-backed configuration offers reviewable history but does not by itself provide flag ownership, expiry, RBAC/audit workflow, or context targeting semantics.
- The cited official site was at 5.0.4 when reviewed; validate a deployed Spring Boot/Spring Cloud release train and backend module before adoption.

# Related

- [Feature configuration](/concepts/feature-configuration.md)
- [OpenFeature](/concepts/openfeature.md)
- [LINE Central Dogma](/concepts/line-central-dogma.md)
- [Self-hosted feature configuration platforms](/comparisons/feature-flag-platforms.md)

# Citations

- [Spring Cloud Config repository](https://github.com/spring-cloud/spring-cloud-config)
- [Upstream `LICENSE.txt` (Apache License 2.0)](https://raw.githubusercontent.com/spring-cloud/spring-cloud-config/main/LICENSE.txt)
- [Captured upstream README](/sources/spring-cloud-config-readme-2026-07-11.md)
- [Official Spring Cloud Config 5.0.4 reference](https://docs.spring.io/spring-cloud-config/reference/)
- [Official Config Server guide](https://docs.spring.io/spring-cloud-config/reference/server.html)
- [Official environment-repository guide](https://docs.spring.io/spring-cloud-config/reference/server/environment-repository.html)
- [Official Config Client guide](https://docs.spring.io/spring-cloud-config/reference/client.html)
- [Official security guide](https://docs.spring.io/spring-cloud-config/reference/server/security.html)