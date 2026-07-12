---
type: Source
title: Spring AI README capture (2026-07-11)
description: Immutable excerpt of the official Spring AI upstream README, captured for project scope, capabilities, integration, and license provenance.
tags: [spring, spring-ai, java, ai, source]
resource: https://raw.githubusercontent.com/spring-projects/spring-ai/main/README.md
immutable_resource: https://raw.githubusercontent.com/spring-projects/spring-ai/12d0c62ed0fa02d8a1d91c8ed55a8cf3b98e5a47/README.md
captured_at: '2026-07-11T23:03:47Z'
source_hash: sha256:f21bb7741d6539fac763175d2b5848e3657639ee046203808b54c939a51e8adb
---

# Captured upstream excerpt

```markdown
# Spring AI

The Spring AI project provides a Spring-friendly API and abstractions for developing AI applications.

Its goal is to apply Spring ecosystem design principles, such as portability and modular design, to the AI domain and promote using strongly-typed data structures and APIs as the building blocks of an application.

At its core, Spring AI addresses the fundamental challenge of AI integration: connecting your enterprise Data and APIs with the AI Models.

## Getting Started

The reference documentation includes a Getting Started guide.

## Features

* Support for major AI Model providers and model types including Chat, Embedding, Text to Image, Audio Transcription, Text to Speech, and Moderation.
* Portable API support across AI providers for both synchronous and streaming options. Access to model-specific features is also available.
* Structured Outputs — Mapping of AI Model output to POJOs.
* Support for Vector Store providers and a portable API across Vector Store providers, including a metadata filter API.
* Tool Calling — Permits the model to request the execution of client-side tools and functions.
* Observability — Provides insights into AI-related operations.
* Document injection ETL framework for Data Engineering.
* AI Model Evaluation — Utilities to help evaluate generated content and protect against hallucinated response.
* ChatClient API — Fluent API for communicating with AI Chat Models.
* Advisors API — Encapsulates recurring Generative AI patterns and transforms data sent to and from Language Models.
* MCP (Model Context Protocol) support via Boot Starters and MCP Java Annotations.
* Chat Conversation Memory with pluggable persistent backends and Retrieval Augmented Generation (RAG).
* Spring Boot Auto Configuration and Starters for AI Models and Vector Stores.
```

## License provenance

The official [`LICENSE.txt`](https://raw.githubusercontent.com/spring-projects/spring-ai/12d0c62ed0fa02d8a1d91c8ed55a8cf3b98e5a47/LICENSE.txt), captured on the same date, begins with “Apache License, Version 2.0, January 2004.” Its SHA-256 at capture was `aac73b3148f6d1d7111dbca32099f68d26c644c6813ae1e4f05f6579aa2663fe`.
