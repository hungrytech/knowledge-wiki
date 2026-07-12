---
type: Source
title: Spring Kafka listener-container reference capture (2026-07-11)
resource: https://github.com/spring-projects/spring-kafka/tree/4313f430534cea392eac569f225324c8b0849f73
captured_at: 2026-07-11T16:32:31Z
source_hash:
  readme_sha256: 5fff91d16eb354ea0229749a848fb19c31b00fb6fe82522c272493f2978e0865
  message_listener_container_sha256: 46fe9acbd4825825eb74ed1ab7a60b2cbc78f55294532461a9fef7babdca02ec
upstream_commit: 4313f430534cea392eac569f225324c8b0849f73
license: Apache-2.0
---

# Spring Kafka listener-container source capture

This immutable provenance record identifies the official materials used by [Spring Kafka Listener Containers](/concepts/spring-kafka-listener-containers.md). It records the upstream commit and complete-resource SHA-256 values; it is not a substitute for the upstream documentation.

## Captured canonical resources

| Resource | Canonical URL | SHA-256 |
|---|---|---|
| Repository README | [raw README](https://raw.githubusercontent.com/spring-projects/spring-kafka/4313f430534cea392eac569f225324c8b0849f73/README.md) | `5fff91d16eb354ea0229749a848fb19c31b00fb6fe82522c272493f2978e0865` |
| Message listener container reference | [raw AsciiDoc](https://raw.githubusercontent.com/spring-projects/spring-kafka/4313f430534cea392eac569f225324c8b0849f73/spring-kafka-docs/src/main/antora/modules/ROOT/pages/kafka/receiving-messages/message-listener-container.adoc) | `46fe9acbd4825825eb74ed1ab7a60b2cbc78f55294532461a9fef7babdca02ec` |
| Official rendered reference | [Message Listener Containers](https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/message-listener-container.html) | rendered documentation |

## Exact upstream claims used in the concept

The official listener-container reference states:

> Two `MessageListenerContainer` implementations are provided: `KafkaMessageListenerContainer` and `ConcurrentMessageListenerContainer`.

> The `KafkaMessageListenerContainer` receives all messages from all topics or partitions on a single thread. The `ConcurrentMessageListenerContainer` delegates to one or more `KafkaMessageListenerContainer` instances to provide multi-threaded consumption.

It documents that `ContainerProperties` carries topics/partitions and other configuration, that topic subscription delegates partition distribution to Kafka through `group.id`, and that explicit `TopicPartitionOffset` assignment is applied when the container starts.

It also documents these lifecycle/offset facts:

- listener containers implement `SmartLifecycle`; `autoStartup` defaults to true; default phase is `Integer.MAX_VALUE - 100`;
- `concurrency=3` creates three `KafkaMessageListenerContainer` instances;
- default non-transactional `AckMode` is `BATCH`;
- Spring Kafka sets `enable.auto.commit=false` from 2.3 unless explicitly configured;
- transactions send offsets to the transaction and use record/batch semantics according to listener type;
- `nack()` must be called on the consumer thread which invokes the listener.

## Source-code paths cited separately

Source implementation evidence is pinned to the same commit:

- [`KafkaBootstrapConfiguration.java`](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/annotation/KafkaBootstrapConfiguration.java)
- [`KafkaListenerAnnotationBeanPostProcessor.java`](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/annotation/KafkaListenerAnnotationBeanPostProcessor.java)
- [`KafkaListenerEndpointRegistry.java`](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/config/KafkaListenerEndpointRegistry.java)
- [`ConcurrentMessageListenerContainer.java`](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/listener/ConcurrentMessageListenerContainer.java)
- [`KafkaMessageListenerContainer.java`](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/listener/KafkaMessageListenerContainer.java)
