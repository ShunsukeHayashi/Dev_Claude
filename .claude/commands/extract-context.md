# /extract-context

Extract hierarchical context from sources and generate YAML documentation.

## Usage

```
/extract-context [sources...]
```

## Arguments

- `sources` - One or more URLs, file paths, or text snippets to extract context from

## Description

This command uses the YAML Context Engineering Agent to:

1. Analyze the provided sources
2. Extract hierarchical heading structures (L1, L2, L3)
3. Generate YAML frontmatter with metadata
4. Create organized context files in Markdown format
5. Save files to the `generated_contexts` directory

## Examples

```
/extract-context https://docs.example.com/api
/extract-context docs/*.md
/extract-context "Raw text to analyze"
```

## Implementation

When invoked with `$ARGUMENTS`, the command will execute the following workflow:

### Step 1: Parse Arguments
```javascript
const args = "$ARGUMENTS".trim();
if (!args) {
    console.error("❌ エラー: ソースを指定してください");
    console.log("使用方法: /extract-context <URL|file|text>");
    process.exit(1);
}

// URLパターンのチェック
const urlPattern = /^https?:\/\//;
const isUrl = urlPattern.test(args);

console.log("🚀 コンテキスト抽出を開始します");
console.log(`📍 ソース: ${args}`);
console.log(`📊 タイプ: ${isUrl ? 'URL' : 'ファイル/テキスト'}`);
```

### Step 2: Fetch Content
URLの場合はMCPツールを使用してコンテンツを取得:

```
# URLの場合
mcp__yaml-context-engineering__web_content_fetcher urls=["$ARGUMENTS"] timeout=30
```

ファイルの場合は読み込み:
```
# ファイルの場合
Read $ARGUMENTS
```

### Step 3: Extract Structure
取得したコンテンツから階層構造を抽出:

```
mcp__yaml-context-engineering__llm_structure_extractor content="$CONTENT" extraction_config={"granularity": "L1_L2", "summarization": "detailed"}
```

### Step 4: Generate YAML Documentation
構造化されたコンテンツをYAML形式で保存:

```javascript
// ファイル名の生成
const fileName = isUrl ? 
    new URL(args).hostname.replace(/\./g, '_') : 
    args.replace(/[^a-zA-Z0-9]/g, '_');

const outputPath = `generated_contexts/${fileName}.md`;
```

```
mcp__yaml-context-engineering__file_system_manager action="write_file" path="$OUTPUT_PATH" content={
    "title": "$TITLE",
    "source_url": "$SOURCE",
    "language": "$LANGUAGE",
    "body": "$CONTENT",
    "hierarchy_levels": $HIERARCHY,
    "extraction_confidence": $CONFIDENCE
}
```

### Step 5: Update Index
生成されたコンテキストのインデックスを更新:

```
mcp__yaml-context-engineering__file_system_manager action="generate_index"
```

### Step 6: Log to LDD
タスクの実行記録をLDDシステムに保存:

```
mcp__yaml-context-engineering__ldd_manager action="create_task" task_name="Context extraction: $SOURCE" status="Completed"
```

## Expected Output

成功すると以下のようなメッセージが表示されます:

```
✅ コンテキスト抽出が完了しました！
📄 ファイル: generated_contexts/example_com.md
📊 階層レベル: L1(3), L2(7), L3(12)
🎯 信頼度: 0.95
📁 インデックスが更新されました
```

## Error Handling

- **無効なURL**: URLの形式をチェックし、エラーメッセージを表示
- **ファイルが見つからない**: ファイルの存在を確認し、適切なエラーを表示
- **ネットワークエラー**: 3回までリトライし、失敗時は詳細なエラー情報を提供
- **構造抽出エラー**: フォールバックとして基本的な構造抽出を実行