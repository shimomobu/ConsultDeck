# ConsultDeck Decision Log

## Decision 001: PPTXを正式成果物とする

- Status: Accepted
- Phase: 0
- Decision: ConsultDeckはPPTXファイルを正式成果物とする。
- Rationale: コンサル資料はPowerPointでの後編集、配布、レビューが前提となるため、MVPでは編集可能な`.pptx`を最終出力にする。

## Decision 002: SlideSpecを中核設計とする

- Status: Accepted
- Phase: 0
- Decision: SlideSpecをLLM生成結果とRenderer入力の唯一の接点とする。
- Rationale: PPTX生成の前段を構造化データに閉じ込めることで、LLM、テンプレート、レビュー、Rendererの責務を分離できる。

## Decision 003: Rendererを差し替え可能にする

- Status: Accepted
- Phase: 0
- Decision: Rendererは`render(spec: SlideSpec) -> Path`の境界で差し替え可能にする。
- Rationale: 内蔵Rendererと外部Rendererを同じアプリケーション層から扱い、PPTX生成方式の変更を局所化する。

## Decision 004: MCP経由のPPT生成を将来拡張として考慮する

- Status: Accepted
- Phase: 0
- Decision: MCP経由のPPT生成機能呼び出しは、MVP後の拡張として設計上考慮する。
- Rationale: 外部の高品質Rendererや既存PPT生成サービスと連携できる余地を残しつつ、MVPでは内蔵Rendererを優先する。

## Decision 005: Stable Diffusionは補助用途に限定する

- Status: Accepted
- Phase: 0
- Decision: Stable Diffusionは表紙、概念イメージ、挿絵などの補助用途に限定する。
- Rationale: 構造図、比較図、グラフは正確性と編集性が重要なため、画像生成ではなくPPTネイティブ要素を優先する。

## Decision 006: GPU利用は時間分離・同時利用禁止とする

- Status: Accepted
- Phase: 0
- Decision: LLM推論と画像生成のGPU利用は時間分離し、同時利用を禁止する。
- Rationale: ローカルGPU環境で推論と画像生成が競合すると性能劣化や失敗につながるため、ファイルロックで排他制御する。

## Decision 007: TemplateRepositoryを純粋なデータアクセス層とする

- Status: Accepted
- Phase: 2.6
- Decision: TemplateRepositoryはYAMLテンプレートの読み込み、一覧取得、ID取得に責務を限定し、RequirementSpecやTemplateSelectorに依存しない。
- Rationale: データアクセスと選択ロジックを分離することで、テンプレート取得の副作用範囲を小さくし、マッチングルールの変更をTemplateSelectorに集約する。

## Decision 008: TemplateSelectorのaudience一致はMVPでは厳密一致とする

- Status: Accepted
- Phase: 2.6
- Decision: TemplateSelectorのaudience判定はMVPではtrim + casefoldの完全一致のみとする。
- Rationale: audienceエイリアス、階層関係、スコアリング、優先順位付けは過剰実装になるため、Phase 2.6ではpurpose/doc_typeの語彙揺れ吸収に限定する。
- Future: TemplateSpecの`layout_rules`、`style_rules`、`output_targets`はPhase 5前に追加検討する。
