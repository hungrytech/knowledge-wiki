# Knowledge Wiki

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

<p align="center"><img src="assets/wikibrain-carto/wikibrain-04d-centered-boy-wikibrain-title.png" alt="WikiBrain: 少年と親しみやすい脳のマスコットがつながった知識マップを探検する様子" width="100%" /></p>
<p align="center"><strong>再現可能なリサーチとローカルなセマンティック検索のための、Markdown ネイティブ・ローカルファースト知識システム。</strong></p>

> **状態: 初期段階ですが動作します。** OKF スタイルの Markdown が正本であり、PostgreSQL と pgvector は再構築可能な検索投影です。

## 目的

多くの個人知識ツールでは、データベース、専用エディタ、または埋め込みベンダーが正本になります。このプロジェクトでは、人間が読めて Git で管理できる Markdown を永続的な成果物とします。

- **コーパスの所有:** 概念、比較、ソースキャプチャはローカルの `data/wiki/` に保管します。リポジトリには個人の知識文書を意図的に含めません。
- **監査可能なリサーチ:** キャプチャには URL、UTC タイムスタンプ、SHA-256 provenance が保持され、解釈は根拠へリンクします。
- **ローカル検索:** API は `intfloat/multilingual-e5-small` をローカルで実行し、384 次元ベクトルを PostgreSQL/pgvector に保存します。有料 LLM/埋め込み API は不要です。
- **捨てられるインデックス:** API の再起動により Markdown からカタログを再構築できます。DB は唯一の知識コピーではありません。

## アーキテクチャ

```text
OKF Markdown ──> FastAPI cataloger ──> PostgreSQL + pgvector ──> React/Vite browser
     │                   │                       │
     │                   └── ローカル多言語埋め込み (384d)
     └── source provenance、内部リンク、可読な Git 履歴
```

| レイヤー | 役割 | 主な技術 |
| --- | --- | --- |
| `data/wiki/` | 正本の知識バンドル | Markdown + YAML frontmatter / OKF v0.1 慣例 |
| `server/` | catalog projection、URL capture、セマンティック検索 | FastAPI、Psycopg、Sentence Transformers |
| `infra/postgres/` | 検索スキーマ・ベクトルインデックス | PostgreSQL 16 + pgvector |
| `web/` | 文書・グラフ・検索ブラウザ | React、TypeScript、Vite |

## クイックスタート

### 前提条件

- Docker Desktop / Docker Compose
- ローカル開発では任意: [uv](https://docs.astral.sh/uv) と Node.js

```bash
git clone https://github.com/hungrytech/knowledge-wiki.git
cd knowledge-wiki
docker compose up -d --build
docker compose ps
curl -fsS http://localhost:8000/api/health
```

- Wiki browser: <http://localhost:5173>
- API: <http://localhost:8000/api>
- PostgreSQL: `localhost:5433`（ローカル開発専用）

最初の API 起動時に公開多言語埋め込みモデルをダウンロードし、Docker の `knowledge-models` volume に保持します。

> このリポジトリには個人の知識文書は含まれません。インストール後にローカルの `data/wiki/` に文書を作成すると、Git に無視され、この端末だけに残ります。

### セマンティック検索の確認

```bash
curl -fsS --get http://localhost:8000/api/semantic-search \
  --data-urlencode 'q=self hosted feature flags remote configuration' \
  --data-urlencode 'limit=5'
```

## 知識モデル

```text
data/wiki/
├── index.md          # 人間向けナビゲーション
├── log.md            # キュレーション履歴
├── concepts/         # 持続的な説明
├── comparisons/      # 意思決定向け分析
├── projects/         # システムと実装
└── sources/          # 不変の一次資料
```

`Source` は外部資料と provenance を保存し、`Concept` と `Comparison` は解釈を記録します。この境界により主張をレビュー可能にし、根拠を黙って書き換えることを防ぎます。

## 開発

```bash
uv run --project server pytest server/tests -q
npm --prefix web test -- --run
npm --prefix web run build
```

## プライバシーとセキュリティ

- **ローカル利用**を前提としています。API、DB ポート、Compose の認証情報を公衆インターネットへ公開しないでください。
- Compose の PostgreSQL パスワードは開発用プレースホルダーです。共有/本番環境では変更し、シークレット管理を使用してください。
- 公開 fork 前に `data/wiki/` に個人メモやライセンス制限のある内容がないか確認してください。

## ロードマップ

- [ ] heading-aware chunk の永続化
- [ ] PostgreSQL FTS + RRF hybrid retrieval
- [ ] graph/provenance ナビゲーションの改善
- [ ] import/export と corpus validation ツール
- [ ] Spring/JVM OSS リサーチの拡張

## ライセンス

このプロジェクトは [MIT License](LICENSE) で公開されています。

---

**知識は、それをインデックスするツールより長く生きるべきです。**
