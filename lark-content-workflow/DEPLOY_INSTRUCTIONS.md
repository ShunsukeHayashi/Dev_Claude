# 🚀 簡単デプロイメント手順

Railway CLIのログインが対話式のため、以下の代替手順でデプロイを実行してください。

## 📋 推奨デプロイメント方法

### オプション1: Railway Web UI (推奨)
```bash
# 1. https://railway.app/ にブラウザでアクセス
# 2. GitHubアカウントでサインアップ/ログイン  
# 3. "Deploy from GitHub repo" を選択
# 4. このリポジトリを連携
# 5. 環境変数を設定:
```

**設定する環境変数:**
```
LARK_APP_ID=cli_a8d2fdb1f1f8d02d
LARK_APP_SECRET=V7mzILXEgIaqLwLXtyZstekRJsjRsFfJ
LARK_BASE_APP_TOKEN=WaTCbnKSiaJvMcs3cdPjxobKp8C  
LARK_BASE_TABLE_ID=tblvQlQXva14zQpa
NODE_ENV=production
```

### オプション2: Vercel デプロイ
```bash
# ログインして実行
vercel login
vercel --prod

# 環境変数設定
vercel env add LARK_APP_ID production
vercel env add LARK_APP_SECRET production
vercel env add LARK_BASE_APP_TOKEN production
vercel env add LARK_BASE_TABLE_ID production
```

### オプション3: ローカル本番環境テスト
```bash
# Docker使用
docker-compose up -d

# または直接起動
NODE_ENV=production npm start
```

## 🔧 Railway手動デプロイ手順

ブラウザで以下の手順を実行：

### 1. Railway アカウント作成
- https://railway.app/ にアクセス
- "Sign up with GitHub" をクリック
- GitHubアカウントで認証

### 2. プロジェクト作成  
- "New Project" をクリック
- "Deploy from GitHub repo" を選択
- このリポジトリ (`lark-content-workflow`) を選択

### 3. 環境変数設定
Variables タブで以下を設定：
```
LARK_APP_ID=cli_a8d2fdb1f1f8d02d
LARK_APP_SECRET=V7mzILXEgIaqLwLXtyZstekRJsjRsFfJ
LARK_BASE_APP_TOKEN=WaTCbnKSiaJvMcs3cdPjxobKp8C
LARK_BASE_TABLE_ID=tblvQlQXva14zQpa
NODE_ENV=production
PORT=$PORT
```

### 4. デプロイ確認
- Deployments タブで進行状況を確認
- 完了後、生成されたURLでアクセステスト
- `/health` エンドポイントで正常性確認

## ✅ デプロイ後の確認項目

```bash
# 1. ヘルスチェック
curl https://your-app-url.railway.app/health

# 2. SSE接続テスト  
curl -H "Accept: text/event-stream" https://your-app-url.railway.app/api/workflow/stream

# 3. Lark Base接続確認
curl https://your-app-url.railway.app/api/lark/records

# 4. ワークフロー開始テスト
curl -X POST https://your-app-url.railway.app/api/workflow/start \
  -H "Content-Type: application/json" \
  -d '{"topic":"テストワークフロー","parameters":{"style":"professional"}}'
```

## 🔍 トラブルシューティング

### よくある問題
1. **環境変数エラー**: Railway/Vercelの Variables 設定を再確認
2. **Lark API エラー**: App ID/Secret の有効性を確認  
3. **タイムアウト**: railway.json の healthcheckTimeout を延長

### ログ確認方法
```bash
# Railway: Web UIのLogs タブで確認
# Vercel: vercel logs コマンド
# Docker: docker-compose logs -f
```

---

## 🎯 次のステップ

1. ✅ デプロイメント完了
2. 🔧 Claude Desktop MCP 統合設定
3. 📊 SEO最適化タスクの実行開始
4. 📈 パフォーマンス監視設定

**成功したら、生成されたURLを教えてください！**