---
type: Concept
title: Spring Kafka Listener Containers
summary: Spring application startup부터 @KafkaListener endpoint 등록, SmartLifecycle, concurrent consumer, poll loop, offset/error/transaction까지의 공식 코드베이스 분석.
tags: [spring-kafka, kafka, listener-container, kafka-listener, consumer, lifecycle, offset, transaction]
source:
  - https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/message-listener-container.html
  - https://github.com/spring-projects/spring-kafka/tree/4313f430534cea392eac569f225324c8b0849f73
---

# Spring Kafka Listener Containers

> 범위: Spring Kafka 공식 `main` commit `4313f430534cea392eac569f225324c8b0849f73` (2026-07-11 capture, 당시 `4.1.1-SNAPSHOT`)와 공식 Reference를 대조했다. 내부 `ListenerConsumer` 분기는 릴리스별로 변할 수 있으므로, 운영 중인 버전 tag에서 같은 클래스를 다시 확인해야 한다.

## 먼저 구분할 것

`@KafkaListener`는 Kafka consumer를 직접 만드는 annotation이 아니다. Spring bean method를 **endpoint 모델**로 바꾸고, endpoint registry가 **listener container**를 생성·시작하도록 지시하는 선언이다.

```text
Spring ApplicationContext refresh
  -> @EnableKafka infrastructure registration
  -> KafkaListenerAnnotationBeanPostProcessor scans completed beans
  -> MethodKafkaListenerEndpoint
  -> KafkaListenerEndpointRegistrar
  -> KafkaListenerEndpointRegistry (SmartLifecycle)
  -> KafkaListenerContainerFactory
  -> ConcurrentMessageListenerContainer (optional parent)
  -> KafkaMessageListenerContainer x concurrency
  -> ListenerConsumer + KafkaConsumer + poll loop
  -> MessageListener adapter -> user @KafkaListener method
```

중요한 경계는 다음과 같다.

| 경계 | 실제 책임 |
|---|---|
| `@KafkaListener` | topics, group, concurrency 등 endpoint metadata 선언 |
| endpoint/registrar | annotation metadata를 endpoint descriptor로 모으고 factory를 결정 |
| registry | container를 map에 보관하고 Spring lifecycle에 연결 |
| factory | endpoint를 `ContainerProperties` + listener adapter + concrete container로 변환 |
| container | consumer 생성, subscribe/assign, poll, dispatch, commit, pause, shutdown |
| Kafka client | group membership, partition assignment, actual `poll()`/commit protocol |

## 1. Spring 기동: `@EnableKafka`가 등록하는 것

`@EnableKafka`는 `KafkaListenerConfigurationSelector`를 import한다. selector는 `DeferredImportSelector`이며 `KafkaBootstrapConfiguration`을 늦게 가져온다. bootstrap configuration은 infrastructure bean definition으로 다음을 등록한다.

```text
KafkaListenerAnnotationBeanPostProcessor
KafkaListenerEndpointRegistry
```

이는 `@KafkaListener` 자체가 bean post processor가 아니라는 점을 보여준다. annotation을 이해하고 container를 조립하는 주체는 위 infrastructure beans다.

- [`EnableKafka.java`](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/annotation/EnableKafka.java)
- [`KafkaListenerConfigurationSelector.java`](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/annotation/KafkaListenerConfigurationSelector.java)
- [`KafkaBootstrapConfiguration.java`](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/annotation/KafkaBootstrapConfiguration.java)

## 2. bean 초기화 후 annotation → endpoint

`KafkaListenerAnnotationBeanPostProcessor` (KLABPP)의 `postProcessAfterInitialization(bean, beanName)`는 이미 만들어진 bean을 대상으로 한다.

1. `AopUtils.getTargetClass(bean)`으로 target class를 얻는다.
2. `MethodIntrospector.selectMethods(...)`로 method-level `@KafkaListener`를 찾는다. class-level annotation과 `@KafkaHandler` multi-method 모델도 별도 처리한다.
3. 각 listener method에 `processKafkaListener(...)`를 호출한다.
4. 이 메서드는 `MethodKafkaListenerEndpoint`에 target method를 넣고, annotation metadata를 endpoint로 옮긴다.

endpoint에 실리는 대표 metadata:

```text
id, groupId, topics, topicPattern, topicPartitions,
clientIdPrefix, concurrency, autoStartup,
consumerProperties, batch, filter, ackMode,
errorHandler, containerFactory, containerPostProcessor
```

factory를 annotation에서 지정하지 않으면 기본 bean name은 보통 `kafkaListenerContainerFactory`다. 이 시점에는 container가 아직 반드시 시작된 것이 아니다. registrar가 endpoint descriptor를 모은다.

## 3. singleton 완료 후 registrar → registry

KLABPP의 `afterSingletonsInstantiated()`는 모든 `KafkaListenerConfigurer`에 `configureKafkaListeners(registrar)` 기회를 준 뒤, registrar에 registry와 default container factory bean name을 연결하고 `registrar.afterPropertiesSet()`을 호출한다.

`KafkaListenerEndpointRegistrar#registerAllEndpoints()`은 endpoint마다 factory를 다음 우선순위로 해결한다.

```text
endpoint-specific factory
  -> registrar default factory
    -> default factory bean name lookup
```

그 뒤 `KafkaListenerEndpointRegistry#registerListenerContainer(endpoint, factory)`를 호출한다. 초기 bootstrap 동안에는 등록만 쌓고, registry의 SmartLifecycle start 시점에 시작된다. 반대로 context refresh 뒤 동적으로 등록한 endpoint는 기본적으로 즉시 start 경로를 탄다. `autoStartup=false`만으로 late registration이 멈춰 있다고 가정하면 안 된다. registry의 `alwaysStartAfterRefresh` 정책을 확인해야 한다.

## 4. Registry는 왜 필요한가: 일반 bean이 아닌 container lifecycle

annotation으로 만든 container는 일반 application-context bean처럼 하나씩 등록되는 모델이 아니다. `KafkaListenerEndpointRegistry`의 `listenerContainers` map이 id별로 보관하고 lifecycle을 관리한다.

`registerListenerContainer(...)`은 id 중복을 막고 `createListenerContainer(...)` 결과를 map에 넣는다. 생성 경로는 아래다.

```text
factory.createListenerContainer(endpoint)
  -> if InitializingBean: afterPropertiesSet()
  -> phase compatibility check
  -> registry map
```

registry는 `SmartLifecycle`이다.

```text
registry.start()
  -> every container: startIfNecessary(container)

startIfNecessary(container)
  -> (contextRefreshed && alwaysStartAfterRefresh)
       || container.isAutoStartup()
  -> container.start()
```

공식 문서 기준 listener container의 기본 `autoStartup`은 `true`, default phase는 `Integer.MAX_VALUE - 100`이다. 따라서 listener가 읽은 메시지를 받을 DB/cache/downstream consumer SmartLifecycle component는 더 **이른 phase**에서 준비돼야 한다. registry 내부 auto-start container들의 custom phase가 서로 다르면 phase mismatch 예외가 날 수 있다.

## 5. Factory: endpoint를 concrete container와 호출 adapter로 바꾸는 단계

`KafkaListenerContainerFactory#createListenerContainer(KafkaListenerEndpoint)`가 경계다. 일반적인 `ConcurrentKafkaListenerContainerFactory`는 endpoint의 topics, topic pattern 또는 `TopicPartitionOffset`에서 `ContainerProperties`를 만들고 `ConcurrentMessageListenerContainer`를 만든다.

공통 factory 흐름은 다음처럼 읽을 수 있다.

```text
endpoint
  -> create container
  -> set listener id / main listener id
  -> endpoint.setupListenerContainer(...)
  -> converter, error handler, interceptor, customizer 적용
  -> container
```

`MethodKafkaListenerEndpoint#createMessageListener(...)`은 record 또는 batch `MessagingMessageListenerAdapter`를 만들고, `MessageHandlerMethodFactory.createInvocableHandlerMethod(bean, method)` 결과와 연결한다. 즉 poll loop가 호출하는 `onMessage(...)`는 adapter를 거쳐 결국 사용자가 작성한 Java method를 호출한다.

## 6. Container 계층: parent concurrency와 실제 consumer

Spring Kafka는 두 concrete `MessageListenerContainer`를 제공한다.

| 클래스 | 실제 역할 |
|---|---|
| `KafkaMessageListenerContainer` (KMLC) | 하나의 `KafkaConsumer`, 하나의 consumer thread, topic/partition records 수신 |
| `ConcurrentMessageListenerContainer` (CMLC) | KMLC 하나 이상을 만들고 lifecycle/control을 집계하는 parent |

`concurrency=N`은 보통 KMLC N개, consumer N개, consumer thread N개를 의미한다. 그러나 처리 병렬성은 `min(concurrency, 실제 할당 가능한 partition)`을 넘을 수 없다.

- topics/topic pattern 구독: partition assignment는 Kafka consumer group과 assignor가 한다.
- explicit `TopicPartitionOffset`: CMLC가 child KMLC에 partition을 분배한다. concurrency가 partition 수보다 크면 낮춘다.
- 여러 topic과 기본 `RangeAssignor` 조합에서는 concurrency가 커도 idle consumer가 생길 수 있다. partition assignment strategy를 실제 topic layout과 함께 검토한다.
- 같은 partition의 records는 순서 보장을 위해 같은 consumer에서 순차 처리된다.

각 child는 `ConsumerFactory#createConsumer(...)`으로 consumer를 얻는다. `client.id` suffix와 child container name suffix는 JMX/metrics 식별에 반영된다. listener instance 하나를 여러 child thread가 공유하므로 user listener는 thread-safe하거나 stateless해야 한다. 상태가 필요하면 thread confinement/ThreadLocal cleanup/독립 container를 설계해야 한다.

## 7. `KafkaMessageListenerContainer` 시작과 consumer thread

`AbstractMessageListenerContainer#start()`는 group id, listener type, fenced state를 확인하고 subclass `doStart()`로 넘긴다.

KMLC `doStart()`의 핵심은 다음이다.

```text
listenerTaskExecutor (없으면 default executor)
  -> new ListenerConsumer(listener, listenerType, observationRegistry)
  -> setRunning(true)
  -> consumerExecutor.submitCompletable(listenerConsumer)
```

`ListenerConsumer` 생성자는 `ConsumerFactory#createConsumer(groupId, clientId, suffix, overrides)`로 Kafka client를 만들고 `subscribeOrAssignTopics(consumer)`을 수행한다.

- topics / pattern이면 `consumer.subscribe(..., rebalanceListener)`
- explicit partitions면 `consumer.assign(...)`

consumer object는 thread-safe하지 않다. `Consumer`의 pause/resume/seek/commit/rebalance control은 listener thread 또는 container가 정한 consumer-thread handoff에서 다뤄야 한다.

## 8. poll loop에서 user method까지

`ListenerConsumer#run()`은 initialize 뒤 `while (isRunning())`에서 `pollAndInvoke()`를 반복한다. 현재 main 코드의 개념적 순서는 다음과 같다.

```text
pending commit / transaction offset bookkeeping
  -> pending seek / rebalance enforcement
  -> user pause / async-ack pause state
  -> doPoll()
      -> consumer.poll(pollTimeout)
  -> invokeIfHaveRecords(records)
      -> record or batch listener dispatch
  -> resume if conditions are met
```

record listener 경로는 대략 다음이다.

```text
invokeRecordListener()
  -> doInvokeWithRecords()
    -> doInvokeRecordListener(record)
      -> invokeOnMessage(record)
        -> adapter.onMessage(record[, acknowledgment][, consumer])
          -> InvocableHandlerMethod
            -> user @KafkaListener method
```

`RecordInterceptor`는 listener 전에 record를 검사/대체할 수 있다. `null`을 반환하면 listener는 호출되지 않는다. 그러나 interceptor 안에서 consumer position 또는 committed offset을 임의로 바꾸면 container의 offset 관리와 충돌한다.

## 9. offsets: `AckMode`는 재처리 경계를 정한다

`enable.auto.commit=true`이면 Kafka client가 auto-commit한다. 컨테이너 offset 모델을 사용하려면 false가 일반적이며, Spring Kafka 2.3+는 명시하지 않으면 이를 false로 둔다. 기본 `AckMode`는 `BATCH`다.

| AckMode | 비트랜잭션에서 commit하는 시점 |
|---|---|
| `RECORD` | listener가 각 record 처리 후 정상 반환 |
| `BATCH` | 한 `poll()` 결과의 모든 record 처리 후 |
| `TIME` | batch 처리 후 `ackTime` 경과 시 |
| `COUNT` | batch 처리 후 누적 `ackCount` 충족 시 |
| `COUNT_TIME` | count 또는 time 충족 시 |
| `MANUAL` | listener `acknowledge()` 후, BATCH와 같은 timing |
| `MANUAL_IMMEDIATE` | listener thread에서 acknowledge 호출 즉시 |

`syncCommits=true`가 기본이면 `commitSync()`, false면 `commitAsync()`와 callback을 쓴다. `asyncAcks=true`는 out-of-order manual ack를 허용하지만 offset gap이 생기면 consumer를 pause하고 commit을 지연할 수 있으며, 중복 전달 위험을 바꾸고 `nack()`와 함께 쓸 수 없다.

`nack()`과 partial batch ack는 listener를 호출한 consumer thread에서만 쓸 수 있다. nack은 처리되지 않은 records를 다음 poll에서 redelivery하도록 seek하고, 지정 sleep 동안 할당 partition을 pause하면서 poll을 유지한다.

## 10. error, retry, transaction은 같은 정책으로 보지 말 것

### Non-transactional

`CommonErrorHandler`/`DefaultErrorHandler`가 일반 경계다. `DefaultErrorHandler`는 BackOff와 recoverer(DLT publish 등)를 구성할 수 있고, seek 후 재전달하거나 특정 버전에서 records를 메모리에 보관해 resubmit하는 모델을 선택할 수 있다. 무제한 retry는 poison record가 partition을 영구 정지시킬 수 있으므로 bounded retry + recoverer/DLT 정책을 명시한다.

긴 backoff가 `max.poll.interval.ms`를 위협하면 `ContainerPausingBackOffHandler`가 pause/poll/resume 방식의 대안이지만, transactions와 결합할 수 없는 제약을 확인해야 한다.

### Transactional / EOS

container에 `KafkaAwareTransactionManager`가 있으면 listener 호출 전에 transaction을 시작할 수 있다. 성공하면 offsets는 consumer commit이 아니라 `sendOffsetsToTransaction(...)`으로 transaction에 들어가고, 실패하면 rollback 및 redelivery 경로를 탄다. record listener와 batch listener의 offset semantics는 각각 RECORD/BATCH에 해당한다.

Spring Kafka 3.0+의 EOS는 `EOSMode.V2`이며 broker 2.5+가 필요하다. 여기서 exactly-once는 read-process-write의 **write**가 exactly-once라는 뜻이지, user business process 전체가 마법처럼 한 번만 실행된다는 뜻은 아니다. listener에서 별도 executor로 넘긴 일은 container transaction/consumer thread context에 자동 결합되지 않는다.

## 11. rebalance, pause, events, observation

### Rebalance

topic subscribe에서는 Kafka group coordinator가 assignment한다. `ConsumerAwareRebalanceListener`는 revoke-before-commit, revoke-after-commit, assigned, lost 경계를 제공한다. 외부 offset state/side effect 정리는 이 경계를 명시적으로 설계해야 한다.

### Pause/resume

안전한 API는 `MessageListenerContainer#pause()`/`resume()`이다. pause는 다음 poll 전에, resume은 현재 poll 반환 뒤 적용된다. pause 상태에서도 group membership을 유지하려고 poll은 계속한다. `isPauseRequested()`는 요청만, `isConsumerPaused()`는 실제 consumer pause 완료를 뜻한다.

### Events

idle event interval을 설정하면 idle/no-longer-idle 및 partition idle events를 받을 수 있다. `ConsumerStartingEvent`, `ConsumerFailedToStartEvent`, `ConsumerPausedEvent`, `ConsumerStoppedEvent`, `ConcurrentContainerStoppedEvent`는 lifecycle signal이다. 기본 event multicaster는 consumer thread에서 동기 발행하므로 handler에서 무거운 일을 하지 않는다. async multicaster라면 event의 `Consumer`를 호출하면 안 된다.

### Metrics and observation

Micrometer timer는 `spring.kafka.listener` 성공/실패 시간을 제공한다. `ContainerProperties.observationEnabled=true`로 Observation/tracing을 켜면 timer 방식과 분리해 생각해야 한다. batch record observation은 비용 및 context propagation 경계를 확인한다. tag는 low-cardinality를 유지한다.

## 12. 운영 설계 체크리스트

1. listener phase보다 먼저 DB/cache/downstream health가 준비되는가?
2. group id, topics, `missingTopicsFatal`, auth failure retry 정책이 의도적인가?
3. partition 수, concurrency, `max.poll.records`, listener p99 처리 시간, `max.poll.interval.ms`가 함께 계산됐는가?
4. listener와 deserializer instance가 concurrency에서 thread-safe한가?
5. AckMode과 error handler/DLT/transaction이 만드는 redelivery boundary를 테스트했는가?
6. non-blocking retry, blocking retry, transaction을 섞을 때 문서화된 제약을 확인했는가?
7. graceful stop에서 parent CMLC를 제어하고 rebalance/offset commit 관측을 남기는가?
8. consumer stalled/idle/auth/fenced 이벤트와 metric/trace를 alert에 연결했는가?

## Source map

- [Spring Kafka Reference — Listener Annotation](https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/listener-annotation.html)
- [Message Listener Containers](https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/message-listener-container.html)
- [Container lifecycle](https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/kafkalistener-lifecycle.html)
- [Container properties](https://docs.spring.io/spring-kafka/reference/kafka/container-props.html)
- [Error handling](https://docs.spring.io/spring-kafka/reference/kafka/annotation-error-handling.html)
- [Transactions](https://docs.spring.io/spring-kafka/reference/kafka/transactions.html)
- [Exactly once semantics](https://docs.spring.io/spring-kafka/reference/kafka/exactly-once.html)
- [Events](https://docs.spring.io/spring-kafka/reference/kafka/events.html)
- [KafkaListenerAnnotationBeanPostProcessor](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/annotation/KafkaListenerAnnotationBeanPostProcessor.java)
- [KafkaListenerEndpointRegistry](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/config/KafkaListenerEndpointRegistry.java)
- [KafkaMessageListenerContainer](https://github.com/spring-projects/spring-kafka/blob/4313f430534cea392eac569f225324c8b0849f73/spring-kafka/src/main/java/org/springframework/kafka/listener/KafkaMessageListenerContainer.java)
