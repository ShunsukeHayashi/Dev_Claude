"""MCP Server implementation for YAML Context Engineering."""

import asyncio
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .config import Config
from .utils.logging import get_logger, console
from .tools import (
    WebContentFetcher,
    LLMStructureExtractor,
    URLDiscoveryEngine,
    FileSystemManager
)
from .tools.ldd_manager import LDDManagerTool, LDD_MANAGER_TOOL
from .tools.quality_analyzer_tool import QualityAnalyzerTool
from .ldd import LDDConfig


class YamlContextServer:
    """YAML Context Engineering MCP Server."""
    
    def __init__(self, config: Config):
        """Initialize the server.
        
        Args:
            config: Server configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.server = Server("shunsuke-scout-mcp")
        
        # Initialize tools
        self.web_fetcher = WebContentFetcher(config)
        self.structure_extractor = LLMStructureExtractor(config)
        self.url_discovery = URLDiscoveryEngine(config)
        self.file_manager = FileSystemManager(config)
        
        # Initialize LDD system
        ldd_config = LDDConfig(
            logsDir=str(config.output.output_base_directory / 'logs'),
            memoryBankPath=str(config.output.output_base_directory / '@memory-bank.md'),
            templatePath=str(config.output.output_base_directory / '@logging_template.md')
        )
        self.ldd_manager = LDDManagerTool(ldd_config)
        
        # Initialize Quality Analyzer
        self.quality_analyzer = QualityAnalyzerTool(str(config.output.output_base_directory))
        
        # Setup handlers
        self._setup_handlers()
        
        self.logger.info("YAML Context Engineering MCP Server initialized", 
                        config=config.__dict__)
    
    def _setup_handlers(self) -> None:
        """Set up tool execution handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            tools = [
                Tool(
                    name="web_content_fetcher",
                    description="指定されたURLからウェブページのコンテンツを取得",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "取得するURLのリスト"
                            },
                            "timeout": {
                                "type": "integer",
                                "default": 30,
                                "description": "タイムアウト秒数"
                            }
                        },
                        "required": ["urls"]
                    }
                ),
                Tool(
                    name="llm_structure_extractor",
                    description="テキストコンテンツから階層的な見出し構造を抽出",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "解析するテキストコンテンツ"
                            },
                            "target_schema": {
                                "type": "object",
                                "description": "目標とする構造スキーマ"
                            },
                            "extraction_config": {
                                "type": "object",
                                "description": "抽出設定"
                            }
                        },
                        "required": ["content"]
                    }
                ),
                Tool(
                    name="url_discovery_engine",
                    description="コンテンツから関連URLを発見し、優先度付きで返す",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "URLを探すコンテンツ"
                            },
                            "base_domain": {
                                "type": "string",
                                "description": "基準となるドメイン"
                            },
                            "filters": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "URLフィルターパターン"
                            }
                        },
                        "required": ["content", "base_domain"]
                    }
                ),
                Tool(
                    name="file_system_manager",
                    description="ディレクトリ作成、ファイル書き込み、パス管理",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["create_directory", "write_file", "sanitize_path", "generate_index"],
                                "description": "実行するアクション"
                            },
                            "path": {
                                "type": "string",
                                "description": "操作対象のパス"
                            },
                            "content": {
                                "type": "string",
                                "description": "書き込む内容（write_fileの場合）"
                            }
                        },
                        "required": ["action"]
                    }
                ),
                Tool(
                    name="ldd_manager",
                    description=LDD_MANAGER_TOOL["description"],
                    inputSchema=LDD_MANAGER_TOOL["inputSchema"]
                ),
                Tool(
                    name="quality_analyzer",
                    description="Analyze the quality of extracted context files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["analyze_file", "analyze_directory", "compare_files", "suggest_improvements"],
                                "description": "The quality analysis action to perform"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to analyze"
                            },
                            "directory_path": {
                                "type": "string",
                                "description": "Path to directory to analyze"
                            },
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of file paths to compare"
                            },
                            "severity_filter": {
                                "type": "string",
                                "enum": ["all", "critical", "high", "medium", "low"],
                                "default": "all",
                                "description": "Filter issues by severity level"
                            }
                        },
                        "required": ["action"]
                    }
                )
            ]
            return tools
        
        @self.server.call_tool()
        async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            """Handle tool execution requests."""
            self.logger.info(f"Tool called: {name}", arguments=arguments)
            
            try:
                if name == "web_content_fetcher":
                    result = await self.web_fetcher.fetch(
                        urls=arguments["urls"],
                        timeout=arguments.get("timeout", 30)
                    )
                elif name == "llm_structure_extractor":
                    result = await self.structure_extractor.extract(
                        content=arguments["content"],
                        target_schema=arguments.get("target_schema", {}),
                        extraction_config=arguments.get("extraction_config", {})
                    )
                elif name == "url_discovery_engine":
                    result = await self.url_discovery.discover(
                        content=arguments["content"],
                        base_domain=arguments["base_domain"],
                        filters=arguments.get("filters", [])
                    )
                elif name == "file_system_manager":
                    result = await self.file_manager.execute(
                        action=arguments["action"],
                        path=arguments.get("path"),
                        content=arguments.get("content")
                    )
                elif name == "ldd_manager":
                    result = await self.ldd_manager.execute(
                        action=arguments["action"],
                        **{k: v for k, v in arguments.items() if k != "action"}
                    )
                elif name == "quality_analyzer":
                    result = await self.quality_analyzer.execute(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                self.logger.info(f"Tool executed successfully: {name}")
                return [{"content": json.dumps(result, ensure_ascii=False)}]
                
            except Exception as e:
                self.logger.error(f"Tool execution failed: {name}", error=str(e))
                raise Exception(f"Tool execution failed: {name} - {str(e)}")
    
    async def run(self, host: str = "localhost", port: int = 3000) -> None:
        """Run the MCP server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        console.info(f"Starting YAML Context Engineering MCP Server")
        console.info(f"Server: {self.config.server_name} v{self.config.server_version}")
        
        try:
            # Create output directory if it doesn't exist
            self.config.output.output_base_directory.mkdir(parents=True, exist_ok=True)
            
            # Run the server
            async with stdio_server() as (read_stream, write_stream):
                console.success("MCP Server started successfully")
                console.info("Waiting for client connections...")
                
                await self.server.run(
                    read_stream,
                    write_stream,
                    server_params={
                        "name": self.config.server_name,
                        "version": self.config.server_version
                    }
                )
                
        except KeyboardInterrupt:
            console.warning("Server stopped by user")
        except Exception as e:
            console.error(f"Server error: {e}")
            raise