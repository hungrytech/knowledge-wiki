---
type: Concept
title: Spring AMQP
description: Spring and Java support for AMQP 0.9.1 messaging, especially RabbitMQ, through templates, listener containers, administration, and Spring Boot integration.
tags: [spring, spring-amqp, amqp, rabbitmq, messaging, java, jvm]
resource: https://spring.io/projects/spring-amqp
timestamp: '2026-07-11T23:55:54Z'
---

# Purpose

Spring AMQP is the Spring project for using Java and Spring with AMQP 0.9.1, particularly RabbitMQ. The upstream README states that scope directly; its immutable capture is preserved in [Spring AMQP README capture](/sources/spring-amqp-readme-2026-07-11.md). It is a messaging integration library, not an AMQP broker: RabbitMQ (or another compatible deployment) remains a separately operated service.

# Main composition model

The official reference divides the project around application-facing and infrastructure-facing pieces:

- **`AmqpTemplate` / `RabbitTemplate`** provide synchronous request/reply and one-way send/receive operations while translating Spring message abstractions to AMQP operations.
- **Listener containers** own consumer lifecycle, broker connection/consumer coordination, message dispatch, acknowledgement behavior, concurrency, recovery, and listener invocation. `@RabbitListener` supplies an annotation-oriented endpoint model over those containers.
- **`AmqpAdmin` / `RabbitAdmin`** can declare exchanges, queues, bindings, and related broker resources from application configuration.
- **Message conversion, retry, and error handling** are composition points between an application payload and a broker delivery. They must be selected with the listener’s acknowledgement and failure policy, rather than treated as independent conveniences.

The detailed API and behavior contract belongs to the [official Spring AMQP reference](https://docs.spring.io/spring-amqp/reference/amqp.html), including its [asynchronous consumer/listener-container material](https://docs.spring.io/spring-amqp/reference/amqp/receiving-messages/async-consumer.html).

# Common uses

Use it to publish domain events or commands through exchanges and routing keys, consume work queues, integrate request/reply messaging where its failure semantics are acceptable, and declare broker topology at application startup. Spring Boot applications commonly obtain connection factories, templates, listener-container factories, conversion, and health/metrics integration through Boot’s AMQP support; the exact properties and auto-configuration behavior must be checked against the target Boot and Spring AMQP reference documentation.

A service can use Spring AMQP alongside [Spring Cloud Bus](/concepts/spring-cloud-bus.md), but the roles are different: Spring AMQP is the application-facing AMQP integration layer; Spring Cloud Bus distributes Spring configuration and management events over a selected broker binding.

# Spring/JVM integration

The project is a Java/Spring library. Its template, administration, and listener abstractions use Spring’s bean lifecycle, dependency injection, conversion, exception translation, and application-event patterns. Annotation endpoints are discovered and registered through Spring infrastructure; container factories centralize threading, acknowledgements, prefetch, conversion, retry, and error policy. This makes those policies explicit application configuration rather than code inside each consumer.

For durable handlers, keep domain processing idempotent. A broker redelivery, consumer restart, listener exception, network interruption, or acknowledgement timing can make a message observable more than once. An AMQP acknowledgment is not an atomic transaction across the broker and a database or external HTTP side effect.

# Operations, security, and compatibility boundaries

- Operate the broker separately: capacity, queue/exchange topology, disk alarms, network reachability, TLS, authentication, authorization, and upgrades are broker responsibilities. `RabbitAdmin` declaration does not replace change management for shared production topology.
- Put broker credentials and TLS material in managed configuration/secrets, restrict each application identity to the least required virtual host, exchanges, queues, and operations, and avoid logging message bodies or credentials. The project links its official [security policy](https://github.com/spring-projects/spring-amqp/security/policy) from the README.
- Bound consumer concurrency, prefetch, retries, and dead-letter/recovery handling to the downstream system’s capacity. Unbounded retry or requeue can create hot loops; a dead-letter strategy needs retention, inspection, and replay ownership.
- Treat inbound payloads as untrusted. Use deliberately restricted converters and type mappings; do not allow arbitrary remote type selection or unsafe deserialization merely for convenience.
- AMQP 0.9.1 and RabbitMQ-specific behavior are related but not identical portability promises. Confirm broker features, client compatibility, and the chosen Spring AMQP/Spring Framework/Spring Boot combination in the version-specific official reference before deployment.

# Limits and trade-offs

Spring AMQP reduces client API and lifecycle boilerplate; it does not choose a message schema, ordering model, deduplication policy, topology ownership model, or failure semantics for the application. Listener containers make concurrent consumption practical, but increase the need to reason about ordering, back pressure, poison messages, and shutdown. Request/reply over a broker may be useful for bounded integrations, but it retains distributed-systems timeout and correlation failure modes; it is not a local method call.

# Related

- [Spring Cloud Bus](/concepts/spring-cloud-bus.md)
- [Spring Cloud Config](/concepts/spring-cloud-config.md)
- [Spring OSS ecosystem catalog](/concepts/spring-oss-ecosystem.md)
- [Spring AMQP README capture](/sources/spring-amqp-readme-2026-07-11.md)

# Official citations

- [Spring AMQP project page](https://spring.io/projects/spring-amqp) — confirmed 2026-07-11 UTC.
- [Official repository](https://github.com/spring-projects/spring-amqp), [immutable README capture](/sources/spring-amqp-readme-2026-07-11.md), and [immutable upstream README](https://raw.githubusercontent.com/spring-projects/spring-amqp/90fac17abba05f8bedf7028a367ac576b5fb3ba9/README.md) — confirmed 2026-07-11 UTC.
- [Official Spring AMQP Reference](https://docs.spring.io/spring-amqp/reference/amqp.html) and [listener-container reference](https://docs.spring.io/spring-amqp/reference/amqp/receiving-messages/async-consumer.html) — consulted 2026-07-11 UTC.
- [Official `LICENSE.txt`](https://raw.githubusercontent.com/spring-projects/spring-amqp/90fac17abba05f8bedf7028a367ac576b5fb3ba9/LICENSE.txt) — Apache License 2.0 text, confirmed 2026-07-11 UTC.
