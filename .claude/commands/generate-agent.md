# /generate-agent

Create specialized sub-agent for context extraction.

## Usage

```
/generate-agent [specialization]
```

## Arguments

- `specialization` - Type of specialized agent to create (e.g., "api-docs", "tutorial", "technical-spec")

## Description

This command generates a new specialized sub-agent tailored for specific types of context extraction:

1. **api-docs** - Optimized for API documentation extraction
2. **tutorial** - Focused on tutorial and guide content
3. **technical-spec** - Specialized for technical specifications
4. **knowledge-base** - Designed for knowledge base articles
5. **custom** - Create a custom agent with user-defined parameters

## Generated Files

```
.claude/agents/
└── [specialization]-agent.md
```

## Agent Template

Each generated agent includes:
- Custom system prompt
- Specialized tool permissions
- Extraction strategies
- Output formatting rules
- Quality criteria

## Examples

```
/generate-agent api-docs
/generate-agent tutorial
/generate-agent custom "Legal document analyzer"
```

## Implementation

When invoked with `$ARGUMENTS`, the command will execute:

### Step 1: Parse Specialization
```javascript
const args = "$ARGUMENTS".trim();
const specialization = args || "general";

// 定義済みの専門分野
const specializations = {
    "api-docs": "API Documentation Specialist",
    "tutorial": "Tutorial & Guide Specialist",
    "technical-spec": "Technical Specification Analyst",
    "knowledge-base": "Knowledge Base Curator",
    "general": "General Context Extractor",
    "custom": args // カスタムの場合は引数をそのまま使用
};

const agentName = specializations[specialization] || args;
const fileName = specialization.replace(/\s+/g, '-').toLowerCase();

console.log("🤖 専門エージェントを生成します");
console.log(`📊 専門分野: ${agentName}`);
console.log(`📄 ファイル名: ${fileName}-agent.md`);
```

### Step 2: Generate Agent Template
各専門分野に応じたエージェントテンプレートを生成:

#### API Documentation Specialist
```markdown
# ${agentName}

API ドキュメントの抽出と構造化に特化したエージェント。

## システムプロンプト

あなたはAPI ドキュメント抽出の専門家です。以下に焦点を当てます：

1. **エンドポイントの識別**
   - HTTP メソッド（GET, POST, PUT, DELETE）
   - URLパターン
   - パラメータとクエリ文字列

2. **リクエスト/レスポンス構造**
   - ヘッダー情報
   - ボディスキーマ
   - 認証要件

3. **コード例の抽出**
   - 言語別のサンプルコード
   - cURLコマンド
   - SDKの使用例

4. **エラーハンドリング**
   - HTTPステータスコード
   - エラーレスポンス形式
   - トラブルシューティング

## 抽出戦略

- エンドポイントごとに独立したセクションを作成
- パラメータテーブルの生成
- 認証フローの図解
- レート制限情報の強調

## 出力形式

\`\`\`yaml
---
title: "API Documentation - ${SOURCE}"
api_version: "${VERSION}"
base_url: "${BASE_URL}"
authentication: "${AUTH_TYPE}"
endpoints:
  - method: GET
    path: /api/v1/resource
    description: "..."
---
\`\`\`
```

#### Tutorial & Guide Specialist
```markdown
# ${agentName}

チュートリアルとガイドの構造化に特化したエージェント。

## システムプロンプト

あなたはチュートリアル構造化の専門家です：

1. **学習目標の抽出**
   - 前提条件
   - 到達目標
   - 必要なツール/環境

2. **ステップバイステップ構造**
   - 番号付きステップ
   - 各ステップの期待結果
   - トラブルシューティング

3. **実践的な例**
   - 動作するコード例
   - スクリーンショット参照
   - よくある間違い

## 抽出戦略

- 順序立てられた学習パスの構築
- 難易度レベルの識別
- 実践演習の抽出
- 関連リソースのリンク

## 品質基準

- ステップの完全性: 100%
- コード例の動作確認可能性
- 初心者への配慮
```

### Step 3: Write Agent File
```
Write .claude/agents/${fileName}-agent.md "${AGENT_TEMPLATE}"
```

### Step 4: Update Settings
settings.jsonにエージェントを登録:

```javascript
// 既存のsettings.jsonを読み込み
const settings = JSON.parse(Read(".claude/settings.json"));

// 新しいエージェントを追加
settings.sub_agents = settings.sub_agents || {};
settings.sub_agents[fileName] = {
    "file": `agents/${fileName}-agent.md`,
    "enabled": true,
    "specialization": specialization
};

// 更新されたsettingsを保存
Write(".claude/settings.json", JSON.stringify(settings, null, 2));
```

### Step 5: Create Usage Example
使用例を含むドキュメントを生成:

```
Write .claude/agents/${fileName}-usage.md '# ${agentName} 使用ガイド

## エージェントの呼び出し

\`\`\`
Task agent=${fileName} "Extract API documentation from https://api.example.com/docs"
\`\`\`

## 期待される出力

このエージェントは${specialization}に特化しており、以下を生成します：

- 構造化された${specialization}ドキュメント
- YAML frontmatterによるメタデータ
- 専門分野に最適化されたフォーマット

## カスタマイズ

エージェントファイル（\`.claude/agents/${fileName}-agent.md\`）を編集して、
抽出ルールやフォーマットをカスタマイズできます。'
```

### Step 6: Test Agent
生成されたエージェントをテスト:

```
# エージェントの動作確認
Task agent=${fileName} "Test extraction with sample content"
```

## Expected Output

エージェントが正常に生成されると:

```
✅ 専門エージェントが生成されました！
🤖 エージェント: API Documentation Specialist
📄 設定ファイル: .claude/agents/api-docs-agent.md
📚 使用ガイド: .claude/agents/api-docs-usage.md
⚙️  settings.json が更新されました

使用方法:
Task agent=api-docs "Extract from https://api.example.com"

カスタマイズ:
エージェントファイルを編集して動作を調整できます。
```

## Available Specializations

1. **api-docs** - API ドキュメント（エンドポイント、パラメータ、レスポンス）
2. **tutorial** - チュートリアルとハウツーガイド
3. **technical-spec** - 技術仕様書（アーキテクチャ、設計）
4. **knowledge-base** - ナレッジベース記事（FAQ、トラブルシューティング）
5. **custom** - カスタム専門分野（任意の名前を指定）