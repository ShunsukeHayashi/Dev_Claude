"""Main entry point for YAML Context Engineering MCP Server."""

import asyncio
import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Add src directory to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from yaml_context_engineering.server import YamlContextServer
from yaml_context_engineering.config import Config

# Configure logging to stderr (stdout is used for MCP communication)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(
            Path.home() / '.claude' / 'logs' / 'yaml-context-engineering.log',
            mode='a'
        )
    ]
)

logger = logging.getLogger(__name__)


def get_output_directory() -> Path:
    """Get the output directory from environment or default."""
    # Check environment variable first
    env_dir = os.getenv('MCP_OUTPUT_DIRECTORY')
    if env_dir:
        return Path(env_dir)
    
    # Check if we're in a project with generated_contexts
    local_dir = Path.cwd() / 'generated_contexts'
    if local_dir.exists():
        return local_dir
    
    # Default to home directory
    return Path.home() / 'generated_contexts'


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting YAML Context Engineering MCP Server")
    
    # Ensure log directory exists
    log_dir = Path.home() / '.claude' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Get configuration from environment
    output_dir = get_output_directory()
    logger.info(f"Output directory: {output_dir}")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create configuration
    config = Config.from_env()
    config.output.output_base_directory = output_dir
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Create and run server
    server = YamlContextServer(config)
    
    try:
        # Run the server with STDIO transport
        logger.info("MCP Server is running in STDIO mode...")
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    # Handle module execution (-m flag)
    if len(sys.argv) > 1 and sys.argv[1] == "-m":
        sys.argv.pop(1)
    
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)