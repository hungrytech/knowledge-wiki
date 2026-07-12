---
type: Concept
title: Datadog Java Tracer Agent
description: Datadog's Apache-2.0 Java APM tracer deployed as the isolated dd-java-agent JVM agent.
tags: [datadog, apm, java-agent, bytecode-instrumentation, observability]
---

# Naming and scope

The official project is [DataDog/dd-trace-java](https://github.com/DataDog/dd-trace-java), described as Datadog's Java APM client library. Its runtime Java agent artifact is **`dd-java-agent.jar`**. “dd-trace-agent” is therefore a useful informal label, but not the canonical repository or artifact name. This page concerns JVM runtime instrumentation, not Datadog Agent host/container installation.

# Deployment and architecture

The supported startup pattern places the agent in JVM options before `-jar`:

```bash
java -javaagent:/path/to/dd-java-agent.jar \
  -Ddd.service=my-app -Ddd.env=staging -Ddd.version=1.0 \
  -jar app.jar
```

The tracer documentation warns against treating the agent JAR as an ordinary application classpath dependency. At `premain`, the bootstrap code locates the agent JAR, creates an isolated class loader, then hands control to the agent. The agent installs Byte Buddy `ClassFileTransformer` instances; discovered `InstrumenterModule` implementations match target classes and methods and inject Byte Buddy `Advice` while classes load. Classes loaded through a remote `ClassLoader` are not automatically instrumented.

The distribution is a composite/shadow JAR. Internal dependencies are relocated below `datadog.` to reduce application classpath collisions. The architecture names areas such as tracing, profiling, AppSec, IAST, debugger, CI Visibility, LLM Observability, and integrations; their presence in the JAR does **not** imply every product feature is enabled.

# Tracing model and integrations

`dd-trace-core` contains the core tracing engine: `CoreTracer`, spans/contexts, pending traces, async scope handling, propagation codecs, sampling, and writers. The standard `DDAgentWriter` sends traces to a local Datadog Agent; a direct-intake writer is a separate path. `dd-trace-api` exposes public tracer APIs, while agent instrumentation uses internal `AgentTracer`/`AgentSpan` contracts. `dd-trace-ot` is a legacy OpenTracing compatibility library for manual instrumentation, not the automatic bytecode agent.

The agent documents broad web, messaging, database, and cloud-client coverage. Examples include Spring MVC/WebFlux/Boot, Servlet containers, Netty, gRPC, Kafka, JMS, RabbitMQ, JDBC, PostgreSQL, MongoDB, Redis, Elasticsearch/OpenSearch, AWS SDK, and HTTP clients. Exact availability, maturity, default enablement, framework versions, and JDK support must be checked in the [compatibility table](https://docs.datadoghq.com/tracing/trace_collection/compatibility/java/) for the deployed tracer release. `DD_INTEGRATIONS_ENABLED=false` disables integrations globally; `DD_INTEGRATION_<NAME>_ENABLED` controls an individual integration.

# Configuration, transport, and propagation

Configuration accepts both JVM properties and environment variables; system properties take precedence when both define the same setting. Unified service tags are `DD_SERVICE`, `DD_ENV`, and `DD_VERSION`. The default export path is the local Datadog Agent (`localhost:8126`); `DD_TRACE_AGENT_URL` can override host/port and supports HTTP or `unix://` UDS. Containers must explicitly validate Agent reachability and DogStatsD/JMXFetch routing.

Automatic instrumentation propagates trace context. Supported Java styles include `datadog`, W3C `tracecontext`, `b3single`, `b3multi`, `baggage`, `xray`, and `none`; legacy `b3` is deprecated. Extraction can continue, restart, or ignore an inbound context. Cross-version messaging needs testing: for example, Datadog documents disabling Kafka header propagation when pre-0.11 consumers coexist.

# Remote Configuration and control-plane implications

Datadog documents Remote Configuration as enabled by default for Java tracing and capable of changing selected tracing behavior without a JVM restart. The trace library talks to the local Datadog Agent; the Agent obtains updates over outbound HTTPS. Documented remote-managed examples include sampling, log injection, and HTTP header tags; related Datadog products can use the same delivery plane.

This is an operational control plane: keep Remote Configuration enablement, API-key permissions, Datadog RBAC, audit trail, and change monitoring under explicit governance. It is not a generic self-hosted OpenFeature provider or a substitute for a domain feature-flag control plane.

# Compatibility, performance, and security

- Do **not** co-load multiple Java agents that perform APM/tracing work; Datadog marks this unsupported. Any combination with another Byte Buddy/ASM transformer needs JDK, framework, and transformer-order testing.
- The project uses build-time **Muzzle** checks to avoid applying an integration where expected types/methods are absent. Muzzle is not a functional test and cannot prove reflection/`MethodHandle` paths safe.
- JDK, architecture, AOT, and GraalVM Native Image support are release-specific. Early-access JDKs are not supported; Native Image uses a distinct build-time path.
- Header, query-string, request-body, cloud payload, and principal tagging can expose sensitive data. Minimize tags, configure query obfuscation, and review data classification, retention, and access controls before enabling them.
- Sampling, partial flush, exclusions, and integration selection determine cost and overhead. `dd.trace.methods` is not an all-purpose profiler; use the appropriate profiling product for CPU/memory/I/O diagnosis. Restrict debug logging to incident investigation.

# Relationship to ASM and Java agents

The Datadog Java agent's documented transformation pipeline is based on **Byte Buddy**, rather than a direct public OW2 ASM API contract. Byte Buddy itself may use bytecode-level facilities internally, but this does not make OW2 ASM a user-facing configuration surface for the tracer. [OW2 ASM](/concepts/ow2-asm.md) is a lower-level class-file transformation library; Java Instrumentation lifecycle, bootstrap isolation, and retransformation policy belong to the agent/JVM layer.

# Related

- [OW2 ASM](/concepts/ow2-asm.md)
- [Spring Cloud Config](/concepts/spring-cloud-config.md)
- [OpenFeature](/concepts/openfeature.md)

# Citations

- [Datadog Java tracer repository](https://github.com/DataDog/dd-trace-java)
- [Architecture](https://github.com/DataDog/dd-trace-java/blob/master/ARCHITECTURE.md)
- [How instrumentations work](https://github.com/DataDog/dd-trace-java/blob/master/docs/how_instrumentations_work.md)
- [Java tracing setup](https://docs.datadoghq.com/tracing/trace_collection/dd_libraries/java/)
- [Java library configuration](https://docs.datadoghq.com/tracing/trace_collection/library_config/java/)
- [Java compatibility](https://docs.datadoghq.com/tracing/trace_collection/compatibility/java/)
- [Context propagation](https://docs.datadoghq.com/tracing/trace_collection/trace_context_propagation/)
- [Remote Configuration](https://docs.datadoghq.com/remote_configuration/)
