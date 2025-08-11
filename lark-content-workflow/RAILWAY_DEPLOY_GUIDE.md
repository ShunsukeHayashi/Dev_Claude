# 🚀 Railway 本番デプロイ実行ガイド

## 📋 デプロイ手順（ブラウザで実行）

### Step 1: Railway アカウント作成
1. **Railway サイトにアクセス**: https://railway.app/
2. **GitHubでサインアップ**: "Sign up with GitHub" をクリック
3. **権限承認**: GitHubアカウントへのアクセスを許可

### Step 2: プロジェクト作成
1. **New Project をクリック**
2. **Deploy from GitHub repo を選択**
3. **リポジトリ選択**: `ShunsukeHayashi/Dev_Claude` を選択
4. **サブディレクトリ指定**: `lark-content-workflow` を指定

### Step 3: 環境変数設定
Variables タブで以下を設定：

```bash
# 必須環境変数
LARK_APP_ID=cli_a8d2fdb1f1f8d02d
LARK_APP_SECRET=V7mzILXEgIaqLwLXtyZstekRJsjRsFfJ
LARK_BASE_APP_TOKEN=WaTCbnKSiaJvMcs3cdPjxobKp8C
LARK_BASE_TABLE_ID=tblvQlQXva14zQpa

# サーバー設定
NODE_ENV=production
PORT=$PORT

# オプション設定
SSE_HEARTBEAT_INTERVAL=30000
SSE_MAX_CONNECTIONS=100
CORS_ORIGIN=*
```

### Step 4: デプロイ実行
1. **Deploy ボタンをクリック**
2. **ビルドログを確認**
3. **成功を待機** (通常2-3分)

### Step 5: デプロイ後確認
生成されたURLで以下をテスト：

```bash
# ヘルスチェック
curl https://your-app.railway.app/health

# Expected Response:
{
  "status": "healthy",
  "activeConnections": 0,
  "larkBase": {
    "connected": true,
    "appToken": "configured"
  },
  "timestamp": "2025-08-11T14:20:00.000Z"
}
```

---

## 🔧 代替デプロイ方法

### Option A: Vercel (フロントエンド特化)
```bash
# ターミナルで実行
vercel login
vercel --prod

# 環境変数はVercel Web UIで設定
```

### Option B: Docker Compose (セルフホスト)
```bash
# 本番環境変数ファイル作成
cp .env.example .env.production
# .env.production を編集

# Docker起動
docker-compose up -d

# ヘルスチェック
curl http://localhost:3001/health
```

---

## 📊 デプロイ成功後のアクション

### 1. MCP統合設定
Claude Desktop設定ファイル更新:
```json
{
  "mcpServers": {
    "lark-content-workflow": {
      "command": "node",
      "args": ["/path/to/lark-content-workflow/src/mcp-server.js"],
      "env": {
        "LARK_APP_ID": "cli_a8d2fdb1f1f8d02d",
        "LARK_APP_SECRET": "V7mzILXEgIaqLwLXtyZstekRJsjRsFfJ",
        "LARK_BASE_APP_TOKEN": "WaTCbnKSiaJvMcs3cdPjxobKp8C"
      }
    }
  }
}
```

### 2. SSE動作確認
```bash
# SSEストリーム接続テスト
curl -H "Accept: text/event-stream" \
     https://your-app.railway.app/api/workflow/stream

# ワークフロー開始テスト
curl -X POST https://your-app.railway.app/api/workflow/start \
     -H "Content-Type: application/json" \
     -d '{"topic":"テストワークフロー","parameters":{"style":"professional"}}'
```

### 3. Lark Base 動作確認
```bash
# レコード取得テスト
curl https://your-app.railway.app/api/lark/records

# レコード作成テスト
curl -X POST https://your-app.railway.app/api/lark/records \
     -H "Content-Type: application/json" \
     -d '{"fields":{"記事タイトル":"テスト記事","ステータス":"新規"}}'
```

---

## 🎯 成功後の次のステップ

### 1. SEO最適化タスクの実行開始
- `assign_Tasks.md` の100項目タスクリストを活用
- ワークフローによる自動化でSEO効率向上
- Lark Baseでの進捗管理とKPI追跡

### 2. チーム運用開始
- ライター、SEOスペシャリスト、データアナリストのアサイン
- 週次レビュー体制の確立
- パフォーマンス監視ダッシュボードの活用

### 3. システム拡張
- 追加MCPツールの開発
- カスタムワークフローの作成
- API連携の拡張

---

## 📞 サポート情報

### トラブルシューティング
| 問題 | 解決方法 |
|------|----------|
| ビルド失敗 | package.jsonの依存関係を確認 |
| 環境変数エラー | Railway Variables設定を再確認 |
| Lark API エラー | App ID/Secret の有効性を確認 |
| 404エラー | railway.json の設定を確認 |

### 成功指標
- ✅ ヘルスチェック: HTTP 200
- ✅ SSE接続: イベントストリーム受信
- ✅ Lark Base: レコード操作成功
- ✅ MCP: Claude Desktopで利用可能

---

**🎉 デプロイが完了したら、生成されたURLを共有してください！**

Railway生成URL例: `https://your-project-name-production.railway.app`