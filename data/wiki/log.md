# Directory Update Log

## 2026-07-12

* **Bilingual presentation**: Added Korean translation extensions (`title_ko`, `description_ko`, `body_ko`) to the Markdown-first API and Korean/English detail-view selection. Full Korean and English Concept views are now curated for [Ktor](/concepts/ktor.md) and [Exposed](/concepts/exposed.md); immutable Source captures remain preserved as their English primary-source records.

## 2026-07-11

* **Research**: Added primary-source-backed Kotlin/JVM analyses for [Ktor](/concepts/ktor.md) and [Exposed](/concepts/exposed.md). The notes distinguish Ktor's coroutine/pipeline web-runtime model from Exposed's JDBC/R2DBC SQL DSL/DAO access model, make their composition boundary explicit, and preserve pinned immutable upstream README captures for both projects.

* **Research & cookbook**: Added a primary-source-backed [Spring Kafka Listener Containers](/concepts/spring-kafka-listener-containers.md) analysis and a book-style local HTML cookbook (`docs/spring-kafka-listener-container-cookbook.html`). It traces `@EnableKafka` → annotation post-processor → endpoint/registry → factory → concurrent child containers → `KafkaConsumer.poll()` → listener method, and records ack/error/transaction/rebalance/threading operation boundaries. Preserved an immutable [source capture](/sources/spring-kafka-listener-container-2026-07-11.md) pinned to upstream commit `4313f430534cea392eac569f225324c8b0849f73`.

* **Research**: Added detailed, primary-source-backed analyses of [Datadog Java Tracer Agent](/concepts/datadog-java-tracer-agent.md) (`dd-trace-java` / `dd-java-agent.jar`) and [OW2 ASM](/concepts/ow2-asm.md): instrumentation lifecycle, Byte Buddy/ASM relationship, transport/propagation, remote configuration, class-file transformation APIs, compatibility, security, and performance boundaries. Captured immutable upstream provenance records for both.

* **Research**: Added source-backed [Spring Cloud Bus](/concepts/spring-cloud-bus.md) analysis: broker-backed Spring configuration/management event propagation, Actuator endpoint and instance-addressing behavior, operational boundaries, and its distinction from a configuration store, feature-flag evaluator, and OpenFeature provider. Created immutable [upstream documentation capture](/sources/spring-cloud-bus-docs-2026-07-11.md).

* **Research**: Added source-backed Spring Cloud Config analysis: its configuration-distribution architecture, Spring Boot Config Data/client refresh model, backend/security boundaries, and distinction from OpenFeature and feature-flag/experimentation control planes. Created [upstream README capture](/sources/spring-cloud-config-readme-2026-07-11.md) and [concept](/concepts/spring-cloud-config.md).
* **Research**: Added detailed LINE/NAVER-adjacent, Spring/JVM, and Python/Django feature-configuration research, including Central Dogma, Flagship, OpenFlagr, Togglz, FF4J, django-waffle, django-flags, and Dynaconf.
* **Research**: Added cited analysis of self-hosted feature configuration platforms: Unleash, Flagsmith, GrowthBook, Flipt, and OpenFeature.
* **Retrieval design**: Added a tested Markdown heading-aware chunking primitive and reciprocal-rank-fusion ordering primitive for the pgvector-first hybrid search path.

* **Indexing**: Added local multilingual embeddings and pgvector semantic retrieval; Markdown remains the source of truth.
* **Capture**: Preserved the [Open Knowledge Format (OKF) specification](/sources/open-knowledge-format-okf.md) with URL, timestamp, and SHA-256 provenance.
* **Initialization**: Created an OKF v0.1 personal knowledge bundle and local visualization workspace.
