---
type: Concept
title: Spring AI
description: Spring-friendly Java APIs and Spring Boot integration for composing applications with AI models, vector stores, tools, and related workflows.
tags: [spring, spring-ai, java, jvm, generative-ai, rag]
resource: https://spring.io/projects/spring-ai
timestamp: '2026-07-11T23:03:47Z'
---

# Purpose

Spring AI is a Spring project for building AI-enabled applications with Spring-oriented APIs and abstractions. The official README frames its purpose as connecting enterprise data and APIs with AI models while applying portability, modularity, and strongly typed Java structures to the AI domain. [The captured upstream README](/sources/spring-ai-readme-2026-07-11.md) preserves that claim and its retrieval-time hash.

This is an application-integration framework, not an AI model service. A deployed application still needs an authenticated model provider, data sources, and an explicit policy for what actions an AI response may trigger.

# Main composition model

The project’s public surface is organized around several integration points:

- **Model APIs** provide portable synchronous and streaming access to chat, embedding, image, audio, and moderation capabilities. Provider-specific options remain available where portability is insufficient.
- **`ChatClient` and advisors** compose prompts, model calls, conversation memory, retrieval augmentation, and recurring cross-cutting patterns in application code.
- **Vector-store and document ETL APIs** connect ingestion and similarity retrieval to RAG flows. They make storage providers interchangeable at the abstraction boundary; they do not make indexing quality, metadata design, or authorization policy interchangeable.
- **Tool calling and MCP support** let a model request application-side functions or expose Spring services to AI clients. Tool execution is an application security boundary, not an automatic capability grant.
- **Spring Boot auto-configuration and starters** integrate selected model and vector-store implementations into the usual Spring configuration, dependency injection, and observability environment.

The official reference documentation is the detailed contract for individual APIs, provider modules, properties, and configuration: [Spring AI Reference](https://docs.spring.io/spring-ai/reference/).

# Common uses

Typical uses include a conversational interface over controlled business data, semantic retrieval plus response generation, structured extraction into Java objects, application-side tool invocation, and evaluation/observability around AI interactions. The README also lists pluggable conversation-memory backends and model-evaluation utilities.

These features do not establish that generated answers are correct. Retrieval quality, context limits, prompt construction, model behavior, and downstream validation remain part of the application's design.

# Spring/JVM integration

Spring AI is designed for Java/Spring applications rather than as a separate language runtime. Its Spring Boot starters and auto-configuration attach provider clients and vector stores to Boot’s normal property configuration and bean lifecycle. `ChatClient` is described by the project as a fluent model-client API analogous in style to `WebClient` and `RestClient`.

For a durable knowledge flow, a service can ingest documents through the ETL APIs, store embeddings in a selected vector store, retrieve constrained context, and invoke a chat model through the client API. [pgvector](/concepts/pgvector.md) can supply PostgreSQL vector similarity search, but it is storage infrastructure rather than a Spring AI module. The application must separately define document lifecycle, tenant isolation, citations, and fallback behavior.

# Operations, security, and compatibility boundaries

- Keep model-provider credentials in appropriate Spring configuration/secret-management mechanisms; do not put them in prompts, logs, or captured retrieval content. The exact property names and provider requirements belong to the selected version’s reference documentation.
- Treat tools and MCP-exposed actions as untrusted requests: authenticate callers where applicable, authorize each action, constrain parameters and network reach, validate outputs, and audit high-impact operations. A model deciding to call a tool must not bypass application authorization.
- Retrieval can disclose source data. Apply access control before retrieval, carry tenant/document metadata, minimize prompt context, and account for provider retention and data-residency terms separately from Spring AI.
- Metrics and traces can contain prompts, responses, identifiers, or tool arguments. Configure redaction and retention deliberately before enabling broad observability.
- Provider support does not erase provider differences: model availability, token/context limits, streaming behavior, structured-output reliability, rate limits, costs, and safety controls remain provider- and deployment-specific. Verify the selected Spring AI release against the target Spring Boot version from the release’s own documentation.

# Limits and trade-offs

Spring AI offers abstractions, not a universal portability guarantee. Using provider-specific options or tools can reduce migration ease; using only common abstractions can leave useful provider capabilities unused. RAG adds ingestion, embedding, storage, relevance, and evaluation operations. Tool calling increases usefulness but also enlarges the application’s attack surface. These are design costs, not details that a starter removes.

It also should not be confused with [OpenFeature](/concepts/openfeature.md): OpenFeature standardizes feature-flag evaluation interfaces, whereas Spring AI integrates AI-model workflows. It can coexist with configuration systems such as [Spring Cloud Config](/concepts/spring-cloud-config.md), but neither project substitutes for the other's role.

# Related

- [pgvector](/concepts/pgvector.md)
- [Spring Cloud Config](/concepts/spring-cloud-config.md)
- [OpenFeature](/concepts/openfeature.md)
- [Spring AI README capture](/sources/spring-ai-readme-2026-07-11.md)

# Official citations

- [Spring AI project page](https://spring.io/projects/spring-ai) — confirmed 2026-07-11 UTC.
- [Spring AI repository](https://github.com/spring-projects/spring-ai) and [immutable README capture](/sources/spring-ai-readme-2026-07-11.md).
- [Official Spring AI Reference](https://docs.spring.io/spring-ai/reference/) — consulted 2026-07-11 UTC.
- [Official `LICENSE.txt`](https://raw.githubusercontent.com/spring-projects/spring-ai/12d0c62ed0fa02d8a1d91c8ed55a8cf3b98e5a47/LICENSE.txt) — Apache License 2.0 text; captured 2026-07-11 UTC.
