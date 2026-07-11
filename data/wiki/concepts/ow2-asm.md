---
type: Concept
title: OW2 ASM
description: BSD-3-Clause Java class-file analysis and transformation framework used to build bytecode tooling and agents.
tags: [java, bytecode, instrumentation, asm, java-agent]
---

# Scope and identity

Here **ASM** means [OW2 ASM](https://asm.ow2.io/), the Java class-file analysis and manipulation framework—not AWS Secrets Manager or Datadog Application Security Management. Its official upstream is [OW2 GitLab](https://gitlab.ow2.org/asm/asm), not a GitHub mirror. ASM is BSD 3-Clause licensed and can generate new class files or transform existing ones without executing their bytecode.

# API layers

The core API is a streaming visitor model: `ClassVisitor`, `FieldVisitor`, `MethodVisitor`, and `AnnotationVisitor` receive a class-file event stream. Visitors delegate to a downstream visitor, making adapter/decorator chains the normal transformation composition technique. Adapters must preserve the required visit order and `visitEnd()` semantics.

`asm-tree` is optional. Its `ClassNode` and `MethodNode` retain a full mutable object tree, enabling random access and complex whole-method transformations; `accept(ClassVisitor)` serializes it back into a visitor pipeline. This convenience has a cost: official package documentation warns that tree transformations can take roughly twice the time of visitor transformations and increase footprint. `asm-analysis` provides `Analyzer`/interpreter/verifier facilities and per-instruction `Frame[]` data for tree methods. Use the streaming core API in load-time hot paths whenever possible.

# Standard transformation pipeline

A normal transformation is:

```text
original class bytes
  → ClassReader
  → visitor / adapter chain
  → ClassWriter
  → transformed class bytes
```

`ClassReader` parses a class file and emits visitor events. `ClassWriter` produces class-file bytes. For a transformation that mostly adds code, `new ClassWriter(reader, flags)` can reuse the original constant pool, bootstrap methods, and unchanged method bytes. Reused bytes are not recomputed by `COMPUTE_MAXS`/`COMPUTE_FRAMES`, so transformations must know which methods actually change.

Useful reader flags are `SKIP_CODE`, `SKIP_DEBUG`, `SKIP_FRAMES`, and `EXPAND_FRAMES`. When writing new frames, pairing `ClassReader.SKIP_FRAMES` with `ClassWriter.COMPUTE_FRAMES` avoids parsing frames that will be discarded. `EXPAND_FRAMES` can ease compatibility but adds compression/decompression work and is not a default performance choice.

# Frames, verification, and class loading

`COMPUTE_MAXS` calculates maximum stack/local sizes. For class-file version 1.7 and later, valid stack-map frames are also required when frames are absent or invalid; `COMPUTE_FRAMES` recalculates both frames and maxima while ignoring supplied `visitFrame` data.

Frame calculation has an important agent/container hazard. ASM's default `ClassWriter.getCommonSuperClass` can call `Class.forName(..., false, loader)` to resolve type hierarchy. In an isolated plugin class loader, OSGi/Jakarta EE deployment, or during definition of the very class being transformed, that can produce unavailable types, wrong hierarchy decisions, or unwanted loading effects. A transformation system should override it with a metadata-based resolver that does not load application classes and understands currently defining types.

`CheckClassAdapter.verify` can catch structural/data-flow errors but is not identical to the JVM verifier; test transformed bytecode on the target JDK. If a verifier loader is supplied, it may load referenced types. For untrusted input, apply input-size/resource limits and isolate/timeout parsing and analysis; ASM does not execute bytecode, but frame calculation and verification can expand the class-loading trust boundary.

# Version compatibility

ASM API levels range from stable `ASM4` through `ASM9`; `ASM10_EXPERIMENTAL` is intentionally unstable and requires preview compilation. Feature minimums matter: modules require ASM6, nestmates ASM7, records ASM8, and sealed-class permitted subclasses ASM9. A visitor with too-low an API level can throw `UnsupportedOperationException` when it sees a newer feature.

The inspected upstream master declares ASM 9.11 and Java 11 as build source/target baseline, while its opcode constants define class-file versions through Java 27 and `ClassReader` rejects versions above that range. The JDK required to run/build ASM and the class-file versions it can parse are separate compatibility questions. Align all ASM modules to one version; agent/plugin environments additionally need to account for shaded/relocated ASM and class-loader isolation.

# Role in Java agents

ASM is **not** a Java agent. Java Instrumentation owns `premain`, transformer registration, bootstrap visibility, class-loader policy, and retransformation. An agent can use ASM inside a transformer callback to implement `ClassReader → adapters → ClassWriter`. In the [Datadog Java Tracer Agent](/concepts/datadog-java-tracer-agent.md), the documented public transformation pipeline is Byte Buddy-based; treat ASM as a related lower-level mechanism rather than a configurable Datadog tracer component.

# Operational guidance

- Prefer streaming visitors, `SKIP_DEBUG`, and Writer reuse for high-volume load-time transformations.
- Limit tree/analysis/frame recomputation to classes that actually need it.
- Preserve bytecode semantics and test every target JDK/library combination.
- Keep all ASM artifacts version-aligned and avoid accidental collision with application/framework-provided ASM.
- Do not accept arbitrary class bytes without memory, CPU, and class-loader boundaries.

# Related

- [Datadog Java Tracer Agent](/concepts/datadog-java-tracer-agent.md)
- [Spring Cloud Config](/concepts/spring-cloud-config.md)

# Citations

- [Official OW2 ASM source repository](https://gitlab.ow2.org/asm/asm)
- [Official README](https://gitlab.ow2.org/asm/asm/-/blob/master/README.md)
- [BSD 3-Clause license](https://gitlab.ow2.org/asm/asm/-/blob/master/LICENSE.txt)
- [Core API package documentation](https://gitlab.ow2.org/asm/asm/-/blob/master/asm/src/main/java/org/objectweb/asm/package.html)
- [ClassReader](https://gitlab.ow2.org/asm/asm/-/blob/master/asm/src/main/java/org/objectweb/asm/ClassReader.java)
- [ClassWriter](https://gitlab.ow2.org/asm/asm/-/blob/master/asm/src/main/java/org/objectweb/asm/ClassWriter.java)
- [Tree API package documentation](https://gitlab.ow2.org/asm/asm/-/blob/master/asm-tree/src/main/java/org/objectweb/asm/tree/package.html)
- [CheckClassAdapter](https://gitlab.ow2.org/asm/asm/-/blob/master/asm-util/src/main/java/org/objectweb/asm/util/CheckClassAdapter.java)
