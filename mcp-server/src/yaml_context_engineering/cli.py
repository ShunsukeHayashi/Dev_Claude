"""CLI interface for YAML Context Engineering."""

import asyncio
import sys
import click
from pathlib import Path
from typing import Optional

from .server import YamlContextServer
from .config import Config
from .utils.logging import console, setup_logging


@click.group()
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """YAML Context Engineering CLI."""
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level, structured=False)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('url')
@click.option('--output-dir', '-o', type=Path, help='Output directory')
@click.option('--depth', '-d', type=int, default=2, help='Crawl depth')
async def extract(url: str, output_dir: Optional[Path], depth: int) -> None:
    """Extract context from URL."""
    config = Config.from_env()
    
    if output_dir:
        config.output.output_base_directory = output_dir
    if depth:
        config.crawling.max_crawl_depth = depth
    
    server = YamlContextServer(config)
    
    try:
        # Use the web content fetcher
        console.info(f"Fetching content from {url}...")
        results = await server.web_fetcher.fetch([url])
        
        if not results or not results[0]["success"]:
            console.error(f"Failed to fetch {url}")
            sys.exit(1)
        
        # Extract structure
        console.info("Extracting hierarchical structure...")
        structure = await server.structure_extractor.extract(results[0]["content"])
        
        # Save to file
        console.info("Generating YAML documentation...")
        filename = Path(url).name or "extracted"
        await server.file_manager.execute(
            "write_file",
            f"{filename}.md",
            {
                "title": results[0].get("title", "Extracted Content"),
                "source_url": url,
                "language": results[0].get("language", "unknown"),
                "body": results[0]["content"],
                "hierarchy_levels": structure.get("hierarchy_levels", [])
            }
        )
        
        console.success(f"✅ Context extracted to: {config.output.output_base_directory}/{filename}.md")
        
    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)
    finally:
        await server.web_fetcher.close()


@cli.command()
@click.argument('file', type=Path)
@click.option('--output-dir', '-o', type=Path, help='Output directory')
async def analyze(file: Path, output_dir: Optional[Path]) -> None:
    """Analyze local file structure."""
    if not file.exists():
        console.error(f"File not found: {file}")
        sys.exit(1)
    
    config = Config.from_env()
    if output_dir:
        config.output.output_base_directory = output_dir
    
    server = YamlContextServer(config)
    
    try:
        # Read file content
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract structure
        console.info(f"Analyzing structure of {file}...")
        structure = await server.structure_extractor.extract(content)
        
        # Display results
        console.info(f"Format detected: {structure['format_detected']}")
        console.info(f"Total headings: {structure['total_headings']}")
        console.info(f"Confidence: {structure['confidence_score']:.2f}")
        console.info(f"Hierarchy levels: {structure['hierarchy_levels']}")
        
        # Save analysis
        await server.file_manager.execute(
            "write_file",
            f"{file.stem}_analysis.md",
            {
                "title": f"Analysis of {file.name}",
                "source_url": str(file.absolute()),
                "body": generate_analysis_report(structure)
            }
        )
        
        console.success(f"✅ Analysis saved to: {config.output.output_base_directory}/{file.stem}_analysis.md")
        
    except Exception as e:
        console.error(f"Error: {e}")
        sys.exit(1)


def generate_analysis_report(structure: dict) -> str:
    """Generate markdown report from structure analysis."""
    report = f"""# Structure Analysis Report

## Summary
- **Format**: {structure['format_detected']}
- **Total Headings**: {structure['total_headings']}
- **Confidence Score**: {structure['confidence_score']:.2f}
- **Hierarchy Levels**: {', '.join(map(str, structure['hierarchy_levels']))}

## Hierarchical Structure

"""
    
    def render_heading(heading: dict, level: int = 0) -> str:
        indent = "  " * level
        output = f"{indent}- **{heading['text']}** (L{heading['level']})\n"
        if heading.get('children'):
            for child in heading['children']:
                output += render_heading(child, level + 1)
        return output
    
    for heading in structure['structured_headings']:
        report += render_heading(heading)
    
    if structure.get('extracted_entities'):
        report += "\n## Extracted Entities\n\n"
        entities = structure['extracted_entities']
        
        if entities.get('urls'):
            report += f"### URLs ({len(entities['urls'])})\n"
            for url in entities['urls'][:10]:  # First 10
                report += f"- {url}\n"
            if len(entities['urls']) > 10:
                report += f"- ... and {len(entities['urls']) - 10} more\n"
        
        if entities.get('key_terms'):
            report += f"\n### Key Terms ({len(entities['key_terms'])})\n"
            for term in entities['key_terms'][:20]:  # First 20
                report += f"- {term}\n"
    
    return report


@cli.command()
@click.argument('path', type=Path, required=False)
@click.option('--file', '-f', type=Path, help='Analyze a specific file')
@click.option('--directory', '-d', type=Path, help='Analyze all files in directory')
@click.option('--output', '-o', type=Path, help='Save report to file')
@click.option('--severity', type=click.Choice(['all', 'critical', 'high', 'medium', 'low']), 
              default='all', help='Filter issues by severity')
@click.pass_context
async def quality(ctx: click.Context, path: Optional[Path], file: Optional[Path], 
                 directory: Optional[Path], output: Optional[Path], severity: str) -> None:
    """Analyze quality of extracted contexts."""
    from .quality_analyzer import QualityAnalyzer
    
    # Determine what to analyze
    if file:
        target_file = file
    elif path and path.is_file():
        target_file = path
    else:
        target_file = None
    
    if directory:
        target_dir = directory
    elif path and path.is_dir():
        target_dir = path
    elif not target_file:
        target_dir = Path("generated_contexts")
    else:
        target_dir = None
    
    analyzer = QualityAnalyzer()
    
    try:
        if target_file:
            # Analyze single file
            console.info(f"Analyzing quality of: {target_file}")
            report = await analyzer.analyze_file(target_file)
            
            # Filter issues by severity
            if severity != 'all':
                report.issues = [i for i in report.issues if i.severity == severity]
            
            # Display report
            console.print(f"\n[bold]Quality Report for {target_file.name}[/bold]")
            console.print(f"Overall Score: [bold]{report.metrics.overall_score:.1f}/100[/bold]\n")
            
            # Score breakdown
            console.print("[bold]Scores:[/bold]")
            console.print(f"  Completeness: {report.metrics.completeness_score:.1f}")
            console.print(f"  Consistency: {report.metrics.consistency_score:.1f}")
            console.print(f"  Accuracy: {report.metrics.accuracy_score:.1f}")
            console.print(f"  Usability: {report.metrics.usability_score:.1f}\n")
            
            # Issues
            if report.issues:
                console.print(f"[bold]Issues ({len(report.issues)}):[/bold]")
                for issue in sorted(report.issues, 
                                  key=lambda x: ['critical', 'high', 'medium', 'low'].index(x.severity)):
                    color = {'critical': 'red', 'high': 'yellow', 'medium': 'blue', 'low': 'dim'}[issue.severity]
                    console.print(f"  [{color}][{issue.severity}][/{color}] {issue.description}")
                    if issue.recommendation:
                        console.print(f"    → {issue.recommendation}")
                console.print()
            
            # Improvements
            if report.improvements:
                console.print("[bold]Recommended Improvements:[/bold]")
                for imp in report.improvements:
                    console.print(f"  • {imp}")
                console.print()
            
            # Strengths
            if report.strengths:
                console.print("[bold green]Strengths:[/bold green]")
                for strength in report.strengths:
                    console.print(f"  ✓ {strength}")
            
        else:
            # Analyze directory
            console.info(f"Analyzing files in: {target_dir}")
            reports = await analyzer.analyze_directory(target_dir)
            
            if not reports:
                console.warning("No files found to analyze.")
                return
            
            # Generate summary
            summary = analyzer.generate_summary_report(reports)
            console.print(summary)
            
            # Save to file if requested
            if output:
                output.write_text(summary)
                console.success(f"Report saved to: {output}")
        
    except Exception as e:
        console.error(f"Error during quality analysis: {e}")
        if ctx.obj.get('verbose'):
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.group()
def ldd() -> None:
    """LDD (Log-Driven Development) commands."""
    pass


@ldd.command('init')
@click.option('--logs-dir', default='./logs', help='Logs directory')
@click.option('--memory-bank', default='./@memory-bank.md', help='Memory bank file path')
@click.pass_context
async def ldd_init(ctx: click.Context, logs_dir: str, memory_bank: str) -> None:
    """Initialize LDD system."""
    from .ldd import LDDConfig, LoggingEngine, MemoryBank
    
    try:
        console.info("🚀 Initializing LDD system...")
        
        # Create LDD config
        config = LDDConfig(
            logsDir=logs_dir,
            memoryBankPath=memory_bank
        )
        
        # Initialize components
        logging_engine = LoggingEngine(config)
        memory_bank_obj = MemoryBank(config)
        
        # Save config
        import json
        with open('.ldd-config.json', 'w') as f:
            json.dump({
                'logsDir': config.logsDir,
                'memoryBankPath': config.memoryBankPath,
                'templatePath': config.templatePath,
                'enableAutoLogging': config.enableAutoLogging
            }, f, indent=2)
        
        console.success("✅ LDD system initialized successfully!")
        console.info(f"  Logs directory: {logs_dir}")
        console.info(f"  Memory bank: {memory_bank}")
        
    except Exception as e:
        console.error(f"❌ Failed to initialize LDD system: {e}")
        sys.exit(1)


@ldd.command('task')
@click.argument('task_name')
@click.option('-a', '--agent', default='yaml-context-agent', help='Agent name')
@click.option('-p', '--project', help='Project name')
@click.option('-m', '--module', help='Module/component name')
@click.pass_context
async def ldd_task(ctx: click.Context, task_name: str, agent: str, 
                   project: Optional[str], module: Optional[str]) -> None:
    """Create a new task log."""
    from .ldd import LDDConfig, LoggingEngine
    import json
    
    try:
        # Load config
        if Path('.ldd-config.json').exists():
            with open('.ldd-config.json', 'r') as f:
                config_data = json.load(f)
                config = LDDConfig(**config_data)
        else:
            config = LDDConfig()
        
        logging_engine = LoggingEngine(config)
        
        # Create task
        context = {}
        if project:
            context['project'] = project
        if module:
            context['module'] = module
        
        log_entry = await logging_engine.create_task_log({
            'taskName': task_name,
            'agent': agent,
            'context': context,
            'status': 'Initiated'
        })
        
        console.success(f"✅ Task log created: {log_entry['id']}")
        console.info(f"  Task: {task_name}")
        console.info(f"  Status: {log_entry['status']}")
        console.info(f"  Agent: {log_entry['agent']}")
        
    except Exception as e:
        console.error(f"❌ Failed to create task log: {e}")
        sys.exit(1)


@ldd.command('memory')
@click.argument('description')
@click.option('-t', '--type', default='Learning', help='Entry type')
@click.option('-a', '--agent', default='yaml-context-agent', help='Agent name')
@click.option('--tags', help='Comma-separated tags')
@click.pass_context
async def ldd_memory(ctx: click.Context, description: str, type: str, 
                    agent: str, tags: Optional[str]) -> None:
    """Add entry to memory bank."""
    from .ldd import LDDConfig, MemoryBank
    import json
    
    try:
        # Load config
        if Path('.ldd-config.json').exists():
            with open('.ldd-config.json', 'r') as f:
                config_data = json.load(f)
                config = LDDConfig(**config_data)
        else:
            config = LDDConfig()
        
        memory_bank = MemoryBank(config)
        await memory_bank.initialize()
        
        # Create memory entry
        entry = await memory_bank.append_entry({
            'type': type,
            'agent': agent,
            'details': {
                'description': description,
                'insights': [],
                'impact': 'To be determined'
            },
            'tags': tags.split(',') if tags else []
        })
        
        console.success(f"✅ Memory entry added: {entry['id']}")
        console.info(f"  Type: {entry['type']}")
        console.info(f"  Agent: {entry['agent']}")
        
    except Exception as e:
        console.error(f"❌ Failed to add memory entry: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for CLI."""
    # Handle async commands
    async_commands = ['extract', 'analyze', 'quality']
    
    # Check if we need to run async
    needs_async = False
    for cmd in async_commands:
        if cmd in sys.argv:
            needs_async = True
            break
    
    # Also check for ldd subcommands
    if 'ldd' in sys.argv and any(subcmd in sys.argv for subcmd in ['init', 'task', 'memory']):
        needs_async = True
    
    if needs_async:
        # Create new event loop for async commands
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Modify argv to work with click's async handling
        async def run():
            await cli.main(standalone_mode=False)
        
        try:
            loop.run_until_complete(run())
        except Exception:
            # Click will handle the exception
            pass
        finally:
            loop.close()
    else:
        # Non-async commands
        cli()


if __name__ == "__main__":
    main()