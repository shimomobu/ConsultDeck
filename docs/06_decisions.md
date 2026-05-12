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
- Decision: Rendererは`render(spec: SlideSpec, output_dir: Path) -> Path`の境界で差し替え可能にする。
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

## Decision 009: OutlineBuilderはテンプレート構成を決定的に展開する

- Status: Accepted
- Phase: 3
- Decision: OutlineBuilderはLLMを使わず、TemplateSpec.slide_structureをRequirementSpec.slide_countに合わせて決定的に展開し、OutlineSpec.slidesのみを生成する。
- Rationale: MVPでは安定したテスト可能性を優先し、章立て生成をテンプレート起点の純粋変換に限定する。
- Details: slide_countがslide_structureより多い場合は構成を先頭から繰り返す。slide_countが少ない場合は指定枚数で切り詰める。slide_idは`slide-001`からの安定連番とする。

## Decision 010: OutlineSpecの正式構造をslidesへ一本化する

- Status: Accepted
- Phase: 3.5
- Decision: OutlineSpecの正式構造は`slides: list[OutlineItem]`のみとし、旧`sections`構造は廃止する。
- Rationale: 後続のSlideSpec生成で入力構造が二重化すると責務と変換ルールが曖昧になるため、外部利用者がいない現段階でbreaking changeとして整理する。

## Decision 011: SlideBuilderは決定論的な仮本文でSlideSpecを生成する

- Status: Accepted
- Phase: 4
- Decision: SlideBuilderはRequirementSpec、OutlineSpec、TemplateSpecからRenderer入力契約であるSlideSpecを生成し、LLM本文生成はまだ行わない。
- Rationale: Renderer境界に渡す構造を先に固定し、後続のLLM生成やレビュー処理をSlideSpec契約に合わせて追加できる状態にする。
- Details: slide_idとtitleはOutlineItem由来とする。message、bullets、notesは決定論的な仮文を生成する。layout_typeはMVPではroleの簡易ルールで決定し、未該当はcontentとする。

## Decision 012: Renderer前のSlideSpec契約を緩めすぎず固定する

- Status: Accepted
- Phase: 4.5
- Decision: SlideSpec.slidesは1件以上を必須とし、Slide.bulletsは空配列を許容する。SlideBuilderはCONTENT/TWO_COLUMNではbulletsを生成し、TITLE/BLANKではbulletsなしを許容する。
- Rationale: 表紙や空白レイアウトではbulletsが不要な一方、空デッキはRenderer入力として意味を持たないため、制約をSlideSpecとBuilderの責務に分ける。

## Decision 013: deck_idは呼び出し側指定と自動生成を両立する

- Status: Accepted
- Phase: 4.5
- Decision: SlideBuilder.build()は任意のdeck_idを受け取り、未指定時はUUID由来の衝突しにくいIDを生成する。
- Rationale: テストや再現性が必要な経路では固定IDを使い、通常生成ではテンプレートID由来の固定ID衝突を避ける。

## Decision 014: Builtin PPTX Rendererは最小編集可能PPTXを生成する

- Status: Accepted
- Phase: 5
- Decision: BuiltinPptxRendererはpython-pptxをRenderer層に閉じ込め、SlideSpecから編集可能な`.pptx`を生成する。
- Rationale: Phase 5では見た目の完成度より、Renderer境界、実ファイル生成、スライド数一致、基本layout処理を優先する。
- Details: 出力ファイル名は`spec.deck_id + ".pptx"`とする。TITLE、CONTENT、TWO_COLUMN、BLANKの最小レイアウトだけを処理する。

## Decision 015: Renderer Protocolを採用する

- Status: Accepted
- Phase: 5.5
- Decision: Renderer境界はABCではなくProtocolで表現する。
- Rationale: BuiltinPptxRendererと将来のMcpRendererを疎結合に保ち、継承よりも構造的部分型で差し替え可能性を表現する。
- Details: Protocolの契約は`render(spec: SlideSpec, output_dir: Path) -> Path`に限定し、TemplateSpecなどテンプレート管理の詳細をRenderer境界へ持ち込まない。

## Decision 016: deck_idはファイル名stemとして扱う

- Status: Accepted
- Phase: 5.5
- Decision: SlideSpec.deck_idには`/`、`\`、`..`などパスに解釈されうる文字列を許可しない。
- Rationale: Rendererの出力ファイル名が`deck_id + ".pptx"`であるため、deck_id経由のディレクトリトラバーサルやoutput_dir外への書き込みをモデル層で防ぐ。

## Decision 017: 同一deck_idのPPTXは上書きする

- Status: Accepted
- Phase: 5.5
- Decision: BuiltinPptxRendererは同じoutput_dirとdeck_idで再実行された場合、既存の`.pptx`を上書きする。
- Rationale: MVPではファイル世代管理をRendererに持たせず、呼び出し側がdeck_idまたはoutput_dirで成果物を管理する。

## Decision 018: 残リスクはRisk Registerで一元管理する

- Status: Accepted
- Phase: 5.5
- Decision: Phaseごとの残リスク、レビュー指摘、Decision Log上の未対応事項は`docs/07_risks.md`で管理する。
- Rationale: Phase 6以降の実装で対応漏れを防ぐため、Open / Mitigated / Acceptedの状態を持つリスク台帳として一元管理する。

## Decision 019: CLIはPipelineの薄い入口にする

- Status: Accepted
- Phase: 6
- Decision: `python -m consultdeck`はCLI引数をRequirementSpecへ変換し、Pipelineへ委譲してPPTXのPathを表示する。
- Rationale: CLI、Pipeline、Rendererの責務を分け、GPU、Stable Diffusion、MCP、LLM本文生成を使わない細いend-to-end経路を先に固定する。

## Decision 020: CLIはeditable install後のconsole scriptを正式入口にする

- Status: Accepted
- Phase: 6.5
- Decision: `consultdeck` console scriptを`consultdeck.__main__:main`へ接続し、`python -m consultdeck`も維持する。
- Rationale: 利用者が`PYTHONPATH=src`を設定せずにCLIを実行できるようにしつつ、開発時のmodule entrypointも残す。

## Decision 021: CLIのデフォルトテンプレートはCWDに依存させない

- Status: Accepted
- Phase: MVP tag prep
- Decision: `--templates`未指定時は、実行時CWDではなくプロジェクト同梱の`assets/templates`を参照する。
- Rationale: console scriptをプロジェクトルート以外から実行しても、MVPの標準テンプレートを安定して読み込めるようにする。
- Details: 明示的な`--templates <path>`が指定された場合は、そのパスを優先する。

## Decision 022: LLM本文生成はProvider境界とfallbackで導入する

- Status: Accepted
- Phase: 6
- Decision: LLM本文生成は`LlmProvider` Protocolから`LlmGenerationResult`を受け取り、SlideBuilderがSlideSpecへ反映する。Provider未指定または失敗時はdeterministic contentへfallbackする。
- Rationale: SlideSpecを中心契約として維持し、RendererへLLM概念を持ち込まず、将来のOllama等のProvider差し替えを小さな境界で可能にする。
- Details: 初期実装ではOllama接続、multi-provider化、CLIオプション追加は行わない。
