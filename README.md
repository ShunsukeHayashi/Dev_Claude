# YAML Context Engineering Agent

[![CI/CD Pipeline](https://github.com/yaml-context-engineering/agent/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/yaml-context-engineering/agent/actions)
[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://yaml-context-engineering.github.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io)
[![Claude Code Ready](https://img.shields.io/badge/Claude%20Code-Ready-purple)](https://claude.ai/code)

様々な形式の入力から、階層的かつ構造化されたコンテキスト情報を抽出し、生成AIが参照可能なYAML形式の.mdファイルとして自動的に整理・永続化する自律型エージェント。

## 📊 プロジェクト統計

- **MCP Tools**: 5 (web_content_fetcher, llm_structure_extractor, url_discovery_engine, file_system_manager, ldd_manager)
- **Sub-agents**: 5 (context-extractor, quality-analyzer, api-docs-specialist, tutorial-specialist, knowledge-base-specialist)
- **Slash Commands**: 3 (/extract-context, /setup-project, /generate-agent)
- **Supported Formats**: HTML, Markdown, YAML, JSON
- **GitHub Actions**: 5 workflows (CI/CD, PR Review, Issue Processing, Context Extraction, Docs Generation)

## 🚀 MVP実装ステータス

### Phase 1: MCP Server実装 ✅ 完了 (2025-08-03)

✅ **実装完了項目:**
- Core MCP server (Python/asyncio)
- 5つのツール実装完了
- Content extraction engine
- YAML generation pipeline
- LDD (Log-Driven Development) システム
- 包括的なテストスイート

### Phase 2: Claude Code統合 ✅ 完了 (2025-08-04)

✅ **実装完了項目:**
- [x] カスタムスラッシュコマンドの実装
- [x] Hooks configurationの設定
- [x] Sub-agent definitionsの作成
- [x] Local testing environmentの構築

### Phase 3: GitHub Actions自動化 ✅ 完了 (2025-08-04)

✅ **実装完了項目:**
- [x] CI/CDワークフローの実装
- [x] PR review automationの設定
- [x] Issue processing automationの実装
- [x] Documentation generationの自動化

## 📚 ドキュメント

- 📖 [Documentation Site](https://yaml-context-engineering.github.io) - 完全なドキュメント
- 🚀 [Getting Started Guide](docs/user-guide/quickstart.md) - クイックスタートガイド
- 🏗️ [Architecture Overview](docs/architecture/README.md) - システムアーキテクチャ
- 🔧 [API Reference](docs/api/mcp-tools.md) - API リファレンス
- 🤝 [Contributing Guide](CONTRIBUTING.md) - 貢献ガイドライン

## 🔧 セットアップ

### 前提条件

- Python 3.9以上
- pip (Pythonパッケージマネージャー)
- Git

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/yaml-context-engineering/agent.git
cd yaml-context-engineering-agent

# Python仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
cd mcp-server
pip install -e .

# Claude Code設定の確認
cat .claude/settings.json
```

## 🎯 使用方法

### Claude Code スラッシュコマンド

```bash
# URLからコンテキスト抽出
/extract-context https://docs.example.com/api

# 新規プロジェクトのセットアップ
/setup-project my-context-project

# 専門エージェントの生成
/generate-agent api-docs
```

### MCP ツール使用例

```python
# Claude Code内で使用
mcp__yaml-context-engineering__web_content_fetcher urls=["https://example.com"]
mcp__yaml-context-engineering__llm_structure_extractor content="..."
```

### CLI コマンド

```bash
# MCP サーバーの起動
yaml-context-mcp

# コンテキスト抽出（開発中）
yaml-context extract https://example.com

# LDD システム
yaml-context ldd init
yaml-context ldd task "Extract API docs"
```

## 🏗️ アーキテクチャ

```
yaml-context-engineering-agent/
├── .claude/                   # Claude Code 設定
│   ├── settings.json         # 統合設定
│   ├── commands/             # スラッシュコマンド
│   ├── agents/               # サブエージェント
│   └── hooks/                # フックスクリプト
├── .github/                  # GitHub Actions
│   └── workflows/            # 自動化ワークフロー
├── mcp-server/               # MCP サーバー実装
│   ├── src/                  # ソースコード
│   └── tests/                # テストスイート
├── generated_contexts/       # 生成されたコンテキスト
├── test-claude-code/         # テストスクリプト
└── config.yaml              # プロジェクト設定
```

## 🛠️ 開発

### テスト実行

```bash
# 統合テスト
./test-claude-code/test-integration.sh

# MCP サーバーテスト
cd mcp-server && pytest

# スラッシュコマンドテスト
./test-claude-code/test-slash-commands.sh
```

### コード品質

```bash
# リンティング
ruff check .

# フォーマット
black .

# 型チェック
mypy .
```

## 🔄 Phase 4: Advanced Features (次期開発)

- [ ] Quality analysis systemの実装
- [ ] Plugin architectureの開発
- [ ] Performance optimizationの実施
- [ ] Comprehensive testingの実施

## 📝 変更履歴

最新の変更については[CHANGELOG.md](CHANGELOG.md)を参照してください。

## 🤝 貢献

プロジェクトへの貢献を歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)をご覧ください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE.md](LICENSE.md)をご覧ください。

## 🙏 謝辞

- [Anthropic](https://anthropic.com) - Claude AI と MCP プロトコル
- [Model Context Protocol](https://modelcontextprotocol.io) - 標準化されたAI統合
- すべての貢献者とコミュニティメンバー