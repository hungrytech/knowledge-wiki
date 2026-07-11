---
type: Source
title: Spring Cloud Config README capture (2026-07-11)
description: Immutable excerpt captured from the upstream Spring Cloud Config README, covering server/client capabilities and Apache-2.0 statement.
tags: [spring, java, remote-config, source]
resource: https://raw.githubusercontent.com/spring-cloud/spring-cloud-config/main/README.adoc
timestamp: '2026-07-11T03:04:14Z'
source_hash: sha256:a7bccadf8796bfe6af513a27eefb2552434fb0cfd0604e3fa30a2ce9774bcad0
---

# Captured upstream excerpt

```asciidoc
= Features

== Spring Cloud Config Server

Spring Cloud Config Server offers the following benefits:

* HTTP resource-based API for external configuration (name-value pairs or equivalent YAML content)
* Encrypt and decrypt property values (symmetric or asymmetric)
* Embeddable easily in a Spring Boot application using `@EnableConfigServer`

== Spring Cloud Config Client

Specifically for Spring applications, Spring Cloud Config Client lets you:

* Bind to the Config Server and initialize Spring `Environment` with remote property sources.
* Encrypt and decrypt property values (symmetric or asymmetric).
* `@RefreshScope` for Spring `@Beans` that want to be re-initialized when configuration changes.
* Use management endpoints:
** `/env` for updating `Environment` and rebinding `@ConfigurationProperties` and log levels.
** `/refresh` for refreshing the `@RefreshScope` beans.
** `/restart` for restarting the Spring context (disabled by default).
** `/pause` and `/resume` for calling the `Lifecycle` methods (`stop()` and `start()` on the `ApplicationContext`).

Spring Cloud is released under the non-restrictive Apache 2.0 license.
```
