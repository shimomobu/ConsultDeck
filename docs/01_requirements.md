# ConsultDeck 要件定義

## 1. 目的

ローカル環境で動作するコンサル資料半自動生成システム。  
AIは「構成設計」「型適用」「下書き生成」「レビュー補助」を担当し、最終品質保証は人間が行う。

---

## 2. 入力仕様

ユーザーは以下の入力を与える。

| 項目          | 型      | 必須 | 説明                        |
| ----------- | ------ | -- | ------------------------- |
| theme       | string | ◎  | 資料テーマ                     |
| purpose     | string | ◎  | 目的（提案・説明・報告など）            |
| audience    | string | ◎  | 読者（経営層・部長層・現場など）          |
| slide_count | int    | ◎  | スライド枚数                    |
| constraints | string | -  | 記載禁止事項・対象範囲など             |
| tone        | string | -  | フォーマル・戦略系など（デフォルト: フォーマル）|
| template_id | string | -  | テンプレートID（未指定時は自動選択）       |

入力はCLI引数またはYAML入力ファイル経由で受け付ける。

---

## 3. RequirementSpec

ユーザー入力を構造化したデータオブジェクト。

```
RequirementSpec
  theme: str
  purpose: str
  audience: str
  slide_count: int
  constraints: str | None
  tone: str
  template_id: str | None
```

---

## 4. OutlineSpec

RequirementSpecを基にLLMが生成するスライド構成案。

```
OutlineSpec
  title: str
  slides: list[OutlineItem]
    OutlineItem
      slide_id: str
      title: str
      role: str
```

---

## 5. SlideSpec（中核データ構造）

SlideSpecはシステム全体の中核となるデータ構造であり、Rendererへの唯一の入力とする。

```
SlideSpec
  deck_id: str
  title: str
  template_id: str
  slides: list[Slide]  # 1件以上
    Slide
      slide_id: str
      title: str
      message: str
      bullets: list[str]  # TITLE / BLANKでは空配列可
      diagram: DiagramSpec | None
      image: ImageSpec | None
      notes: str | None
      layout_type: LayoutType  # title / content / two_column / blank
```

SlideSpecはJSONまたはYAMLでシリアライズ可能とする。  
Renderer以外のモジュールはSlideSpecを直接PPTXへ変換しない。

---

## 6. テンプレート管理仕様

テンプレートは登録・更新・削除可能。

| 項目              | 説明        |
| --------------- | --------- |
| template_id     | 一意ID      |
| name            | テンプレート名称  |
| doc_type        | 提案・報告・分析等 |
| use_case        | 利用用途      |
| audience        | 想定読者      |
| phase           | 提案フェーズ    |
| slide_structure | スライド構成    |
| layout_rules    | レイアウト規則   |
| style_rules     | 配色・余白・文体等 |
| output_targets  | pptx等     |

MVPでは`layout_rules`、`style_rules`はdict、`output_targets`はlistとして扱う。  
高度なレイアウト決定はPhase 5以降でRenderer側の責務と合わせて整理する。

### 初期提供テンプレート（MVP対象）

| テンプレートID          | 用途  | 構成           |
| ----------------- | --- | ------------ |
| proposal_standard | 提案型 | 課題 → 解決 → 効果 |
| analysis_standard | 分析型 | 事実 → 分析 → 示唆 |
| report_standard   | 報告型 | 状況 → 課題 → 対応 |

---

## 7. PPTX生成仕様

SlideSpecを入力としてPPTXを生成する。

| 要求         | 内容                          |
| ---------- | --------------------------- |
| 出力形式       | .pptx                       |
| 編集性        | PowerPointで後編集可能             |
| レイアウト      | テンプレートのlayout_rulesを適用      |
| 画像配置       | PNGを指定位置に差し込み               |
| 図形         | 可能な限りPPTネイティブ図形（テキストボックス等） |
| Renderer分離 | RendererはSlideSpecを主入力とし、TemplateSpecと出力先を受け取る |

---

## 8. Renderer仕様

### 内蔵Renderer（BuiltinPptxRenderer）

python-pptxを使用してSlideSpecとTemplateSpecからPPTXを生成する。

### MCP Renderer（McpRenderer）

SlideSpecをMCP呼び出し用入力形式に変換し、外部PPT生成サービスへ委譲する。

| 要求      | 内容                                 |
| ------- | ---------------------------------- |
| アダプタ    | SlideSpec → MCP入力形式への変換            |
| 接続先変更   | 設定ファイルおよびCLIオプションから変更可能            |
| 有効/無効切替 | BuiltinPptxRenderer / McpRenderer を切り替え |
| フォールバック | MCP不可時はBuiltinPptxRendererへ自動切替        |
| 認証情報    | 環境変数または設定ファイル（平文禁止）                |
| ログ      | 呼び出し結果・失敗理由を記録                     |

---

## 9. レビュー機能仕様

SlideSpec生成後、LLMによるレビューを実施する。

| レビュー項目 | 説明        |
| ------ | --------- |
| 論理性    | 話の流れ・因果関係 |
| 冗長性    | 重複表現の検出   |
| 読者適合   | 対象読者への適合度 |
| 構造     | MECE性等    |
| テンプレ逸脱 | 型崩れ検知     |

レビュー結果はSlideSpecと並列でCLIに出力する。修正指示はユーザーが行う。

---

## 10. 画像生成仕様

Stable Diffusion（AUTOMATIC1111）を用いる。

| 用途     | 利用可否 |
| ------ | ---- |
| 表紙     | ○    |
| 概念イメージ | ○    |
| 挿絵     | △    |
| 構造図    | ×    |
| 比較図    | ×    |
| グラフ    | ×    |

- 全スライド画像生成は禁止
- 画像生成はSlideSpecのImageSpecが存在するスライドのみ対象
- GPU利用は排他制御（LLM推論と同時実行禁止）

---

## 11. 非機能要件

| 項目   | 内容                   |
| ---- | -------------------- |
| 実行環境 | Linux / HP Z620      |
| GPU  | RTX 3060 12GB（排他制御）  |
| RAM  | 64GB                 |
| LLM  | Ollama（Gemma系小型モデル） |
| UI   | CLI（MVP）/ Web UI（将来）|
| 設定形式 | YAML                 |
| テスト  | TDD / カバレッジ80%以上    |
| Renderer | 差し替え可能な構造        |

---

## 12. MVPスコープ

| 機能                | MVP | 理由           |
| ----------------- | --- | ------------ |
| CLI入力             | ○   | 必須動作経路       |
| RequirementSpec生成 | ○   | パイプライン起点     |
| OutlineSpec生成（LLM）| ○  | 構成設計         |
| SlideSpec生成（LLM） | ○   | 中核           |
| BuiltinRenderer   | ○   | 正式出力         |
| 初期3テンプレート        | ○   | 最小限の型適用      |
| レビュー機能（簡易）       | ○   | MVP内で実装      |
| McpRenderer       | △   | インタフェース定義のみ  |
| 画像生成（SD）          | △   | 接続確認のみ（オプション）|
| Web UI            | ×   | 将来拡張         |
| テンプレートGUI管理      | ×   | 将来拡張         |

---

## 13. 非MVPスコープ（将来拡張）

| 項目                     | 内容          |
| ---------------------- | ----------- |
| Web UI                 | ブラウザ操作      |
| テンプレ共有                 | テンプレートライブラリ |
| Google Slides Renderer | 複数Renderer対応|
| LLM Judge              | レビュー高度化     |
| Mermaid連携              | 図生成         |
| RAG                    | 社内資料参照      |
| GUI設定変更                | MCP接続先等のGUI |
