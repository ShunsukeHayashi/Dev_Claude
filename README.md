# YAML Context Engineering for Claude Code

Claude Code用のMCPツールとして、階層的なコンテキスト情報を抽出し、YAML形式のドキュメントを自動生成するツールセット。

## 🎉 プロジェクトステータス

- **MVP**: ✅ **完成** (2025-08-04)
- **Phase 1**: ✅ 完了 - Core MCP Server実装
- **Phase 2**: 🚧 **開始** - Claude Code統合強化
- **Phase 3**: 📅 計画中 - GitHub Actions自動化
- **Phase 4**: 📅 計画中 - 高度な機能実装

### 最新の更新
- ✅ MVPが完成し、基本的なURL抽出とYAML生成が動作
- ✅ CLIインターフェース実装完了
- ✅ 5つのMCPツール実装完了
- 🔧 YAMLシリアライズの問題を修正
- 🚀 Phase 2: Claude Code統合の開発開始

## 概要

このプロジェクトは、Claude Codeの拡張ツールとして機能するMCPサーバーです。様々な形式の入力（URL、テキスト、構造化データ）から階層的かつ構造化されたコンテキスト情報を抽出し、Claude Codeが参照可能なYAML形式の.mdファイルとして自動的に整理・永続化します。

### Claude Codeでの主な機能

- 🌐 **URLクロール**: Claude Code内から指定URLのコンテンツを自動取得
- 📊 **階層構造抽出**: Claude Codeの解析能力を拡張し、L1、L2、L3レベルの見出し構造を自動識別
- 📝 **コンテンツ要約**: Claude Codeのコンテキスト管理を支援する要約機能
- 🔄 **自律的クロール**: Claude Codeのタスク実行中に関連URLを発見し、再帰的に処理
- 💾 **YAML生成**: Claude Codeが理解しやすい構造化されたYAML frontmatterを持つMarkdownファイルを生成

## Claude Codeプロジェクト構造

```
Dev_Claude/
├── .claude/                   # Claude Code設定（最重要）
│   ├── settings.json         # MCPサーバー設定と統合
│   ├── commands/             # カスタムスラッシュコマンド
│   │   ├── extract-context.md
│   │   ├── setup-project.md
│   │   └── generate-agent.md
│   └── agents/               # Claude Code用サブエージェント
│       ├── context-extractor.md
│       └── quality-analyzer.md
├── mcp-server/                # Claude Code用MCPサーバー実装
│   ├── src/                   # ソースコード
│   │   └── yaml_context_engineering/
│   │       ├── tools/         # Claude Codeツール実装
│   │       ├── utils/         # ユーティリティ
│   │       └── templates/     # YAMLテンプレート
│   ├── tests/                 # テストスイート
│   └── docs/                  # API ドキュメント
├── generated_contexts/        # Claude Codeが生成したコンテキスト
├── CLAUDE.md                 # Claude Code専用ガイドライン
└── README.md                 # このファイル
```

## セットアップ

### 前提条件

- Claude Code（必須）
- Python 3.9以上（MCPサーバー用）
- pip（Pythonパッケージマネージャー）

### インストール手順

1. リポジトリのクローン
```bash
git clone <repository-url>
cd Dev_Claude
```

2. Python仮想環境の作成（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 依存関係のインストール
```bash
cd mcp-server
pip install -r requirements.txt
```

4. 開発モードでのインストール
```bash
pip install -e .
```

5. LDDシステムの初期化（オプション）
```bash
yaml-context ldd init
```

## 使用方法

### Claude Codeでの使用（推奨）

1. Claude Codeでプロジェクトを開く
2. カスタムスラッシュコマンドを使用：

```
/extract-context https://docs.example.com/api
/setup-project my-project
/generate-agent api-docs
```

### MCPサーバーの手動起動（開発用）

```bash
cd mcp-server
python -m yaml_context_engineering.main
```

注: 通常はClaude Codeが自動的にMCPサーバーを起動します。

### プログラムから使用

```python
from yaml_context_engineering import YamlContextServer

server = YamlContextServer()
await server.run()
```

## Claude Codeで利用可能なツール

### 1. web_content_fetcher
Claude Codeから指定URLのコンテンツを取得

### 2. llm_structure_extractor  
Claude Codeの理解を助ける階層構造の抽出

### 3. url_discovery_engine
Claude Codeのタスク実行中に関連URLを自動発見

### 4. file_system_manager
Claude Codeのワークスペース内でファイル管理

### 5. ldd_manager
Log-Driven Development (LDD) システムでタスク管理とナレッジ蓄積

これらのツールはClaude Code内で `mcp__yaml-context-engineering__` プレフィックスで利用可能です。

詳細は[docs/API.md](mcp-server/docs/API.md)を参照。

## Claude Code用出力形式

Claude Codeが理解しやすい形式でファイルを生成：

```yaml
---
# Claude Codeメタデータ
title: "抽出されたコンテンツのタイトル"
source_url: "https://source.url"
last_updated: "2025-01-15T10:30:00Z"
content_type: "documentation"
language: "ja"

# Claude Code解析情報
extraction_confidence: 0.95
claude_code_version: "1.0.0"
extracted_by: "claude-code-context-extractor"
extraction_timestamp: "2025-08-03T12:00:00Z"

# Claude Code階層構造
hierarchy_levels: ["L1", "L2", "L3"]
related_sources: []
tags: []
---

# コンテンツ

Claude Codeが参照しやすい階層的に整理されたコンテンツ...
```

## LDD (Log-Driven Development) システム

YAML Context Engineeringには、タスク管理とナレッジ蓄積のためのLDDシステムが統合されています。

### LDDの主な機能

- **📝 タスクログ管理**: コンテキスト抽出タスクの詳細な記録
- **🧠 メモリバンク**: 抽出パターンや洞察の永続化
- **📊 パターン分析**: 成功・失敗パターンの自動分析
- **🔍 知識検索**: 蓄積された知識の効率的な検索

### LDDコマンド

```bash
# LDDシステムの初期化
yaml-context ldd init

# タスクログの作成
yaml-context ldd task "APIドキュメントの抽出" -p "my-project" -m "api-docs"

# メモリバンクへの追加
yaml-context ldd memory "効率的な抽出パターンを発見" -t Pattern --tags "optimization,extraction"

# タスクの更新（開発中）
yaml-context ldd task update <task-id> --status "Completed"

# メモリの検索（開発中）
yaml-context ldd memory search "extraction pattern"

# パターン分析（開発中）
yaml-context ldd analyze
```

### LDDディレクトリ構造

```
generated_contexts/
├── logs/                      # タスクログ
│   ├── tasks/                # タスク実行ログ
│   ├── system/               # システムログ
│   └── metrics/              # メトリクス
├── @memory-bank.md           # メモリバンク（知識DB）
└── @logging_template.md      # ログテンプレート
```

## 開発

### テストの実行

```bash
cd mcp-server
pytest
```

### コードフォーマット

```bash
black src/ tests/
```

### 型チェック

```bash
mypy src/
```

## トラブルシューティング

### 一般的な問題

1. **インポートエラー**: Python pathが正しく設定されているか確認
2. **権限エラー**: 出力ディレクトリへの書き込み権限を確認
3. **ネットワークエラー**: インターネット接続とプロキシ設定を確認

### ログの確認

詳細なログはコンソールに出力されます。ログレベルは環境変数で調整可能：

```bash
export MCP_LOG_LEVEL=DEBUG
```

## 貢献

Claude Code拡張への貢献を歓迎します！

1. このリポジトリをフォーク
2. Claude Codeで開発環境をセットアップ
3. 機能ブランチを作成 (`git checkout -b feature/claude-code-enhancement`)
4. Claude Codeでテストを実行
5. 変更をコミット（Claude Codeのフックが自動実行）
6. プルリクエストを作成

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 関連プロジェクト

- [Serena MCP Server](https://github.com/oraios/serena) - セマンティックなコード検索・編集
- [Claude-flow](https://github.com/ruvnet/claude-flow) - AIオーケストレーションプラットフォーム

## 今後の計画

### Phase 2: Claude Code統合の強化 🚧 **進行中**
- [ ] カスタムスラッシュコマンドの実装
  - `/extract-context` - URLからコンテキストを抽出
  - `/setup-project` - プロジェクト初期化
  - `/generate-agent` - 専門エージェント生成
- [ ] Hooks configurationの設定
- [ ] Sub-agent definitionsの作成
- [ ] Local testing environmentの構築

### Phase 3: GitHub Actions自動化 📅
- [ ] CI/CDワークフローの実装
- [ ] PR review automationの設定
- [ ] Issue processing automationの実装
- [ ] Documentation generationの自動化

### Phase 4: 高度な機能 📅
- [ ] Quality analysis systemの実装
- [ ] Plugin architectureの開発
- [ ] Performance optimizationの実施
- [ ] Comprehensive testingの実施

詳細は[PLANNING.md](PLANNING.md)を参照してください。