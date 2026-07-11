---
type: Source
title: Exposed README capture (2026-07-11)
description: Immutable excerpt captured from the official JetBrains Exposed repository README, covering database-access approaches, JDBC/R2DBC support, modules, and Apache-2.0 provenance.
tags: [kotlin, exposed, orm, sql, database, source]
resource: https://raw.githubusercontent.com/JetBrains/Exposed/b801a8acd3afe85b7c6ec6215d972ae525934065/README.md
timestamp: '2026-07-11T16:45:22Z'
source_hash: sha256:d2f41d1938d1b13dd75f4a7aaa9d709be9dc38495525b9ffb942778f118f25cc
---

# Captured upstream excerpt

```markdown
Exposed is a lightweight SQL library on top of a database connectivity driver for the Kotlin programming language, with support for both JDBC and R2DBC (since version 1.0.0-*) drivers. It offers two approaches for database access: a typesafe SQL-wrapping Domain-Specific Language (DSL) and a lightweight Data Access Object (DAO) API.

`exposed-core` provides foundational components and abstractions needed to work with databases in a type-safe manner and includes the DSL API.

`exposed-dao` is optional, works with the DAO API, is compatible with `exposed-jdbc`, and does not work with `exposed-r2dbc`.

`exposed-jdbc` provides JDBC support; `exposed-r2dbc` provides R2DBC support.

The listed supported databases are H2, MariaDB, MySQL, Oracle, PostgreSQL (including pgjdbc-ng), Microsoft SQL Server, and SQLite.

Exposed is an official JetBrains project; releases are available in Maven Central and contributions are licensed under Apache License, Version 2.0.
```
