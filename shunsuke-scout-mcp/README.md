# Shunsuke Scout MCP - シュンスケ式諜報MCPサーバー

🕵️ **ShunsukeModel / ScoutUnit / v1.0.0**

多様な情報源からピッチの状況を正確に把握し、司令塔が参照可能なYAML形式の戦術データとして構造化・永続化する自律型諜報・分析ユニット。シュンスケ式戦術遂行モデルの中核を担う、階層的コンテキスト抽出MCPサーバー。

## ✨ 特徴

- 🌐 **ウェブクローリング**: URLから自動的にコンテンツを取得
- 📊 **階層構造抽出**: L1, L2, L3などの見出し構造を自動識別
- 📝 **YAMLフロントマター**: メタデータを含む構造化されたドキュメント生成
- 🔍 **品質分析**: 抽出されたコンテンツの品質を自動評価
- 🔌 **プラグインシステム**: 拡張可能なアーキテクチャ
- 🤖 **Claude統合**: Claude CodeとClaude Desktopとの完全統合
- 📚 **LDD (Log-Driven Development)**: ログベースの開発サポート

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/yaml-context-engineering.git
cd yaml-context-engineering
```

### 2. 仮想環境の作成と依存関係のインストール

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Claude Desktop設定

Claude Desktopの設定ファイルに以下を追加:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "yaml-context-engineering": {
      "command": "python3",
      "args": ["-m", "yaml_context_engineering.main"],
      "cwd": "/Users/your-username/Dev/yaml-context-engineering",
      "env": {
        "PYTHONPATH": "/Users/your-username/Dev/yaml-context-engineering/src",
        "MCP_OUTPUT_DIRECTORY": "/Users/your-username/generated_contexts"
      }
    }
  }
}
```

### 4. Claude Code設定（グローバル）

`~/.claude/settings.json`に同様の設定を追加

## 📖 使い方

### Claude Codeでの使用

グローバルスラッシュコマンドが利用可能:

```bash
# コンテキストを抽出
/extract-context https://example.com/docs

# 品質を分析
/analyze-quality generated_contexts/

# プロジェクトをセットアップ
/setup-yaml-context my-project
```

### Claude Desktopでの使用

MCPツールが自動的に利用可能になります。

## ツール

### web_content_fetcher

指定されたURLからウェブページのコンテンツを取得します。

```json
{
  "tool": "web_content_fetcher",
  "params": {
    "urls": ["https://example.com"],
    "timeout": 30
  }
}
```

### llm_structure_extractor

テキストコンテンツから階層的な見出し構造を抽出します。

```json
{
  "tool": "llm_structure_extractor",
  "params": {
    "content": "...",
    "target_schema": {},
    "extraction_config": {}
  }
}
```

### url_discovery_engine

コンテンツから関連URLを発見し、優先度付きで返します。

```json
{
  "tool": "url_discovery_engine",
  "params": {
    "content": "...",
    "base_domain": "example.com",
    "filters": []
  }
}
```

### file_system_manager

ディレクトリ作成、ファイル書き込み、パス管理を行います。

## 開発

### 依存関係のインストール

```bash
pip install -r requirements.txt
```

### テストの実行

```bash
pytest
```

### コードフォーマット

```bash
black src/ tests/
```

## ライセンス

MIT License