# Knowledge Wiki

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

<p align="center">
  <img src="assets/knowledge-wiki-hero.svg" alt="Markdown 문서가 로컬 API와 pgvector 검색으로 흐르는 Knowledge Wiki 구조" width="100%" />
</p>

<p align="center"><strong>재현 가능한 조사와 로컬 의미 검색을 위한, Markdown 중심·로컬 우선 지식 시스템.</strong></p>

> **상태: 초기 단계지만 작동 중입니다.** OKF 스타일 Markdown이 정본이며 PostgreSQL/pgvector는 다시 만들 수 있는 검색 인덱스입니다.

## 왜 만들었나

많은 개인 지식 도구는 데이터베이스, 전용 편집기, 또는 임베딩 벤더를 정본으로 삼습니다. 이 프로젝트는 사람이 읽고 Git으로 관리할 수 있는 Markdown을 정본으로 둡니다.

- **지식의 소유권:** 개념, 비교, 원문 캡처는 모두 `data/wiki/`에 있으며, 이 애플리케이션 없이도 활용할 수 있습니다.
- **검증 가능한 조사:** 캡처한 원문은 URL, UTC 시각, SHA-256 provenance를 보존하고 분석 문서는 근거로 연결됩니다.
- **로컬 검색:** API가 `intfloat/multilingual-e5-small`을 로컬 실행하고 PostgreSQL/pgvector에 384차원 벡터를 저장합니다. 유료 LLM·임베딩 API가 필요 없습니다.
- **폐기 가능한 인덱스:** API를 재시작하면 Markdown에서 catalog를 재구축합니다. DB가 유일한 지식 사본이 아닙니다.

## 아키텍처

```text
OKF Markdown ──> FastAPI cataloger ──> PostgreSQL + pgvector ──> React/Vite browser
     │                   │                       │
     │                   └── 로컬 다국어 임베딩 (384d)
     └── source provenance, 내부 링크, 사람이 읽을 수 있는 Git 이력
```

| 계층 | 역할 | 주요 기술 |
| --- | --- | --- |
| `data/wiki/` | 정본 지식 묶음 | Markdown + YAML frontmatter / OKF v0.1 관례 |
| `server/` | catalog projection, URL capture, 의미 검색 | FastAPI, Psycopg, Sentence Transformers |
| `infra/postgres/` | 검색 스키마·벡터 인덱스 | PostgreSQL 16 + pgvector |
| `web/` | 문서·그래프·검색 브라우저 | React, TypeScript, Vite |

## 빠른 시작

### 준비물

- Docker Desktop / Docker Compose
- 로컬 개발 시 선택: [uv](https://docs.astral.sh/uv), Node.js

```bash
git clone https://github.com/hungrytech/knowledge-wiki.git
cd knowledge-wiki
docker compose up -d --build
docker compose ps
curl -fsS http://localhost:8000/api/health
```

- Wiki browser: <http://localhost:5173>
- API: <http://localhost:8000/api>
- PostgreSQL: `localhost:5433` — 로컬 개발 전용

최초 API 실행 때 공개 다국어 임베딩 모델을 내려받아 Docker `knowledge-models` volume에 보존합니다.

### 의미 검색 확인

```bash
curl -fsS --get http://localhost:8000/api/semantic-search \
  --data-urlencode 'q=self hosted feature flags remote configuration' \
  --data-urlencode 'limit=5'
```

## 지식 모델

```text
data/wiki/
├── index.md          # 사람용 탐색
├── log.md            # 큐레이션 이력
├── concepts/         # 지속 가능한 설명
├── comparisons/      # 의사결정 중심 분석
├── projects/         # 시스템·구현
└── sources/          # 변경하지 않는 원문 근거
```

`Source`는 외부 원문과 provenance를 보관하고, `Concept`와 `Comparison`은 해석을 기록합니다. 이 경계를 유지하면 주장 검토가 쉬우며 근거를 조용히 바꾸지 않게 됩니다.

## 조사 주제

현재 저장소에는 feature/remote configuration, OpenFeature, Unleash·Flagsmith·GrowthBook·Flipt·OpenFlagr, LINE Central Dogma/Flagship, Spring Cloud Config·Togglz·FF4J, `django-waffle`·`django-flags`·Dynaconf의 1차 출처 기반 분석이 있습니다.

## 개발

```bash
uv run --project server pytest server/tests -q
npm --prefix web test -- --run
npm --prefix web run build
```

## 개인정보·보안

- 이 프로젝트는 **로컬 사용**을 목표로 합니다. API, DB 포트, Compose 자격 증명을 인터넷에 노출하지 마세요.
- Compose PostgreSQL 비밀번호는 개발용 placeholder입니다. 공유/운영 배포 전에는 변경하고 secret 관리를 사용하세요.
- 공개 fork 전에 `data/wiki/`에 개인 노트나 라이선스가 제한된 자료가 없는지 검토하세요.

## 로드맵

- [ ] heading-aware chunk 영속화
- [ ] PostgreSQL FTS + RRF hybrid retrieval
- [ ] graph/provenance 탐색 개선
- [ ] import/export 및 corpus validation 도구
- [ ] Spring/JVM OSS 조사 확장

## 라이선스

이 프로젝트는 [MIT License](LICENSE)로 배포됩니다.

---

**지식은 그것을 인덱싱하는 도구보다 오래 살아야 합니다.**
