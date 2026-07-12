---
type: Concept
title: Ktor
title_ko: Ktor
description: Apache-2.0 Kotlin asynchronous framework for HTTP services, web applications, clients, and multiplatform networking.
description_ko: HTTP 서비스·웹 애플리케이션·클라이언트·멀티플랫폼 네트워킹을 위한 Apache-2.0 Kotlin 비동기 프레임워크.
body_ko: |
  # 무엇인가

  Ktor는 JetBrains가 개발한 Apache-2.0 라이선스의 Kotlin 비동기 서비스·웹 애플리케이션 프레임워크다. 공개 API는 Kotlin 우선이며 애플리케이션 파이프라인, 플러그인, 라우팅, 코루틴 기반 핸들러를 중심으로 구성된다. 검토한 저장소 근거는 [보존된 upstream README](/sources/ktor-readme-2026-07-11.md)에 남겨 두었다.

  Ktor는 서버에만 한정되지 않는다. 생태계에는 서버와 클라이언트 아티팩트가 모두 있다. 이 문서는 서버 애플리케이션 모델에 집중한다. 배포 대상에 맞는 아티팩트와 플랫폼 엔진을 선택해야 한다.

  # 아키텍처와 실행 모델

  Ktor 서버는 임베디드 서버 또는 호환되는 Servlet 3.0+ 컨테이너에서 엔진으로 호스팅된다. upstream README에는 Netty, Jetty, Servlet 컨테이너 호스팅이 명시되어 있다. 엔진·컨테이너 선택은 배포 결정이며, 애플리케이션 라우팅 결정과는 별개다.

  애플리케이션 동작은 하나의 인터셉션 파이프라인으로 조합한다. 라우팅 핸들러, 인증, 직렬화, 상태 처리, 로깅 등 횡단 관심사는 단일 영속성·DI·템플릿 스택에 강제되지 않고 플러그인/인터셉터로 추가한다. Kotlin 코루틴이 비동기 프로그래밍 모델을 제공하며, 호스트 구현체는 스레드를 막지 않기 위해 비동기 I/O를 사용한다.

  이 유연성은 작은 서비스나 비-Spring Kotlin 시스템에 유용하지만, 관례는 팀의 책임이 된다. DI, 설정, 검증, 관측성, 오류 매핑, 영속성 경계를 명시적으로 정해야 한다.

  # JVM/Kotlin 통합

  전형적인 JVM 서비스는 `io.ktor:ktor-server-netty` 같은 서버 엔진 의존성을 선언하고, 임베디드 엔진을 시작하며, 애플리케이션 모듈에 라우팅과 플러그인을 설치한다. Ktor의 Kotlin DSL은 라우트·플러그인 선언을 애플리케이션 코드 가까이에 둔다. 독립 실행형으로 배포하거나 필요하면 Servlet 컨테이너와 통합할 수 있다.

  Ktor에는 네트워크 소켓을 열지 않고 애플리케이션 호출을 검증하는 특수 인프로세스 테스트 환경이 있으며, 실제 임베디드 서버에 대한 일반 통합 테스트도 가능하다. 선택한 엔진, 프록시/TLS 동작, 타임아웃, 취소, DB·클라이언트 리소스를 별도로 시험해야 한다. 테스트 엔진이 운영 네트워크 검증을 대신하지는 않는다.

  # Exposed·Spring과의 관계

  [Exposed](/concepts/exposed.md)는 Ktor 구성 요소가 아니라 Kotlin SQL/ORM 라이브러리다. Ktor 서비스에서 함께 조합할 수 있지만, Ktor가 Exposed를 요구하지도 Exposed가 Ktor를 요구하지도 않는다. HTTP 요청 처리, 트랜잭션, DB 접근을 분리하여 트랜잭션 수명과 코루틴 디스패칭을 의도적으로 관리해야 한다.

  Ktor는 Spring Boot와도 다르다. Spring의 자동 설정과 넓은 애플리케이션 플랫폼 대신, 자유도가 높은 Kotlin 웹/런타임 기반을 제공한다. 필요하다면 Spring 통합을 채택할 수 있으나 기본 아키텍처는 아니다.

  # 운영과 대가

  - 운영 제약, 네이티브·Servlet 요구, 프로토콜 지원, 팀의 친숙도를 기준으로 엔진/컨테이너를 선택한다. 모든 엔진의 동작과 튜닝이 같다고 가정하지 않는다.
  - 코루틴 요청 경로에서 블로킹 I/O를 적절한 디스패처로 격리하지 않는 한 피한다. 코루틴 문법만으로 블로킹 DB·SDK 호출이 논블로킹이 되지는 않는다.
  - 인증, 요청 제한, 예외-응답 매핑, 구조화 로그, 트레이싱, 메트릭, 정상 종료를 위한 공통 플러그인과 정책을 일찍 확립한다.
  - Ktor의 제한된 강제 구조는 집중된 서비스를 조합할 때 장점이지만, 공유 모듈·리뷰 기준이 없으면 큰 조직에서 일관성을 낮출 수 있다.

tags: [kotlin, ktor, http, web, server, coroutines, jetbrains]
resource: https://github.com/ktorio/ktor
timestamp: '2026-07-11T16:45:22Z'
---

# What it is

Ktor is JetBrains' Apache-2.0 framework for building asynchronous Kotlin services and web applications. Its public API is Kotlin-first and centers on application pipelines, plugins, routing, and coroutine-based handlers. The [captured upstream README](/sources/ktor-readme-2026-07-11.md) preserves the reviewed repository evidence.

Ktor is not only a server: its ecosystem includes server and client artifacts. This note concentrates on the server-side application model; choose the relevant artifacts and platform engine for the deployment target.

# Architecture and execution model

A Ktor server is hosted by an engine, either as an embedded server or in a compatible Servlet 3.0+ container. The upstream README explicitly identifies Netty, Jetty, and Servlet-container hosting; engine and container selection remains a deployment decision, not an application-routing decision.

Application behavior is composed through a unified interception pipeline. Routing handlers, authentication, serialization, status handling, logging, and other cross-cutting behavior are added as plugins/interceptors rather than being imposed by a single persistence, DI, or templating stack. Kotlin coroutines provide the asynchronous programming model, while host implementations use asynchronous I/O to avoid blocking threads.

This flexibility is useful for small services and non-Spring Kotlin systems, but it makes conventions a team responsibility: choose dependency injection, configuration, validation, observability, error mapping, and persistence boundaries explicitly.

# JVM/Kotlin integration

A typical JVM service declares a server-engine dependency such as `io.ktor:ktor-server-netty`, starts an embedded engine, and installs routing/plugins in the application module. Ktor's Kotlin DSL keeps route and plugin declarations close to application code. It may be deployed standalone or integrated with a Servlet container where that is required.

Ktor has a special in-process test environment that can exercise application calls without opening a network socket, plus ordinary integration testing against a real embedded server. Test the selected engine, proxy/TLS behavior, timeouts, cancellation, and database/client resources separately; the test engine does not replace production-network coverage.

# Relationship to Exposed and Spring

[Exposed](/concepts/exposed.md) is a Kotlin SQL/ORM library, not a Ktor component. They can be composed in a Ktor service, but Ktor does not require Exposed and Exposed does not require Ktor. Keep HTTP request handling, transactions, and database access separate so that transaction lifetime and coroutine dispatching remain deliberate.

Ktor also differs from Spring Boot: it supplies an unopinionated Kotlin web/runtime foundation rather than Spring's auto-configuration and broad application platform. Spring integrations can be adopted where useful, but they are not the framework's default architecture.

# Operations and trade-offs

- Select an engine/container based on operational constraints, native/Servlet needs, protocol support, and team familiarity; do not assume every engine has identical behavior or tuning.
- Avoid blocking I/O inside coroutine request paths unless it is isolated on an appropriate dispatcher; coroutine syntax alone does not turn blocking database or SDK calls non-blocking.
- Establish common plugins and policies early for authentication, request limits, exception-to-response mapping, structured logging, tracing, metrics, and graceful shutdown.
- Ktor's limited imposed structure is a benefit when composing a focused service, but it can increase inconsistency across a large organization without shared modules and review standards.

# Related

- [Exposed](/concepts/exposed.md)
- [Spring Kafka Listener Containers](/concepts/spring-kafka-listener-containers.md)
- [Datadog Java Tracer Agent](/concepts/datadog-java-tracer-agent.md)

# Citations

- [Ktor repository](https://github.com/ktorio/ktor)
- [Pinned upstream README](/sources/ktor-readme-2026-07-11.md)
- [Official Ktor documentation](https://ktor.io/docs/)
- [Official server engines documentation](https://ktor.io/docs/server-engines.html)
- [Official testing documentation](https://ktor.io/docs/server-testing.html)
- [Upstream Apache-2.0 license](https://raw.githubusercontent.com/ktorio/ktor/main/LICENSE)
