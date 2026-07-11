---
type: Source
title: Spring Cloud Bus documentation capture (2026-07-11)
description: Immutable excerpts from the upstream Spring Cloud Bus documentation covering broker-based propagation, endpoints, addressing, and Apache-2.0 licensing.
tags: [spring, java, remote-config, messaging, source]
resource: https://github.com/spring-cloud/spring-cloud-bus
timestamp: '2026-07-11T13:31:37Z'
source_hash: sha256:99dc1362ebbd4f5f0fc4a178c65219213e93697605e820704c9701c6eeab2c8c
---

# Captured upstream excerpts

The following excerpts were captured from the official repository documentation and release metadata listed in the citations of [Spring Cloud Bus](/concepts/spring-cloud-bus.md). They are retained as an immutable provenance record.

```asciidoc
= Introduction

Spring Cloud Bus links the nodes of a distributed system with a lightweight message
broker. This broker can then be used to broadcast state changes (such as configuration
changes) or other management instructions. A key idea is that the bus is like a
distributed actuator for a Spring Boot application that is scaled out. However, it can
also be used as a communication channel between apps. This project provides starters for
either an AMQP broker or Kafka as the transport.

= Quickstart

Spring Cloud Bus works by adding Spring Boot autconfiguration if it detects itself on the
classpath. To enable the bus, add `spring-cloud-starter-bus-amqp` or
`spring-cloud-starter-bus-kafka` to your dependency management. Spring Cloud takes care of
the rest. Make sure the broker (RabbitMQ or Kafka) is available and configured.

The `/bus*` actuator namespace has some HTTP endpoints. Currently, three are implemented.
The first, `/busenv`, sends key/value pairs to update each node's Spring Environment. The
second, `/busrefresh`, reloads each application's configuration, as though they had all
been pinged on their `/refresh` endpoint. The third `/busshutdown` sends a shutdown event
to gracefully shutdown the application instance(s).

= Bus Endpoints

Spring Cloud Bus provides three endpoints, `/actuator/busrefresh`, `/actutator/busshutdown`
and `/actuator/busenv` that correspond to individual actuator endpoints in Spring Cloud
Commons, `/actuator/refresh`, `/actuator/shutdown`, and `/actuator/env` respectively.

The `/actuator/busrefresh` endpoint clears the `RefreshScope` cache and rebinds
`@ConfigurationProperties`.

The `/actuator/busenv` endpoint updates each instances environment with the specified
key/value pair across multiple instances.

= Addressing Instances

The HTTP endpoints accept a "`destination`" path parameter, such as
`/busrefresh/customers:9000`, where `destination` is a service ID. If the ID is owned by
an instance on the bus, it processes the message, and all other instances ignore it.

Spring Cloud is released under the non-restrictive Apache 2.0 license.
```