---
type: Concept
title: Exposed
title_ko: Exposed
description: Apache-2.0 JetBrains Kotlin database library with type-safe SQL DSL and DAO APIs over JDBC and R2DBC.
description_ko: JDBC·R2DBC 위에서 타입 안전 SQL DSL과 DAO API를 제공하는 Apache-2.0 JetBrains Kotlin 데이터베이스 라이브러리.
body_ko: |
  # 무엇인가

  Exposed는 JetBrains의 Apache-2.0 Kotlin 데이터베이스 접근 라이브러리다. upstream 프로젝트는 이를 DB 연결 드라이버 위에 놓이는 경량 SQL 라이브러리로 설명하며, 타입 안전 SQL 래핑 DSL과 선택적인 경량 DAO API를 제공한다. 검토한 근거는 [보존된 upstream README](/sources/exposed-readme-2026-07-11.md)에 남겨 두었다.

  Exposed 자체는 DB 드라이버, HTTP 프레임워크, 마이그레이션 시스템이 아니다. 애플리케이션은 드라이버, 연결/풀 설정, 트랜잭션 경계, 마이그레이션 흐름, SQL 관측성, 스키마 소유권을 여전히 선택해야 한다.

  # 접근 모델과 모듈

  `exposed-core`에는 공통 추상화와 타입 안전 DSL이 들어 있다. `exposed-jdbc`는 JDBC 전송 통합을, `exposed-r2dbc`는 R2DBC 통합을 제공한다. DAO API는 선택적인 `exposed-dao` 모듈이며, upstream README는 JDBC와는 호환되지만 R2DBC와는 호환되지 않는다고 명시한다.

  저장소는 H2, MariaDB, MySQL, Oracle, PostgreSQL(pgjdbc-ng 포함), SQL Server, SQLite를 열거한다. 이는 개별 드라이버, DB 방언, 운영에서 선택한 Exposed 모듈의 버전을 검증하는 일을 대체하지 않는다.

  확장 모듈은 Java/Kotlin 날짜·시간 타입, JSON/JSONB, 마이그레이션, 암호화 열, 금액, Spring Boot/Spring 트랜잭션 통합 등을 다룬다. 코어 라이브러리만으로 모두 제공된다고 가정하지 말고, 각각을 별도 버전·호환성 표면으로 취급한다.

  # JDBC, R2DBC, 코루틴 경계

  JDBC는 블로킹 I/O다. Kotlin 코루틴 애플리케이션에서 Exposed JDBC 모듈을 사용해도 논블로킹이 되지 않는다. 블로킹 트랜잭션을 적절한 디스패처에 격리하고 연결 풀에 상한을 둔다. 관계없는 원격 호출이나 장시간 요청 스트리밍 동안 트랜잭션을 열어 두지 않는다.

  R2DBC는 고유한 모듈과 제약을 가진 별도 전송 경로다. 특히 DAO API는 `exposed-r2dbc`와 함께 사용할 수 없다. 애플리케이션의 지연시간, 동시성, 라이브러리, 트랜잭션 요구를 기준으로 DSL/DAO와 JDBC/R2DBC를 함께 고르고, 선택한 릴리스의 문서화된 동작을 검증한다.

  # Ktor·Spring과의 관계

  [Ktor](/concepts/ktor.md)는 애플리케이션/네트워크 관심사를, Exposed는 관계형 DB 접근을 맡는다. Ktor 서비스가 Exposed를 쓸 수는 있지만 서로에게 필수 프레임워크는 아니다. DB 트랜잭션 객체를 라우팅 코드에 노출하지 말고 서비스/유스케이스 경계에서 트랜잭션 범위를 정의한다.

  Exposed에는 Spring 지향 모듈도 있다. 그렇다고 Spring Data JPA의 대체재이거나 Spring을 요구한다는 뜻은 아니다. 적합한 영속성 선택은 SQL 제어, ORM 매핑 요구, 기존 생태계 통합, 운영 경험에 달려 있다.

  # 운영과 대가

  - DSL은 Kotlin 타입 안전성과 명시적인 SQL 조합을 제공하지만, 생성 SQL, 쿼리 계획, 인덱스, 잠금, 격리, N+1 패턴은 여전히 DB 수준의 관측과 검토가 필요하다.
  - DAO는 선택 사항이며 JDBC 전용이다. R2DBC나 고도로 맞춤화한 SQL이 필요한 경우 ORM 같은 사용감만을 이유로 선택하지 않는다.
  - 스키마 마이그레이션과 하위 호환 배포 방식을 독립적으로 수립한다. 테스트에 적합한 생성/삭제 헬퍼는 운영 마이그레이션 전략이 아니다.
  - 매개변수·자격 증명을 유출하지 않도록 DB 연산을 로그/트레이싱하고, 선택한 드라이버와 풀에 맞춰 쿼리/트랜잭션 타임아웃을 정한다.

tags: [kotlin, exposed, orm, sql, jdbc, r2dbc, database, jetbrains]
resource: https://github.com/JetBrains/Exposed
timestamp: '2026-07-11T16:45:22Z'
---

# What it is

Exposed is JetBrains' Apache-2.0 Kotlin database-access library. The upstream project describes it as a lightweight SQL library above a database connectivity driver, with a type-safe SQL-wrapping DSL and an optional lightweight DAO API. The [captured upstream README](/sources/exposed-readme-2026-07-11.md) preserves the reviewed evidence.

It is not a database driver, an HTTP framework, or a migration system by itself. Applications still choose a driver, connection/pool configuration, transaction boundaries, migration workflow, SQL observability, and schema ownership.

# Access models and modules

`exposed-core` contains shared abstractions and the type-safe DSL. `exposed-jdbc` supplies JDBC transport integration; `exposed-r2dbc` supplies R2DBC integration. The DAO API is an optional `exposed-dao` module, and the upstream README specifically says it is compatible with JDBC but not R2DBC.

The repository lists H2, MariaDB, MySQL, Oracle, PostgreSQL (including pgjdbc-ng), SQL Server, and SQLite. That listing is not a substitute for validating the version of an individual driver, database dialect, or Exposed module selected for production.

Extension modules cover areas such as Java/Kotlin date-time types, JSON/JSONB, migrations, encrypted columns, money, and Spring Boot/Spring transaction integration. Treat these as separately versioned compatibility surfaces rather than assuming the core library alone provides them.

# JDBC, R2DBC, and coroutine boundary

JDBC is blocking I/O. Using Exposed's JDBC module inside a Kotlin coroutine application does not make it non-blocking; isolate blocking transactions on an appropriate dispatcher and bound the connection pool. Do not keep a transaction open across unrelated remote calls or long-lived request streaming.

R2DBC is a separate transport path with its own module and limitations. In particular, the DAO API cannot be used with `exposed-r2dbc`. Select DSL/DAO and JDBC/R2DBC together from the application's latency, concurrency, library, and transaction requirements, then verify the selected release's documented behavior.

# Relationship to Ktor and Spring

[Ktor](/concepts/ktor.md) handles application/network concerns; Exposed handles relational database access. A Ktor service can use Exposed, but neither framework is mandatory for the other. Define transaction scope at the service/use-case boundary rather than exposing database transaction objects into routing code.

Exposed also offers Spring-oriented modules. That does not make it a replacement for Spring Data JPA or a Spring requirement: the appropriate persistence choice depends on SQL control, ORM mapping needs, existing ecosystem integrations, and operational familiarity.

# Operations and trade-offs

- The DSL provides Kotlin type-safety and explicit SQL composition, but generated SQL, query plans, indexes, locking, isolation, and N+1 patterns still require database-level observation and review.
- DAO is optional and JDBC-only; avoid choosing it merely for ORM-like ergonomics when the application needs R2DBC or heavily customized SQL.
- Establish schema migration and backwards-compatible deployment practices independently; create/drop helpers suitable for tests are not a production migration strategy.
- Log/trace database operations without leaking parameters or credentials, and set query/transaction timeouts according to the selected driver and pool.

# Related

- [Ktor](/concepts/ktor.md)
- [pgvector](/concepts/pgvector.md)
- [Spring Cloud Config](/concepts/spring-cloud-config.md)

# Citations

- [Exposed repository](https://github.com/JetBrains/Exposed)
- [Pinned upstream README](/sources/exposed-readme-2026-07-11.md)
- [Official Exposed documentation](https://www.jetbrains.com/help/exposed/home.html)
- [Official Exposed modules guide](https://www.jetbrains.com/help/exposed/exposed-modules.html)
- [Official Exposed transaction documentation](https://www.jetbrains.com/help/exposed/transactions.html)
- [Upstream Apache-2.0 license](https://raw.githubusercontent.com/JetBrains/Exposed/main/LICENSE.txt)
