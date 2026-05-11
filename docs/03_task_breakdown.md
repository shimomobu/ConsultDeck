# ConsultDeck タスクブレークダウン

## 開発方針

- TDD必須（テストを先に書く）
- MVPを最優先で完成させる
- 各フェーズは前フェーズの完了を前提とする
- 過剰実装禁止（タスク外の実装は行わない）

---

## Phase 0: プロジェクト基盤

### P0-1: プロジェクト初期化

| タスク   | 内容                                                          |
| ----- | ----------------------------------------------------------- |
| P0-1-1 | `pyproject.toml` 作成（pytest, pydantic, python-pptx, httpx, click, filelock, PyYAML） |
| P0-1-2 | `src/consultdeck/__init__.py` 作成                            |
| P0-1-3 | `tests/` ディレクトリ構成作成                                        |
| P0-1-4 | `.gitignore` 作成                                            |
| P0-1-5 | `config/settings.yaml` 雛形作成                                |
| P0-1-6 | `pyproject.toml` にテスト設定追加                                  |

**完了条件:** `pytest` が空の状態でパスする

---

## Phase 1: データモデル定義（SlideSpec中核）

TDDで各モデルのバリデーションテストを先行作成する。

### P1-1: RequirementSpec

| タスク   | 内容                                              |
| ----- | ------------------------------------------------- |
| P1-1-T | `tests/unit/models/test_requirement_spec.py` 作成 |
| P1-1-I | `src/consultdeck/models/requirement_spec.py` 実装  |

バリデーション対象:
- `slide_count` は1以上
- `theme` は空文字不可
- `tone` のデフォルト値は `"formal"`

---

### P1-2: OutlineSpec

| タスク   | 内容                                           |
| ----- | ---------------------------------------------- |
| P1-2-T | `tests/unit/models/test_outline_spec.py` 作成  |
| P1-2-I | `src/consultdeck/models/outline_spec.py` 実装  |

---

### P1-3: SlideSpec（中核）

| タスク   | 内容                                         |
| ----- | -------------------------------------------- |
| P1-3-T | `tests/unit/models/test_slide_spec.py` 作成  |
| P1-3-I | `src/consultdeck/models/slide_spec.py` 実装  |

バリデーション対象:
- `layout_type` は `LayoutType` enum値のみ許可
- JSON/YAMLシリアライズの往復テスト

---

### P1-4: TemplateSpec

| タスク   | 内容                                            |
| ----- | ----------------------------------------------- |
| P1-4-T | `tests/unit/models/test_template_spec.py` 作成  |
| P1-4-I | `src/consultdeck/models/template_spec.py` 実装  |

---

**Phase 1完了条件:** 全モデルのユニットテストがパス

---

## Phase 2: テンプレート管理

### P2-1: 初期テンプレートYAML作成

| タスク   | 内容                                            |
| ----- | ----------------------------------------------- |
| P2-1-1 | `assets/templates/proposal_standard.yaml` 作成  |
| P2-1-2 | `assets/templates/analysis_standard.yaml` 作成  |
| P2-1-3 | `assets/templates/report_standard.yaml` 作成    |

---

### P2-2: TemplateRepository

| タスク   | 内容                                                  |
| ----- | ----------------------------------------------------- |
| P2-2-T | `tests/unit/template/test_repository.py` 作成（tmpdir使用）|
| P2-2-I | `src/consultdeck/template/repository.py` 実装          |

テスト対象:
- `get(template_id)` → TemplateSpec返却
- 存在しないIDで `TemplateNotFoundError`
- YAMLパースエラー時の例外

---

### P2-3: TemplateSelector

| タスク   | 内容                                              |
| ----- | ------------------------------------------------- |
| P2-3-T | `tests/unit/template/test_selector.py` 作成        |
| P2-3-I | `src/consultdeck/template/selector.py` 実装         |

テスト対象:
- `template_id` 指定時は直接取得
- 未指定時は `doc_type` でマッチング
- マッチなし時はデフォルト（`proposal_standard`）

---

**Phase 2完了条件:** テンプレート3種のロード・選択テストがパス

---

## Phase 3: LLMクライアント

### P3-1: LlmClient

| タスク   | 内容                                           |
| ----- | ---------------------------------------------- |
| P3-1-T | `tests/unit/llm/test_client.py` 作成（HTTPXモック） |
| P3-1-I | `src/consultdeck/llm/client.py` 実装            |

テスト対象:
- 正常レスポンス取得
- タイムアウト時の例外 `LlmTimeoutError`
- 接続失敗時の例外 `LlmConnectionError`

---

### P3-2: GpuScheduler

| タスク   | 内容                                            |
| ----- | ----------------------------------------------- |
| P3-2-T | `tests/unit/gpu/test_scheduler.py` 作成          |
| P3-2-I | `src/consultdeck/gpu/scheduler.py` 実装（filelock）|

テスト対象:
- ロック取得・解放
- タイムアウトで `GpuLockTimeoutError`

---

**Phase 3完了条件:** LlmClientのモックテストとGpuSchedulerテストがパス

---

## Phase 4: パイプライン実装

### P4-1: InputParser

| タスク   | 内容                                            |
| ----- | ----------------------------------------------- |
| P4-1-T | `tests/unit/pipeline/test_input_parser.py` 作成  |
| P4-1-I | `src/consultdeck/pipeline/input_parser.py` 実装  |

テスト対象:
- CLI引数のパース
- YAMLファイルのパース
- 必須フィールド欠損時のエラー

---

### P4-2: OutlineGenerator

| タスク   | 内容                                                 |
| ----- | ---------------------------------------------------- |
| P4-2-T | `tests/unit/pipeline/test_outline_generator.py` 作成 |
| P4-2-I | `src/consultdeck/pipeline/outline_generator.py` 実装 |

テスト対象:
- LlmClientをモックしてOutlineSpecが生成されること
- LLMレスポンスのJSONパース失敗時のリトライ/例外

---

### P4-3: SlideGenerator

| タスク   | 内容                                                |
| ----- | --------------------------------------------------- |
| P4-3-T | `tests/unit/pipeline/test_slide_generator.py` 作成  |
| P4-3-I | `src/consultdeck/pipeline/slide_generator.py` 実装  |

テスト対象:
- LlmClientをモックしてSlideSpecが生成されること
- slide_count通りのスライド数が生成されること
- SlideSpecバリデーションが通ること

---

### P4-4: Reviewer

| タスク   | 内容                                          |
| ----- | --------------------------------------------- |
| P4-4-T | `tests/unit/pipeline/test_reviewer.py` 作成    |
| P4-4-I | `src/consultdeck/pipeline/reviewer.py` 実装    |

テスト対象:
- LlmClientをモックしてReviewResultが返ること
- ReviewResultの構造検証（項目・スコア・コメント）

---

**Phase 4完了条件:** パイプライン全コンポーネントのユニットテストがパス

---

## Phase 5: Renderer実装

### P5-1: Renderer ABC

| タスク   | 内容                                          |
| ----- | --------------------------------------------- |
| P5-1-I | `src/consultdeck/renderer/base.py` 実装（ABC定義）|

---

### P5-2: BuiltinRenderer

| タスク   | 内容                                                 |
| ----- | ---------------------------------------------------- |
| P5-2-T | `tests/unit/renderer/test_builtin_renderer.py` 作成  |
| P5-2-I | `src/consultdeck/renderer/builtin_renderer.py` 実装  |

テスト対象:
- SlideSpecからPPTXファイルが生成されること
- 出力ファイルが `.pptx` であること
- スライド枚数がSlideSpecと一致すること
- タイトル・本文・メモが埋め込まれること

---

### P5-3: McpAdapter（変換層のみ）

| タスク   | 内容                                               |
| ----- | -------------------------------------------------- |
| P5-3-T | `tests/unit/renderer/test_mcp_adapter.py` 作成（変換テスト）|
| P5-3-I | `src/consultdeck/renderer/mcp_adapter.py` 実装（変換のみ）|

テスト対象:
- SlideSpec → McpPayload変換
- フィールドマッピングの正確性

---

### P5-4: McpRenderer（スタブ）

| タスク   | 内容                                              |
| ----- | ------------------------------------------------- |
| P5-4-T | `tests/unit/renderer/test_mcp_renderer.py` 作成   |
| P5-4-I | `src/consultdeck/renderer/mcp_renderer.py` 実装（スタブ）|

テスト対象:
- MCP接続失敗時にBuiltinRendererへフォールバックすること

---

### P5-5: RendererFactory

| タスク   | 内容                                            |
| ----- | ----------------------------------------------- |
| P5-5-T | `tests/unit/renderer/test_factory.py` 作成       |
| P5-5-I | `src/consultdeck/renderer/factory.py` 実装        |

テスト対象:
- `active: builtin` → BuiltinRenderer返却
- `active: mcp` → McpRenderer返却

---

**Phase 5完了条件:** BuiltinRendererでPPTXが生成され、全Rendererテストがパス

---

## Phase 6: CLIエントリポイント

### P6-1: CLI実装

| タスク   | 内容                                    |
| ----- | --------------------------------------- |
| P6-1-T | `tests/unit/test_cli.py` 作成            |
| P6-1-I | `src/consultdeck/cli.py` 実装（clickコマンド）|

CLIコマンド:

```
consultdeck generate --theme "..." --purpose "..." --audience "..." --slides 10
consultdeck generate --input input.yaml
```

テスト対象:
- `--help` の動作
- 必須引数欠損時のエラーメッセージ
- YAML入力ファイルでのパイプライン起動

---

**Phase 6完了条件:** CLIコマンドが動作し、PPTX出力まで通しで実行できる

---

## Phase 7: 統合テスト

### P7-1: パイプライン統合テスト

| タスク   | 内容                                          |
| ----- | --------------------------------------------- |
| P7-1-T | `tests/integration/test_pipeline.py` 作成      |

テスト対象:
- 入力YAML → RequirementSpec → OutlineSpec → SlideSpec → PPTX の通しテスト
- LLMはモック化（Ollamaへの実接続なし）
- PPTX生成は実行（python-pptxを使用）

---

### P7-2: テンプレート統合テスト

| タスク   | 内容                                                |
| ----- | --------------------------------------------------- |
| P7-2-T | `tests/integration/test_template_pipeline.py` 作成  |

テスト対象:
- 各テンプレート（proposal/analysis/report）でのPPTX生成

---

**Phase 7完了条件:** 統合テストが全パスし、カバレッジ80%以上

---

## タスクサマリ

| Phase | 内容               | MVP | 優先度 |
| ----- | ---------------- | --- | --- |
| P0    | プロジェクト基盤         | ○   | 最高  |
| P1    | データモデル（SlideSpec） | ○   | 最高  |
| P2    | テンプレート管理         | ○   | 高   |
| P3    | LLMクライアント        | ○   | 高   |
| P4    | パイプライン実装         | ○   | 高   |
| P5    | Renderer実装       | ○   | 高   |
| P6    | CLIエントリポイント      | ○   | 中   |
| P7    | 統合テスト            | ○   | 中   |

---

## 非MVPタスク（将来フェーズ）

| タスク             | 内容                |
| --------------- | ----------------- |
| Web UI          | FastAPI + フロントエンド |
| McpRenderer完全実装 | 実際のMCP接続          |
| ImageGenerator  | AUTOMATIC1111連携   |
| Google Slides対応 | 追加Renderer        |
| テンプレートGUI管理    | CRUD UI           |
| RAG             | 社内資料参照            |
| Mermaid図生成      | DiagramSpec連携     |
