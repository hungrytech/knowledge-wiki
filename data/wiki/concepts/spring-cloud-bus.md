---
type: Concept
title: Spring Cloud Bus
description: Apache-2.0 Spring/JVM event bus that uses a message broker to broadcast configuration and management changes across application instances.
tags: [spring, java, remote-config, messaging, kafka, rabbitmq]
resource: https://github.com/spring-cloud/spring-cloud-bus
timestamp: '2026-07-11T13:31:37Z'
---

# What it is

Spring Cloud Bus is an Apache-2.0 Spring Cloud project that connects distributed Spring Boot application nodes through a lightweight message broker. Its official documentation describes broadcast of state changes, including configuration changes, and management instructions; it supplies AMQP and Kafka starters. [The captured upstream documentation](/sources/spring-cloud-bus-docs-2026-07-11.md) is the local immutable provenance record.

At review time, the latest GitHub release was **v5.0.2** (published 2026-06-11), while the repository `main` POM declared `5.0.3-SNAPSHOT`. These are distinct version states: validate the selected Spring Cloud release train, Spring Boot compatibility, and transport binder before deployment.

# Architecture/evaluation model

The Bus uses Spring Cloud Stream and a configured binder to propagate `RemoteApplicationEvent` messages through external middleware; the documented starters are `spring-cloud-starter-bus-amqp` and `spring-cloud-starter-bus-kafka`. A destination can broadcast to all listeners or select a service/instance by its colon-separated bus ID and a path-matching destination pattern.

This is fan-out of management/configuration events, not a configuration store or a request-time flag evaluator. In the common configuration pattern, [Spring Cloud Config](/concepts/spring-cloud-config.md) remains responsible for serving external properties, while Bus distributes refresh events so participating instances refresh their eligible configuration.

# Spring/JVM integration

Adding an AMQP or Kafka Bus starter enables Spring Boot auto-configuration when the dependency is on the classpath; a reachable and configured RabbitMQ or Kafka broker is required. Broker configuration follows Spring Boot/Spring Cloud Stream conventions, and the Bus topic/destination is configurable under `spring.cloud.bus`.

The documented Actuator endpoints are `/actuator/busrefresh`, `/actuator/busenv`, and `/actuator/busshutdown`; they must be explicitly exposed through management endpoint configuration. `busrefresh` clears the `RefreshScope` cache and rebinds `@ConfigurationProperties`; `busenv` distributes a specified key/value change; `busshutdown` requests graceful shutdown. Custom messages must extend `RemoteApplicationEvent`, and both producers and consumers need the event type available for JSON deserialization.

# Targeting/config/experimentation capabilities

Bus targets topology identities (an individual instance or a service pattern), rather than an end user, tenant, cohort, or experiment assignment. The official material reviewed does not describe typed remote-value storage, audience segments, deterministic percentage bucketing, experiment exposure telemetry/analysis, or an OpenFeature provider.

It can distribute a configuration-triggered refresh or custom operational event after an application/control plane has made the decision. It therefore complements, but does not replace, [Feature configuration](/concepts/feature-configuration.md) control planes or [OpenFeature](/concepts/openfeature.md)'s vendor-neutral in-process evaluation/provider abstraction.

# Operations/security

The message broker becomes a production dependency and its credentials, network access, availability, topic isolation, retention, and authorization need an explicit deployment design; these safeguards are not asserted as bundled Bus features by the sources reviewed. Unique bus IDs are operationally important: the official addressing guide says duplicate instance IDs can prevent event processing because Bus eliminates events based on origin and queue handling.

For observability, `spring.cloud.bus.trace.enabled=true` makes sent and acknowledged bus events visible through a Spring Boot `TraceRepository` when present. Treat the Actuator endpoints as privileged management interfaces: only expose them deliberately and protect their surrounding network and Spring Boot management-security configuration according to the deployed application.

# Limitations/trade-offs

- It adds broker and event-delivery operational dependencies; it is not a standalone central configuration database or Git-backed review workflow.
- A broadcast refresh does not make application state atomically consistent: only refresh-capable bindings/scopes are affected, and handlers must tolerate delivery timing and partial rollout.
- `busenv` changes environments across instances and `busshutdown` can stop instances; endpoint exposure and caller authorization require especially careful control.
- Topology-oriented destination matching is not product/user targeting, and Bus has no documented experiment analytics or OpenFeature provider.
- The reviewed upstream state spans release v5.0.2 and `main` 5.0.3-SNAPSHOT; exact endpoint behavior and dependency compatibility must be checked against the chosen released artifacts.

# Related

- [Spring Cloud Config](/concepts/spring-cloud-config.md)
- [Feature configuration](/concepts/feature-configuration.md)
- [OpenFeature](/concepts/openfeature.md)
- [LINE Central Dogma](/concepts/line-central-dogma.md)
- [Self-hosted feature configuration platforms](/comparisons/feature-flag-platforms.md)

# Citations

- [Spring Cloud Bus repository](https://github.com/spring-cloud/spring-cloud-bus)
- [Upstream Apache License 2.0](https://raw.githubusercontent.com/spring-cloud/spring-cloud-bus/main/LICENSE.txt)
- [Official introduction source](https://raw.githubusercontent.com/spring-cloud/spring-cloud-bus/main/docs/modules/ROOT/pages/intro.adoc)
- [Official quickstart source](https://raw.githubusercontent.com/spring-cloud/spring-cloud-bus/main/docs/modules/ROOT/pages/quickstart.adoc)
- [Official endpoint source](https://raw.githubusercontent.com/spring-cloud/spring-cloud-bus/main/docs/modules/ROOT/pages/spring-cloud-bus/bus-endpoints.adoc)
- [Official addressing source](https://raw.githubusercontent.com/spring-cloud/spring-cloud-bus/main/docs/modules/ROOT/pages/spring-cloud-bus/addressing.adoc)
- [Official configuration and tracing source](https://raw.githubusercontent.com/spring-cloud/spring-cloud-bus/main/docs/modules/ROOT/pages/spring-cloud-bus/configuration.adoc)
- [GitHub v5.0.2 release](https://github.com/spring-cloud/spring-cloud-bus/releases/tag/v5.0.2)
- [Captured upstream documentation](/sources/spring-cloud-bus-docs-2026-07-11.md)