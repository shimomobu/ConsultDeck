# ConsultDeck Risk Register

## Status Definitions

- Open: 対応が必要で、Phase 6以降の作業対象にする。
- Mitigated: Phase 5.5までに主要リスクを軽減済み。再発防止として監視する。
- Accepted: MVPでは許容し、明示的に後回しにする。

## Register

| ID | リスク内容 | 影響 | 優先度 | 対応方針 | 対応期限 | 状態 |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | audienceエイリアス未対応 | 「経営層」「役員」「CxO」などの語彙揺れでテンプレート候補が出ない | Medium | MVPでは完全一致を維持。Phase 6以降で必要性を見てalias辞書を追加 | Post-MVP | Accepted |
| R-002 | TemplateSelectorのスコアリング未対応 | 複数候補がある場合の優先順位を表現できない | Medium | テンプレート数が増えるまでは単純filterを維持。候補増加時にscore設計を追加 | Post-MVP | Accepted |
| R-003 | doc_type aliasが固定辞書のみ | 未登録の資料種別や表記揺れに弱い | Medium | Phase 6以降で設定ファイル化またはTemplateSpec側のmetadata化を検討 | Phase 6以降 | Open |
| R-004 | layout_rules/style_rulesの本格反映未対応 | テンプレートごとの差別化、配色、余白、レイアウト品質が出ない | High | Phase 6以降でSlideSpecまたはRenderer設定へ必要な最小スタイル情報を渡す方式を決め、段階的に実装 | Phase 6以降 | Open |
| R-005 | speaker notesの書式制御未対応 | notesは入るが、段落・箇条書き・書式を保持できない | Low | MVPではプレーンテキストで許容。必要に応じてnotes整形を追加 | Post-MVP | Accepted |
| R-006 | deck_idのWindows予約名・長すぎる名前未制御 | Windows環境で保存失敗、またはファイルシステム制限に触れる可能性がある | Medium | Phase 6以降で予約名・長さ制限を追加する | Phase 6以降 | Open |
| R-007 | 同一deck_idで上書きされる | 過去の出力ファイルを失う可能性がある | Medium | MVPではDecision 017として許容。呼び出し側がdeck_id/output_dirを管理する | MVP | Accepted |
| R-008 | PPTX見た目品質が最小限 | 実業務でそのまま使える品質には届かない | High | Phase 6以降でstyle_rules/layout_rules反映とレイアウト改善を追加 | Phase 6以降 | Open |
| R-009 | LLM本文生成未実装 | SlideSpecのmessage/bulletsが仮文のままで、資料内容の品質が低い | High | Phase 6以降でLLM生成をSlideSpec契約へ接続する | Phase 6以降 | Open |
| R-010 | MCP Renderer未実装 | 外部PPT生成サービスへ委譲できない | Medium | MVP後半またはPost-MVPでMcpAdapter/McpRendererを追加 | Post-MVP | Open |
| R-011 | Stable Diffusion画像差し込み未実装 | 表紙や概念画像をPPTXに埋め込めない | Low | MVPでは補助機能扱い。Renderer安定後に必要範囲だけ実装 | Post-MVP | Accepted |
| R-012 | GitHub未pushによるバックアップ未整備 | ローカル障害時に作業履歴を失う可能性がある | High | remote設定後にpush運用を開始する | Phase 6前後 | Open |
| R-013 | TemplateRepositoryが選択責務を持つ設計に戻るリスク | データアクセスと選択ロジックが再混在し、テスト容易性が下がる | Medium | Phase 2.6で責務分離済み。RepositoryにRequirementSpec/TemplateSelector依存を戻さない | Phase 2.6 | Mitigated |
| R-014 | OutlineSpecのsections/slides二重構造による後続処理の迷い | SlideSpec生成時に入力構造が曖昧になる | Medium | Phase 3.5でslidesへ一本化し、旧sectionsを拒否 | Phase 3.5 | Mitigated |
| R-015 | deck_id経由のoutput_dir外書き込み | ディレクトリトラバーサルにより意図しない場所へPPTXを書き込む | High | Phase 5.5で`/`、`\`、`..`をSlideSpec validationで拒否 | Phase 5.5 | Mitigated |
| R-016 | Slide.notesがPPTXへ出力されない | レビュー・発表用メモが成果物から欠落する | High | Phase 5.5でPowerPoint発表者ノートへ反映済み | Phase 5.5 | Mitigated |
| R-017 | python-pptx依存がRenderer以外へ漏れる | Renderer境界が崩れ、モデル・パイプラインがPPTX実装に依存する | High | dependency boundary testで`src/consultdeck/renderer/`配下に限定 | Phase 5 | Mitigated |
| R-018 | dependency boundary testがCWDに依存する | 別CWDからpytestを実行した際に検出漏れが起きる | Medium | Phase 5.5でテストファイル位置からproject rootを解決する方式へ修正 | Phase 5.5 | Mitigated |
| R-019 | CLI実行がPYTHONPATHに依存する | editable install後でも利用者が環境変数を設定しないとCLIを実行できない | High | Phase 6.5でconsole scriptとpackaging設定を追加し、`consultdeck`コマンドを提供 | Phase 6.5 | Mitigated |
| R-020 | 非editable配布時の標準テンプレート同梱未検証 | wheel等で`assets/templates`が同梱されない場合、`--templates`未指定のCLI実行が失敗する可能性がある | Medium | MVPではeditable install前提を維持。配布形式を固める段階でpackage data化とインストール後CLIテストを追加する | Post-MVP | Open |
| R-021 | wheelビルドに`assets/templates`が未同梱 | `pyproject.toml`のwheel設定が`packages = ["src/consultdeck"]`のみのため、non-editable install後にCLIのデフォルトテンプレート参照が壊れる可能性が高い | Medium | R-020の具体化リスク。editable install前提のMVPではタグ阻害にしない。Phase 6でpackage-data、hatch artifacts、`importlib.resources`などを検討する | Phase 6 | Open |
| R-022 | optional dependencyの境界未整理 | LLM、画像生成、MCP連携を同時に必須依存へ入れると、軽量CLI利用や環境構築が不安定になる | Medium | Phase 6でcoreとoptional groupsを分け、base installでCLIとBuiltinPptxRendererが動く状態を維持する | Phase 6 | Open |
