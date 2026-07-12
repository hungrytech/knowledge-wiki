---
type: Source
title: Ktor README capture (2026-07-11)
description: Immutable excerpt captured from the official Ktor repository README, covering framework model, hosting, coroutines, testing, and Apache-2.0 provenance.
tags: [kotlin, ktor, web, server, source]
resource: https://raw.githubusercontent.com/ktorio/ktor/79d4dbc48e75028c3a8c6152cbb6065ccbba851c/README.md
timestamp: '2026-07-11T16:45:22Z'
source_hash: sha256:2871cf48f5a72dcd39a9dae983400734eadee1417d5797d5d5ba3140cb3503a8
---

# Captured upstream excerpt

```markdown
Ktor is an asynchronous framework for creating microservices, web applications and more. Written in Kotlin from the ground up.

Ktor Framework doesn't impose a lot of constraints on what technology a project is going to use – logging, templating, messaging, persistence, serialization, dependency injection, etc. Features are installed into the application using a unified *interception* mechanism which allows building arbitrary pipelines.

Ktor Applications can be hosted in any servlet container with Servlet 3.0+ API support such as Tomcat, or standalone using Netty or Jetty. Support for other hosts can be added through the unified hosting API.

The Ktor pipeline machinery and API are utilising Kotlin coroutines to provide easy-to-use asynchronous programming model without making it too cumbersome. All host implementations are using asynchronous I/O facilities to avoid thread blocking.

Ktor applications can be hosted in a special test environment ... without actually doing any networking. Running integration tests with a real embedded web server are of course possible, too.

Ktor is an official JetBrains product and is primarily developed by the team at JetBrains, with contributions from the community.
```
