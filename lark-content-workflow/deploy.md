# 🚀 Lark Content Workflow - Deployment Guide

SSE MCP ツールの本番環境デプロイメントガイド

## 📋 デプロイメント概要

### システム構成
- **SSEサーバー**: リアルタイムコンテンツワークフロー
- **MCPサーバー**: Claude Code統合用のModel Context Protocol
- **Lark Base統合**: データ管理とタスク追跡
- **マルチプラットフォーム**: Railway、Vercel、Docker対応

---

## 🎯 デプロイメントオプション

### Option 1: Railway (推奨)
```bash
# 1. Railway CLI インストール
npm install -g @railway/cli

# 2. ログイン
railway login

# 3. プロジェクト作成
railway new

# 4. 環境変数設定
railway variables set LARK_APP_ID=cli_a8d2fdb1f1f8d02d
railway variables set LARK_APP_SECRET=V7mzILXEgIaqLwLXtyZstekRJsjRsFfJ
railway variables set LARK_BASE_APP_TOKEN=WaTCbnKSiaJvMcs3cdPjxobKp8C
railway variables set LARK_BASE_TABLE_ID=tblvQlQXva14zQpa
railway variables set NODE_ENV=production

# 5. デプロイ実行
railway up
```

### Option 2: Vercel
```bash
# 1. Vercel CLI インストール
npm install -g vercel

# 2. デプロイ
vercel --prod

# 3. 環境変数設定
vercel env add LARK_APP_ID production
vercel env add LARK_APP_SECRET production
vercel env add LARK_BASE_APP_TOKEN production
vercel env add LARK_BASE_TABLE_ID production
```

### Option 3: Docker
```bash
# 1. イメージビルド
docker build -t lark-content-workflow .

# 2. 環境変数ファイル作成
echo "LARK_APP_ID=cli_a8d2fdb1f1f8d02d" > .env.production
echo "LARK_APP_SECRET=V7mzILXEgIaqLwLXtyZstekRJsjRsFfJ" >> .env.production
echo "LARK_BASE_APP_TOKEN=WaTCbnKSiaJvMcs3cdPjxobKp8C" >> .env.production
echo "LARK_BASE_TABLE_ID=tblvQlQXva14zQpa" >> .env.production

# 3. コンテナ起動
docker run -p 3001:3001 --env-file .env.production lark-content-workflow

# または Docker Compose使用
docker-compose up -d
```

---

## 🔧 MCP サーバー設定

### Claude Desktop 統合

#### 1. MCP設定ファイル更新
```json
{
  "mcpServers": {
    "lark-content-workflow": {
      "command": "node",
      "args": ["/path/to/lark-content-workflow/src/mcp-server.js"],
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

#### 2. Claude Code グローバル設定
```bash
# ~/.claude/commands/ ディレクトリに配置
cp src/mcp-server.js ~/.claude/commands/lark-content-workflow-mcp.js
```

#### 3. 利用可能なMCPツール
- `start_content_workflow`: コンテンツワークフロー開始
- `get_workflow_status`: ワークフロー状況確認
- `get_lark_records`: Lark Baseレコード取得
- `create_lark_record`: レコード作成
- `update_lark_record`: レコード更新
- `setup_lark_base`: Lark Base初期化
- `get_server_health`: サーバー状況確認

---

## 📊 本番環境設定

### 環境変数一覧
```bash
# 必須設定
LARK_APP_ID=cli_a8d2fdb1f1f8d02d
LARK_APP_SECRET=V7mzILXEgIaqLwLXtyZstekRJsjRsFfJ
LARK_BASE_APP_TOKEN=WaTCbnKSiaJvMcs3cdPjxobKp8C
LARK_BASE_TABLE_ID=tblvQlQXva14zQpa

# サーバー設定
NODE_ENV=production
PORT=3001

# SSE設定
SSE_HEARTBEAT_INTERVAL=30000
SSE_MAX_CONNECTIONS=100
SSE_TIMEOUT=300000

# CORS設定
CORS_ORIGIN=https://your-domain.com

# 追加のテーブルID（セットアップ後）
ARTICLES_TABLE_ID=tbl6Lcel9u6C1N3A
KEYWORDS_TABLE_ID=tblBryNkDdCXzRu2
COMPETITORS_TABLE_ID=tbl6Agoi8jnIEJka
PERFORMANCE_TABLE_ID=tblj1iioooENpi3C
WRITERS_TABLE_ID=tbljQt7FRHUxYqQl
```

### パフォーマンス最適化
```bash
# Node.js メモリ設定
NODE_OPTIONS='--max-old-space-size=2048'

# プロセス管理 (PM2使用時)
pm2 start src/server.js --name lark-content-workflow -i max
pm2 startup
pm2 save
```

---

## 🏥 ヘルスチェック・監視

### エンドポイント
```bash
# ヘルスチェック
curl https://your-domain.com/health

# SSE接続テスト
curl -H "Accept: text/event-stream" https://your-domain.com/api/workflow/stream

# Lark Base接続テスト
curl https://your-domain.com/api/lark/records
```

### 監視設定
```yaml
# アラート条件
Metrics:
  - Response time > 5秒
  - Error rate > 1%
  - SSE connections > 80
  - Memory usage > 90%
  - Disk space > 85%

Notifications:
  - Email: ops@your-domain.com
  - Lark: システム運用チャネル
  - SMS: 緊急時のみ
```

---

## 🔒 セキュリティ設定

### HTTPS設定
```bash
# Let's Encrypt証明書 (Nginxプロキシ使用時)
certbot --nginx -d your-domain.com

# Or Railway/Vercelの自動HTTPS使用
```

### ファイアウォール
```bash
# ポート3001のみ開放
ufw allow 3001/tcp
ufw enable
```

### ログ設定
```bash
# ログローテーション
echo "/var/log/lark-content-workflow/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 www-data www-data
}" > /etc/logrotate.d/lark-content-workflow
```

---

## 🚀 デプロイメント実行

### 事前チェックリスト
- [ ] 環境変数が正しく設定されている
- [ ] Lark Base認証情報が有効
- [ ] テスト実行が成功している
- [ ] ドメイン・DNS設定完了
- [ ] SSL証明書設定完了

### デプロイ実行手順

#### Railway デプロイ
```bash
# 1. プロジェクトディレクトリに移動
cd lark-content-workflow

# 2. 依存関係チェック
npm audit fix

# 3. テスト実行
npm test

# 4. Railway デプロイ
railway up

# 5. ヘルスチェック
curl https://your-railway-app.railway.app/health
```

#### デプロイ後確認
```bash
# 1. サーバー起動確認
curl https://your-domain.com/health

# 2. SSE機能確認
curl -H "Accept: text/event-stream" https://your-domain.com/api/workflow/stream

# 3. MCP サーバー確認  
npm run mcp

# 4. Lark Base 接続確認
curl https://your-domain.com/api/lark/records
```

---

## 📝 運用手順

### 日常監視項目
```bash
# 毎日確認
- [ ] ヘルスチェックエンドポイントの応答
- [ ] SSE接続数
- [ ] エラーログの確認
- [ ] リソース使用率

# 週次確認  
- [ ] パフォーマンス指標レビュー
- [ ] セキュリティアップデート
- [ ] バックアップ状況確認
```

### トラブルシューティング
```bash
# ログ確認
tail -f logs/application.log

# プロセス確認
ps aux | grep node

# メモリ使用量確認
free -h

# ディスク使用量確認
df -h

# ネットワーク接続確認
netstat -tlnp
```

---

## 📞 サポート連絡先

- **技術サポート**: dev-team@your-domain.com
- **運用サポート**: ops-team@your-domain.com
- **緊急時**: +81-XX-XXXX-XXXX

## 📚 関連リンク

- [Lark Open API ドキュメント](https://open.larksuite.com/document/)
- [Railway デプロイガイド](https://docs.railway.app/)
- [MCP プロトコル仕様](https://modelcontextprotocol.io/)
- [Claude Code 統合ガイド](https://docs.anthropic.com/en/docs/claude-code)

---

*最終更新: 2025-08-11*  
*バージョン: 1.0.0*