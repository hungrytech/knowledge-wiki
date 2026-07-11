# Knowledge Wiki

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

<p align="center"><img src="assets/knowledge-wiki-hero.svg" alt="Markdown 文档经由本地 API 流向 pgvector 搜索的 Knowledge Wiki 架构" width="100%" /></p>
<p align="center"><strong>一个以 Markdown 为原生格式、以本地优先为原则，支持可复现研究与本地语义检索的知识系统。</strong></p>

> **状态：仍在早期，但已经可用。** OKF 风格 Markdown 是权威来源；PostgreSQL 和 pgvector 是可重新构建的搜索投影。

## 为什么要做这个项目

很多个人知识工具把数据库、专有编辑器或嵌入服务商作为权威来源。本项目把人可读、可由 Git 管理的 Markdown 作为持久成果。

- **拥有语料库：** 概念、比较和源材料捕获保存在本地 `data/wiki/`。仓库有意不包含个人知识文档。
- **可审计的研究：** 捕获材料保留 URL、UTC 时间戳和 SHA-256 provenance；解释文档会链接回证据。
- **本地搜索：** API 在本地运行 `intfloat/multilingual-e5-small`，并把 384 维向量保存到 PostgreSQL/pgvector；不需要付费 LLM 或嵌入 API。
- **可丢弃的索引：** 重启 API 即可从 Markdown 重建目录。数据库从不是唯一的知识副本。

## 架构

```text
OKF Markdown ──> FastAPI cataloger ──> PostgreSQL + pgvector ──> React/Vite browser
     │                   │                       │
     │                   └── 本地多语言嵌入 (384d)
     └── source provenance、内部链接、可读的 Git 历史
```

| 层 | 作用 | 主要技术 |
| --- | --- | --- |
| `data/wiki/` | 权威知识包 | Markdown + YAML frontmatter / OKF v0.1 约定 |
| `server/` | catalog projection、URL capture、语义检索 | FastAPI、Psycopg、Sentence Transformers |
| `infra/postgres/` | 搜索模式与向量索引 | PostgreSQL 16 + pgvector |
| `web/` | 文档、图谱和搜索浏览器 | React、TypeScript、Vite |

## 快速开始

### 前置条件

- Docker Desktop / Docker Compose
- 本地开发可选：[uv](https://docs.astral.sh/uv) 和 Node.js

```bash
git clone https://github.com/hungrytech/knowledge-wiki.git
cd knowledge-wiki
docker compose up -d --build
docker compose ps
curl -fsS http://localhost:8000/api/health
```

- Wiki browser：<http://localhost:5173>
- API：<http://localhost:8000/api>
- PostgreSQL：`localhost:5433`（仅限本地开发）

API 首次启动会下载公开的多语言嵌入模型并保存在 Docker `knowledge-models` volume 中，后续启动会复用它。

> 此仓库不包含个人知识文档。安装后在本地 `data/wiki/` 中创建文档；Git 会忽略它们，因此只保留在此设备上。

### 验证语义检索

```bash
curl -fsS --get http://localhost:8000/api/semantic-search \
  --data-urlencode 'q=self hosted feature flags remote configuration' \
  --data-urlencode 'limit=5'
```

## 知识模型

```text
data/wiki/
├── index.md          # 面向人的导航
├── log.md            # 整理历史
├── concepts/         # 持久解释
├── comparisons/      # 面向决策的分析
├── projects/         # 系统与实现
└── sources/          # 不可变的原始资料
```

`Source` 保存外部材料和 provenance，`Concept` 与 `Comparison` 记录解释。保留此边界可使主张更易审查，并避免静默重写证据。

## 开发

```bash
uv run --project server pytest server/tests -q
npm --prefix web test -- --run
npm --prefix web run build
```

## 隐私与安全

- 项目面向**本地使用**。不要将 API、数据库端口或 Compose 凭据直接暴露到互联网。
- Compose PostgreSQL 密码只是开发占位符。在共享或生产部署前请替换，并使用密钥管理。
- 公开 fork 前请检查 `data/wiki/`，避免包含个人笔记或受许可证限制的材料。

## 路线图

- [ ] 持久化 heading-aware chunks
- [ ] PostgreSQL FTS + RRF hybrid retrieval
- [ ] 改进 graph/provenance 导航
- [ ] import/export 与 corpus validation 工具
- [ ] 扩展 Spring/JVM OSS 研究

## 许可证

本项目基于 [MIT License](LICENSE) 发布。

---

**你的知识应当比为它建立索引的工具活得更久。**
