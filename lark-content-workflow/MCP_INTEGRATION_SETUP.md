# 🔧 Claude Desktop MCP 統合設定ガイド

## 📋 MCP サーバー統合手順

### Step 1: Claude Desktop 設定ファイル更新

#### macOS の場合
```bash
# 設定ファイルパス
~/.claude/claude_desktop_config.json

# または
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Windows の場合  
```bash
# 設定ファイルパス
%APPDATA%/Claude/claude_desktop_config.json
```

### Step 2: MCP 設定追加

既存の設定ファイルに以下を追加：

```json
{
  "mcpServers": {
    "lark-content-workflow": {
      "command": "node",
      "args": ["/Users/shunsuke/Dev/Dev_Claude/lark-content-workflow/src/mcp-server.js"],
      "env": {
        "LARK_APP_ID": "cli_a8d2fdb1f1f8d02d",
        "LARK_APP_SECRET": "V7mzILXEgIaqLwLXtyZstekRJsjRsFfJ", 
        "LARK_BASE_APP_TOKEN": "WaTCbnKSiaJvMcs3cdPjxobKp8C",
        "LARK_BASE_TABLE_ID": "tblvQlQXva14zQpa"
      }
    }
  }
}
```

### Step 3: Claude Desktop 再起動
1. Claude Desktop を完全に終了
2. アプリケーションを再起動
3. MCP接続の確認

---

## 🛠️ 利用可能なMCPツール

### 1. start_content_workflow
**用途**: コンテンツ生成ワークフローの開始
```json
{
  "topic": "Claude Code導入ガイド",
  "parameters": {
    "style": "professional",
    "length": "medium",
    "language": "ja"
  },
  "larkConfig": {
    "assignedWriter": "ハヤシシュンスケ"
  }
}
```

### 2. get_workflow_status  
**用途**: ワークフロー進捗の確認
```json
{
  "workflowId": "wf_20250811_001"
}
```

### 3. get_lark_records
**用途**: Lark Baseレコードの取得
```json
{
  "pageSize": 10,
  "filter": "status:新規"
}
```

### 4. create_lark_record
**用途**: 新規レコードの作成
```json
{
  "fields": {
    "記事タイトル": "新規記事タイトル",
    "ステータス": "新規",
    "執筆フェーズ": "調査"
  }
}
```

### 5. update_lark_record
**用途**: 既存レコードの更新
```json
{
  "recordId": "rec_xxxxx", 
  "fields": {
    "ステータス": "完了",
    "SEOスコア": 85
  }
}
```

### 6. setup_lark_base
**用途**: Lark Base初期セットアップ
```json
{
  "force": false
}
```

### 7. get_server_health
**用途**: サーバー状態確認
```json
{}
```

---

## 🎯 実用的な使用例

### SEO記事最適化ワークフロー
```
Claude Desktop で以下のように実行:

"Claude Code Windows環境での使い方について、
SEO最適化された記事を作成してください。
start_content_workflowツールを使用して、
professional スタイルで medium 長さの記事を生成し、
進捗をリアルタイムで追跡してください。"
```

### Lark Base データ管理
```
"現在のSEO最適化タスクの進捗を確認してください。
get_lark_records ツールで記事投稿記録を取得し、
完了率を計算してレポートを作成してください。"
```

### パフォーマンス監視
```
"システムの健康状態を確認してください。
get_server_health ツールを使用して、
SSE接続数、Lark Base接続状態、
サーバーリソース使用状況をレポートしてください。"
```

---

## 🔍 トラブルシューティング

### よくある問題

#### 1. MCP サーバーが認識されない
```bash
# 原因: Node.jsパスの問題
# 解決: 絶対パスを使用
"command": "/usr/local/bin/node"  # または which node の結果

# 設定確認
which node
node --version  # v16.0.0以上必要
```

#### 2. 環境変数エラー
```bash
# 原因: 環境変数が正しく設定されていない
# 解決: .env ファイルから値をコピー
cat /Users/shunsuke/Dev/Dev_Claude/lark-content-workflow/.env
```

#### 3. Lark API認証エラー
```bash
# 原因: App ID/Secret の期限切れ
# 解決: Lark Developer Console で確認
# https://open.larksuite.com/
```

#### 4. ポート競合エラー
```bash
# 原因: 他のプロセスがポートを使用
# 解決: プロセス確認と終了
lsof -ti:3001 | xargs kill -9
```

### 設定確認コマンド
```bash
# MCP サーバー単体テスト
cd /Users/shunsuke/Dev/Dev_Claude/lark-content-workflow
npm run mcp

# Lark Base接続テスト  
npm test

# 依存関係確認
npm list --depth=0
```

---

## 📊 統合完了の確認方法

### 1. Claude Desktop UI確認
- ツールリストにMCPツールが表示される
- エラーメッセージが表示されない
- ツール実行が正常に動作する

### 2. ログ確認
```bash
# Claude Desktop ログ（macOS）
tail -f ~/Library/Logs/Claude/claude.log

# MCPサーバーログ
npm run mcp 2>&1 | tee mcp-server.log
```

### 3. 動作テスト
```bash
# ヘルスチェック
curl http://localhost:3001/health

# MCP サーバー応答確認
echo '{"method":"tools/list"}' | node src/mcp-server.js
```

---

## 🚀 次のステップ

### 1. SEO最適化の自動化
- 100項目タスクリストとMCP統合
- ワークフロー実行の自動化
- パフォーマンス追跡の自動化

### 2. チーム協業の強化  
- 複数ライターのタスク管理
- リアルタイム進捗共有
- 品質管理の自動化

### 3. システム拡張
- カスタムMCPツールの開発
- 他のプラットフォーム統合
- AI機能の強化

---

**🎯 MCP統合が完了すれば、Claude DesktopからLark Baseを直接操作し、SEO最適化ワークフローを効率的に管理できるようになります！**

*設定完了後、Claude Desktopでツールが利用可能になったかお知らせください。*