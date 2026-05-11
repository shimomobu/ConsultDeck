# ConsultDeck アーキテクチャ設計

## 1. システム全体構成

```
User Input (CLI / YAML)
  ↓
[InputParser]
  ↓
RequirementSpec
  ↓
[TemplateSelector]  ←── [TemplateRepository]
  ↓
OutlineSpec ← [OutlineGenerator (LLM)]
  ↓
SlideSpec   ← [SlideGenerator (LLM)]
  ↓
[Reviewer (LLM)] ──→ ReviewResult (CLI出力)
  ↓
[RendererFactory]
  ├── BuiltinRenderer (python-pptx)
  └── McpRenderer (MCP Adapter)
  ↓
output/deck.pptx
```

---

## 2. モジュール一覧と責務

### 2.1 InputParser

| 項目 | 内容                                |
| -- | --------------------------------- |
| 責務 | CLI引数/YAMLを解析してRequirementSpecを生成 |
| 入力 | sys.argv / input.yaml             |
| 出力 | RequirementSpec                   |
| 依存 | なし                                |
| 制約 | バリデーションのみ。LLM呼び出しなし              |

---

### 2.2 TemplateRepository

| 項目 | 内容                                |
| -- | --------------------------------- |
| 責務 | テンプレートの永続化・CRUD操作                 |
| 入力 | template_id / TemplateSpec        |
| 出力 | TemplateSpec                      |
| 依存 | assets/templates/ ディレクトリ（YAML形式） |
| 制約 | ファイルI/Oのみ。LLM呼び出しなし              |

テンプレートはYAMLファイルとして `assets/templates/{template_id}.yaml` に格納する。

---

### 2.3 TemplateSelector

| 項目 | 内容                             |
| -- | ------------------------------ |
| 責務 | RequirementSpecからテンプレートを選択する   |
| 入力 | RequirementSpec, TemplateRepository |
| 出力 | TemplateSpec                   |
| 依存 | TemplateRepository             |
| 制約 | MVP: ルールベース選択。LLM利用しない         |

選択ロジック: `template_id` 指定あり → 直接取得。なし → `doc_type` / `audience` でマッチング。

---

### 2.4 OutlineGenerator

| 項目 | 内容                                          |
| -- | ------------------------------------------- |
| 責務 | RequirementSpec + TemplateSpec からOutlineSpecを生成 |
| 入力 | RequirementSpec, TemplateSpec               |
| 出力 | OutlineSpec                                 |
| 依存 | LlmClient                                   |
| 制約 | LLM呼び出しはLlmClient経由のみ                      |

---

### 2.5 SlideGenerator

| 項目 | 内容                                              |
| -- | ----------------------------------------------- |
| 責務 | OutlineSpec + TemplateSpec からSlideSpecを生成        |
| 入力 | OutlineSpec, TemplateSpec                       |
| 出力 | SlideSpec                                       |
| 依存 | LlmClient                                       |
| 制約 | SlideSpecの構造はTemplateのlayout_rulesに従う。PPTXを直接生成しない |

---

### 2.6 Reviewer

| 項目 | 内容                                    |
| -- | --------------------------------------- |
| 責務 | SlideSpecの品質をLLMでレビューし、ReviewResultを返す |
| 入力 | SlideSpec, RequirementSpec              |
| 出力 | ReviewResult                            |
| 依存 | LlmClient                               |
| 制約 | SlideSpecを変更しない（読み取り専用）                |

---

### 2.7 RendererFactory

| 項目 | 内容                                        |
| -- | ----------------------------------------- |
| 責務 | 設定に基づきRendererを選択して返す                     |
| 入力 | RendererConfig                            |
| 出力 | Renderer（BuiltinRenderer または McpRenderer） |
| 依存 | BuiltinRenderer, McpRenderer              |
| 制約 | Rendererの実装詳細を知らない                        |

---

### 2.8 BuiltinRenderer

| 項目 | 内容                       |
| -- | ------------------------ |
| 責務 | SlideSpecからPPTXファイルを生成する |
| 入力 | SlideSpec, TemplateSpec  |
| 出力 | output/deck.pptx         |
| 依存 | python-pptx              |
| 制約 | SlideSpec以外の情報を参照しない     |

---

### 2.9 McpRenderer

| 項目 | 内容                                 |
| -- | ---------------------------------- |
| 責務 | SlideSpecをMCP経由で外部Rendererへ委譲する   |
| 入力 | SlideSpec, McpConfig               |
| 出力 | output/deck.pptx（外部サービスからダウンロード）  |
| 依存 | McpAdapter, McpClient              |
| 制約 | フォールバック時はBuiltinRendererへ委譲する     |

---

### 2.10 McpAdapter

| 項目 | 内容                             |
| -- | ------------------------------ |
| 責務 | SlideSpecをMCP呼び出し用ペイロードへ変換する  |
| 入力 | SlideSpec                      |
| 出力 | McpPayload (dict)              |
| 依存 | なし                             |
| 制約 | シリアライズ変換のみ。ネットワーク処理なし          |

---

### 2.11 LlmClient

| 項目 | 内容                         |
| -- | -------------------------- |
| 責務 | Ollama APIへのリクエスト送信と応答取得   |
| 入力 | prompt: str, model: str    |
| 出力 | response: str              |
| 依存 | Ollama（ローカル）               |
| 制約 | GPU同時利用禁止はGpuScheduler経由で制御 |

---

### 2.12 ImageGenerator

| 項目 | 内容                              |
| -- | --------------------------------- |
| 責務 | SlideSpec.ImageSpecに基づき画像を生成する   |
| 入力 | ImageSpec（prompt, size等）         |
| 出力 | PNG file path                     |
| 依存 | AUTOMATIC1111 API                 |
| 制約 | LLM推論と同時実行禁止。ImageSpecのあるスライドのみ対象 |

---

### 2.13 GpuScheduler

| 項目 | 内容                            |
| -- | ------------------------------- |
| 責務 | GPU利用の排他制御（LLM推論 vs 画像生成の競合防止）|
| 入力 | タスク種別（llm / image）            |
| 出力 | ロック取得 / 解放                     |
| 依存 | なし（ファイルロック: filelock）          |
| 制約 | 同時GPU利用を禁止。タイムアウトで解放する         |

---

## 3. Renderer境界

```
┌─────────────────────────────────────────┐
│           Application Layer             │
│  SlideGenerator → SlideSpec            │
│  Reviewer → ReviewResult               │
└──────────────────┬──────────────────────┘
                   │ SlideSpec + TemplateSpec + output_dir
┌──────────────────▼──────────────────────┐
│         Renderer Interface              │
│  render(spec, template, output_dir) -> Path │
└──────────┬──────────────────────────────┘
           ├── BuiltinPptxRenderer (python-pptx)
           └── McpRenderer
                ├── McpAdapter (変換のみ)
                └── McpClient (HTTP / stdio)
```

**Renderer契約:**

```python
class Renderer(Protocol):
    def render(
        self,
        spec: SlideSpec,
        template: TemplateSpec,
        output_dir: Path,
    ) -> Path:
        ...
```

- RendererはSlideSpecを主入力とし、TemplateSpecの最小スタイル情報と出力先ディレクトリを受け取る
- BuiltinPptxRendererはSlide.notesをPowerPointの発表者ノートへ反映する
- python-pptx依存は`src/consultdeck/renderer/`配下に限定する
- RendererはLLM・GPU・UI・テンプレートRepositoryに依存しない
- RendererはUI・LLM・GPU制御に関与しない

---

## 4. SlideSpec責務

SlideSpecは以下の責務を持つ。

| 責務        | 内容                                |
| --------- | --------------------------------- |
| 中核データ構造   | LLM生成結果とRenderer入力の唯一の接点          |
| シリアライズ    | JSON/YAMLで保存・復元可能                 |
| バリデーション   | layout_typeとfieldの整合性を自己検証できる     |
| 変更不可      | Rendererに渡したあとSlideSpecは変更しない     |
| テンプレート非依存 | SlideSpec自体はテンプレート詳細（色・フォント）を保持しない |

SlideSpecはPydanticモデルで定義し、シリアライズ・バリデーションをライブラリに委ねる。

---

## 5. Template管理責務

| 責務     | 担当モジュール              |
| ------ | -------------------- |
| 永続化    | TemplateRepository   |
| 選択     | TemplateSelector     |
| CRUD   | TemplateRepository   |
| スキーマ定義 | TemplateSpec (Pydantic) |
| 格納場所   | assets/templates/*.yaml |

テンプレートはコードに埋め込まない。YAMLファイルとして管理し、実行時にロードする。

---

## 6. MCP Adapter責務

| 責務          | 担当モジュール              |
| ----------- | -------------------- |
| SlideSpec変換 | McpAdapter           |
| 接続・通信       | McpClient            |
| フォールバック制御   | McpRenderer          |
| 設定管理        | McpConfig (YAML)     |
| 認証情報管理      | 環境変数（os.environ）     |
| ログ出力        | McpRenderer          |

McpAdapterはネットワーク処理を持たない純粋な変換層とし、単体テストを容易にする。

---

## 7. ディレクトリ構成

```
consultdeck/
├── docs/
│   ├── 00_rfp.md
│   ├── 01_requirements.md
│   ├── 02_architecture.md
│   ├── 03_task_breakdown.md
│   └── 04_test_plan.md
├── src/
│   └── consultdeck/
│       ├── __init__.py
│       ├── models/
│       │   ├── requirement_spec.py   # RequirementSpec
│       │   ├── outline_spec.py       # OutlineSpec
│       │   ├── slide_spec.py         # SlideSpec（中核）
│       │   └── template_spec.py      # TemplateSpec
│       ├── outline/
│       │   └── builder.py            # OutlineBuilder
│       ├── slide/
│       │   └── builder.py            # SlideBuilder
│       ├── pipeline/
│       │   ├── input_parser.py       # InputParser
│       │   └── reviewer.py           # Reviewer
│       ├── template/
│       │   ├── repository.py         # TemplateRepository
│       │   └── selector.py           # TemplateSelector
│       ├── renderer/
│       │   ├── base.py               # Renderer ABC
│       │   ├── builtin_pptx_renderer.py # BuiltinPptxRenderer
│       │   ├── mcp_adapter.py        # McpAdapter
│       │   ├── mcp_renderer.py       # McpRenderer
│       │   └── factory.py            # RendererFactory
│       ├── llm/
│       │   └── client.py             # LlmClient
│       ├── image/
│       │   └── generator.py          # ImageGenerator
│       ├── gpu/
│       │   └── scheduler.py          # GpuScheduler
│       └── cli.py                    # CLIエントリポイント
├── tests/
│   ├── unit/
│   └── integration/
├── assets/
│   └── templates/
│       ├── proposal_standard.yaml
│       ├── analysis_standard.yaml
│       └── report_standard.yaml
├── output/
├── config/
│   └── settings.yaml
├── pyproject.toml
└── README.md
```

---

## 8. 設定ファイル構造

```yaml
# config/settings.yaml
renderer:
  active: builtin          # builtin | mcp
  fallback_to_builtin: true

mcp:
  endpoint: ""             # 例: http://localhost:8080
  auth_env_var: "MCP_API_KEY"
  timeout_seconds: 30

llm:
  provider: ollama
  model: gemma2:2b
  base_url: http://localhost:11434

image:
  provider: automatic1111
  base_url: http://localhost:7860
  enabled: false           # MVPでは無効

output:
  dir: ./output
```

---

## 9. 技術スタック

| 用途      | ライブラリ/ツール          |
| ------- | ------------------- |
| データモデル  | Pydantic v2         |
| PPTX生成  | python-pptx         |
| LLM通信   | httpx（Ollama API）   |
| 画像生成通信  | httpx（A1111 API）    |
| CLI     | click               |
| テスト     | pytest              |
| 設定      | PyYAML              |
| GPU排他制御 | filelock            |

---

## 10. MVPアーキテクチャスコープ

| コンポーネント          | MVP | 備考          |
| ---------------- | --- | ----------- |
| InputParser      | ○   |             |
| TemplateRepository | ○ |             |
| TemplateSelector | ○   |             |
| OutlineGenerator | ○   |             |
| SlideGenerator   | ○   |             |
| Reviewer         | ○   | 簡易版         |
| BuiltinRenderer  | ○   |             |
| RendererFactory  | ○   |             |
| McpAdapter       | △   | インタフェース定義のみ |
| McpRenderer      | △   | スタブ実装       |
| ImageGenerator   | △   | 接続確認のみ      |
| GpuScheduler     | ○   | LLM推論時のロックのみ|
| LlmClient        | ○   |             |
