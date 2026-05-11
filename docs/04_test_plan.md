# ConsultDeck テスト計画

## 1. テスト方針

### 基本原則

- TDD必須：テストを先に書き、実装で通す（RED → GREEN → REFACTOR）
- カバレッジ目標：ライン80%以上
- LLM・外部API依存はすべてモック化する
- BuiltinRenderer（python-pptx）は実際に実行してPPTXを検証する
- Ollama・AUTOMATIC1111への実接続はユニットテスト・統合テストでは行わない

### テスト種別

| 種別        | 対象                          | 外部依存 | 実行速度 |
| --------- | ----------------------------- | ---- | ---- |
| ユニットテスト   | 個別モジュール                     | モック  | 高速   |
| 統合テスト     | パイプライン全体・Renderer出力検証        | モック  | 中速   |
| E2Eテスト    | CLIコマンド → PPTX生成（将来）         | モック  | 低速   |

---

## 2. テスト戦略：モジュール別

### 2.1 データモデル（models/）

**戦略:** Pydanticのバリデーションを中心にテスト。シリアライズの往復を確認する。

| テスト対象          | テスト内容                             | ファイル                                         |
| -------------- | --------------------------------- | -------------------------------------------- |
| RequirementSpec | slide_count最小値、theme空文字、toneデフォルト値 | `tests/unit/models/test_requirement_spec.py` |
| OutlineSpec    | slides構造、slide_id/title/role、旧sections拒否 | `tests/unit/models/test_outline_spec.py`     |
| SlideSpec      | layout_type enum、JSON往復、YAML往復     | `tests/unit/models/test_slide_spec.py`       |
| TemplateSpec   | 必須フィールド、layout_rules構造            | `tests/unit/models/test_template_spec.py`    |

**共通テストパターン:**

```python
# バリデーションエラーの検証
def test_slide_count_must_be_positive():
    with pytest.raises(ValidationError):
        RequirementSpec(theme="test", purpose="p", audience="a", slide_count=0)

# シリアライズ往復
def test_slide_spec_json_roundtrip(sample_slide_spec):
    json_str = sample_slide_spec.model_dump_json()
    restored = SlideSpec.model_validate_json(json_str)
    assert restored == sample_slide_spec
```

---

### 2.2 テンプレート管理（template/）

**戦略:** ファイルI/Oはtmpdirを使用して実ファイルシステムでテスト。

| テスト対象             | テスト内容                          | ファイル                                    |
| ----------------- | ------------------------------ | --------------------------------------- |
| TemplateRepository | get成功、存在しないIDで例外、YAMLパースエラー | `tests/unit/template/test_repository.py` |
| TemplateSelector  | ID指定取得、doc_typeマッチング、デフォルト選択  | `tests/unit/template/test_selector.py`  |

**テストパターン:**

```python
def test_repository_get_existing(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "proposal_standard.yaml").write_text(SAMPLE_YAML)
    repo = TemplateRepository(template_dir)
    spec = repo.get("proposal_standard")
    assert spec.template_id == "proposal_standard"

def test_repository_get_missing_raises(tmp_path):
    repo = TemplateRepository(tmp_path / "templates")
    with pytest.raises(TemplateNotFoundError):
        repo.get("nonexistent")
```

---

### 2.3 LLMクライアント（llm/）

**戦略:** httpxのモックでOllama APIをスタブ化。ネットワーク接続なし。

| テスト対象     | テスト内容                             | ファイル                            |
| --------- | --------------------------------- | ------------------------------- |
| LlmClient | 正常レスポンス取得、タイムアウト例外、接続エラー例外 | `tests/unit/llm/test_client.py` |

**テストパターン:**

```python
def test_llm_client_success(respx_mock):
    respx_mock.post("http://localhost:11434/api/generate").mock(
        return_value=httpx.Response(200, json={"response": "output text"})
    )
    client = LlmClient(base_url="http://localhost:11434", model="gemma2:2b")
    result = client.generate("test prompt")
    assert result == "output text"

def test_llm_client_timeout(respx_mock):
    respx_mock.post(...).mock(side_effect=httpx.TimeoutException("timeout"))
    with pytest.raises(LlmTimeoutError):
        client.generate("test prompt")
```

---

### 2.4 GPU排他制御（gpu/）

**戦略:** filelockのテスト。実際のロックファイルをtmpdirで作成。

| テスト対象        | テスト内容                   | ファイル                               |
| ------------ | ----------------------- | ---------------------------------- |
| GpuScheduler | ロック取得・解放、タイムアウト例外 | `tests/unit/gpu/test_scheduler.py` |

---

### 2.5 パイプライン（pipeline/）

**戦略:** LlmClientをMockオブジェクトで差し替え。LLM出力は固定のJSONを返す。

| テスト対象           | テスト内容                                  | ファイル                                             |
| --------------- | -------------------------------------- | ------------------------------------------------ |
| InputParser     | CLI引数パース、YAML入力パース、必須フィールド欠損エラー   | `tests/unit/pipeline/test_input_parser.py`       |
| OutlineGenerator | OutlineSpec生成、JSONパース失敗時のリトライ/例外    | `tests/unit/pipeline/test_outline_generator.py`  |
| SlideGenerator  | SlideSpec生成、スライド数一致、バリデーション通過       | `tests/unit/pipeline/test_slide_generator.py`    |
| Reviewer        | ReviewResult生成、構造検証（項目・スコア・コメント）   | `tests/unit/pipeline/test_reviewer.py`           |

**テストパターン:**

```python
def test_slide_generator_produces_correct_count(mock_llm_client):
    mock_llm_client.generate.return_value = SAMPLE_SLIDE_SPEC_JSON
    generator = SlideGenerator(llm_client=mock_llm_client)
    req = RequirementSpec(theme="DX推進", purpose="提案", audience="経営層", slide_count=5)
    spec = generator.generate(outline=sample_outline, template=sample_template, requirement=req)
    assert len(spec.slides) == 5
```

---

### 2.6 Renderer（renderer/）

**戦略:** BuiltinRendererは実際のPPTXを生成して検証。McpRenderer/McpAdapterはモックのみ。

| テスト対象           | テスト内容                                   | ファイル                                           |
| --------------- | --------------------------------------- | ---------------------------------------------- |
| BuiltinPptxRenderer | PPTX生成、スライド枚数一致、タイトル埋め込み、拡張子検証 | `tests/unit/renderer/test_builtin_pptx_renderer.py` |
| McpAdapter      | SlideSpec → McpPayload変換、フィールドマッピング正確性 | `tests/unit/renderer/test_mcp_adapter.py`      |
| McpRenderer     | フォールバック動作（接続失敗 → BuiltinRenderer）    | `tests/unit/renderer/test_mcp_renderer.py`     |
| RendererFactory | active設定でRenderer切替                    | `tests/unit/renderer/test_factory.py`          |

**テストパターン:**

```python
def test_builtin_renderer_creates_pptx(tmp_path, sample_slide_spec):
    renderer = BuiltinRenderer(output_dir=tmp_path)
    output_path = renderer.render(sample_slide_spec)
    assert output_path.suffix == ".pptx"
    assert output_path.exists()
    prs = Presentation(output_path)
    assert len(prs.slides) == len(sample_slide_spec.slides)

def test_mcp_renderer_falls_back_to_builtin(tmp_path, sample_slide_spec):
    builtin = BuiltinRenderer(output_dir=tmp_path)
    mcp_renderer = McpRenderer(
        mcp_client=Mock(side_effect=ConnectionError()),
        fallback=builtin,
    )
    output_path = mcp_renderer.render(sample_slide_spec)
    assert output_path.exists()
```

---

## 3. 統合テスト戦略

### 3.1 パイプライン統合テスト

**対象:** `tests/integration/test_pipeline.py`

**目的:** 各モジュールを接続した状態でパイプライン全体が動作することを確認する。

**モック範囲:**
- LlmClient → モック（固定JSON応答）
- ImageGenerator → スキップ
- GpuScheduler → テスト時はロックスキップ

**実行範囲:**
- TemplateRepository（実ファイル: `assets/templates/`）
- BuiltinRenderer（実際のPPTX生成）

**フロー:**

```
入力YAML → InputParser → RequirementSpec
  → TemplateSelector → TemplateSpec
  → OutlineGenerator（モック）→ OutlineSpec
  → SlideGenerator（モック）→ SlideSpec
  → Reviewer（モック）→ ReviewResult
  → BuiltinRenderer → PPTX（ファイル存在・枚数確認）
```

---

### 3.2 テンプレート統合テスト

**対象:** `tests/integration/test_template_pipeline.py`

**目的:** 3種のテンプレートそれぞれでPPTXが生成できることを確認する。

| テンプレート            | 期待スライド構成          |
| ----------------- | ----------------- |
| proposal_standard | 課題 → 解決 → 効果スライド |
| analysis_standard | 事実 → 分析 → 示唆スライド |
| report_standard   | 状況 → 課題 → 対応スライド |

---

## 4. テストディレクトリ構成

```
tests/
├── conftest.py
├── unit/
│   ├── models/
│   │   ├── test_requirement_spec.py
│   │   ├── test_outline_spec.py
│   │   ├── test_slide_spec.py
│   │   └── test_template_spec.py
│   ├── template/
│   │   ├── test_repository.py
│   │   └── test_selector.py
│   ├── llm/
│   │   └── test_client.py
│   ├── gpu/
│   │   └── test_scheduler.py
│   ├── pipeline/
│   │   ├── test_input_parser.py
│   │   ├── test_outline_generator.py
│   │   ├── test_slide_generator.py
│   │   └── test_reviewer.py
│   └── renderer/
│       ├── test_builtin_pptx_renderer.py
│       ├── test_mcp_adapter.py
│       ├── test_mcp_renderer.py
│       └── test_factory.py
└── integration/
    ├── test_pipeline.py
    └── test_template_pipeline.py
```

---

## 5. 共通フィクスチャ（conftest.py）

```python
@pytest.fixture
def sample_requirement_spec(): ...      # RequirementSpec（テーマ: DX推進）

@pytest.fixture
def sample_outline_spec(): ...          # OutlineSpec（3セクション・5スライド）

@pytest.fixture
def sample_slide_spec(): ...            # SlideSpec（5スライド・各layout_type混在）

@pytest.fixture
def sample_template_spec(): ...         # proposal_standardのTemplateSpec

@pytest.fixture
def mock_llm_client(): ...              # MagicMock(spec=LlmClient)

@pytest.fixture
def tmp_output_dir(tmp_path): ...       # 一時出力ディレクトリ
```

---

## 6. カバレッジ設定

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/consultdeck --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
omit = ["*/cli.py"]  # CLIエントリは統合テストで担保
```

---

## 7. テスト除外範囲

| 除外対象              | 理由                    |
| ----------------- | --------------------- |
| Ollama実接続         | ローカル環境依存。モックで代替       |
| AUTOMATIC1111実接続  | GPU利用・ローカル環境依存。MVPでは無効 |
| McpRenderer実MCP接続 | 外部サービス依存。スタブで代替       |
| PPTX目視確認          | 自動テスト対象外（手動レビュー前提）    |
| LLM出力品質           | 非決定的。プロンプト品質は手動評価     |

---

## 8. MVPテストスコープ

| テスト対象             | MVP | 備考          |
| ----------------- | --- | ----------- |
| データモデル全種          | ○   |             |
| TemplateRepository | ○   |             |
| TemplateSelector  | ○   |             |
| LlmClient（モック）    | ○   |             |
| GpuScheduler      | ○   |             |
| InputParser       | ○   |             |
| OutlineGenerator  | ○   |             |
| SlideGenerator    | ○   |             |
| Reviewer          | ○   |             |
| BuiltinRenderer   | ○   | 実PPTX生成テスト  |
| McpAdapter        | ○   | 変換テストのみ     |
| McpRenderer       | △   | フォールバックテストのみ|
| RendererFactory   | ○   |             |
| 統合テスト（パイプライン）     | ○   |             |
| 統合テスト（テンプレート）     | ○   |             |
| McpRenderer実接続テスト | ×   | 将来          |
| ImageGenerator    | ×   | 将来          |
