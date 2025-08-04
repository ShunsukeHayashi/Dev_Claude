"""Memory Bank for LDD system."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter
import asyncio
from nanoid import generate

from ..utils.logging import get_logger
from .types import MemoryEntry, LDDConfig, SearchQuery, PatternAnalysis


class MemoryBank:
    """Manages the memory bank for storing insights and learnings."""
    
    def __init__(self, config: LDDConfig):
        """Initialize the memory bank."""
        self.config = config
        self.logger = get_logger(__name__)
        self.memory_path = Path(config.memoryBankPath)
        self.entries: List[MemoryEntry] = []
        self._ensure_file()
    
    def _ensure_file(self):
        """Ensure memory bank file exists."""
        if not self.memory_path.exists():
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            self.memory_path.write_text(self._get_template())
    
    def _get_template(self) -> str:
        """Get memory bank template."""
        return """# 🧠 Memory Bank - YAML Context Engineering Agent

## Overview
This memory bank stores insights, learnings, patterns, and discoveries from context extraction tasks.

## Entries

<!-- Memory entries will be added below -->
"""
    
    def _generate_id(self) -> str:
        """Generate unique ID for memory entries."""
        return generate(size=8)
    
    async def initialize(self):
        """Load existing memory bank entries."""
        if self.memory_path.exists():
            content = self.memory_path.read_text()
            self.entries = self._parse_entries(content)
            self.logger.info(f"Loaded {len(self.entries)} memory entries")
    
    def _parse_entries(self, content: str) -> List[MemoryEntry]:
        """Parse memory entries from markdown content."""
        entries = []
        
        # Simple parsing - in production, use proper markdown parser
        entry_pattern = r'### \[(.*?)\] (.*?) - (.*?)\n'
        entries_text = content.split('## Entries')[1] if '## Entries' in content else ''
        
        # TODO: Implement proper markdown parsing
        # For now, return empty list
        return entries
    
    async def append_entry(self, entry_data: Dict) -> MemoryEntry:
        """Add a new entry to the memory bank."""
        date = datetime.now().strftime('%Y-%m-%d')
        timestamp = datetime.now().isoformat()
        entry_id = self._generate_id()
        
        entry: MemoryEntry = {
            'id': entry_id,
            'date': date,
            'timestamp': timestamp,
            'type': entry_data.get('type', 'Learning'),
            'agent': entry_data.get('agent', 'yaml-context-agent'),
            'details': entry_data.get('details', {
                'description': '',
                'insights': [],
                'impact': 'To be determined'
            }),
            'relatedTasks': entry_data.get('relatedTasks', []),
            'tags': entry_data.get('tags', [])
        }
        
        # Append to memory bank file
        await self._append_to_file(entry)
        
        # Add to in-memory list
        self.entries.append(entry)
        
        self.logger.info(f"Added memory entry: {entry_id}", type=entry['type'])
        return entry
    
    async def _append_to_file(self, entry: MemoryEntry):
        """Append entry to memory bank file."""
        content = self.memory_path.read_text()
        
        # Format entry as markdown
        entry_md = f"""
### [{entry['id']}] {entry['type']} - {entry['date']}

**Agent:** {entry['agent']}  
**Tags:** {', '.join(f'#{tag}' for tag in entry['tags']) if entry['tags'] else 'None'}

**Description:**  
{entry['details']['description']}

**Insights:**
{chr(10).join(f'- {insight}' for insight in entry['details']['insights']) if entry['details']['insights'] else '- None yet'}

**Impact:** {entry['details']['impact']}

**Related Tasks:** {', '.join(entry['relatedTasks']) if entry['relatedTasks'] else 'None'}

---
"""
        
        # Append to file
        new_content = content + '\n' + entry_md
        self.memory_path.write_text(new_content)
    
    async def search_memory(self, query: SearchQuery) -> List[MemoryEntry]:
        """Search memory bank with various filters."""
        results = self.entries.copy()
        
        # Filter by keywords
        if query.get('keywords'):
            keywords = [kw.lower() for kw in query['keywords']]
            results = [
                entry for entry in results
                if any(
                    kw in entry['details']['description'].lower() or
                    any(kw in insight.lower() for insight in entry['details']['insights']) or
                    any(kw in tag.lower() for tag in entry['tags'])
                    for kw in keywords
                )
            ]
        
        # Filter by type
        if query.get('type'):
            results = [entry for entry in results if entry['type'] == query['type']]
        
        # Filter by agent
        if query.get('agent'):
            results = [entry for entry in results if entry['agent'] == query['agent']]
        
        # Filter by tags
        if query.get('tags'):
            query_tags = set(query['tags'])
            results = [
                entry for entry in results
                if query_tags.intersection(set(entry['tags']))
            ]
        
        # Apply limit
        limit = query.get('limit', 10)
        return results[:limit]
    
    async def analyze_patterns(self) -> PatternAnalysis:
        """Analyze patterns in memory bank."""
        if not self.entries:
            await self.initialize()
        
        # Count tags
        all_tags = []
        for entry in self.entries:
            all_tags.extend(entry['tags'])
        common_tags = dict(Counter(all_tags))
        
        # Count agent activity
        agent_activity = Counter(entry['agent'] for entry in self.entries)
        
        # Type distribution
        type_distribution = Counter(entry['type'] for entry in self.entries)
        
        # Extract patterns
        error_entries = [e for e in self.entries if e['type'] == 'Error']
        success_entries = [e for e in self.entries if e['type'] == 'Success']
        
        error_patterns = self._extract_patterns(error_entries)
        success_patterns = self._extract_patterns(success_entries)
        
        # Generate insights
        insights = self._generate_insights(common_tags, agent_activity, type_distribution)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(error_patterns, success_patterns)
        
        return {
            'commonTags': common_tags,
            'agentActivity': dict(agent_activity),
            'typeDistribution': dict(type_distribution),
            'errorPatterns': error_patterns,
            'successPatterns': success_patterns,
            'insights': insights,
            'recommendations': recommendations
        }
    
    def _extract_patterns(self, entries: List[MemoryEntry]) -> List[str]:
        """Extract common patterns from entries."""
        patterns = []
        
        # Extract common phrases
        descriptions = [e['details']['description'] for e in entries]
        # TODO: Implement proper pattern extraction
        
        return patterns[:5]  # Top 5 patterns
    
    def _generate_insights(self, tags: Dict, agents: Dict, types: Dict) -> List[str]:
        """Generate insights from analysis."""
        insights = []
        
        if tags:
            top_tag = max(tags, key=tags.get)
            insights.append(f"Most common topic is '{top_tag}' with {tags[top_tag]} occurrences")
        
        if agents:
            top_agent = max(agents, key=agents.get)
            insights.append(f"Most active agent is '{top_agent}' with {agents[top_agent]} entries")
        
        if types:
            if types.get('Error', 0) > types.get('Success', 0):
                insights.append("More errors than successes - consider reviewing extraction strategies")
            elif types.get('Success', 0) > 0:
                success_rate = types.get('Success', 0) / sum(types.values()) * 100
                insights.append(f"Success rate is {success_rate:.1f}%")
        
        return insights
    
    def _generate_recommendations(self, error_patterns: List[str], success_patterns: List[str]) -> List[str]:
        """Generate recommendations based on patterns."""
        recommendations = []
        
        if error_patterns:
            recommendations.append("Review common error patterns and implement preventive measures")
        
        if success_patterns:
            recommendations.append("Leverage successful patterns in future extractions")
        
        if len(self.entries) > 100:
            recommendations.append("Consider archiving old entries to maintain performance")
        
        return recommendations
    
    async def export_insights(self, output_path: Path) -> Dict:
        """Export insights and patterns to a file."""
        analysis = await self.analyze_patterns()
        
        # Create export document
        export_content = f"""# Memory Bank Analysis Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Entries: {len(self.entries)}
- Active Agents: {len(analysis['agentActivity'])}
- Unique Tags: {len(analysis['commonTags'])}

## Insights
{chr(10).join(f'- {insight}' for insight in analysis['insights'])}

## Recommendations
{chr(10).join(f'- {rec}' for rec in analysis['recommendations'])}

## Tag Cloud
{chr(10).join(f'- #{tag}: {count}' for tag, count in sorted(analysis['commonTags'].items(), key=lambda x: x[1], reverse=True)[:20])}

## Agent Activity
{chr(10).join(f'- {agent}: {count} entries' for agent, count in analysis['agentActivity'].items())}

## Type Distribution
{chr(10).join(f'- {type_}: {count}' for type_, count in analysis['typeDistribution'].items())}
"""
        
        output_path.write_text(export_content)
        
        return {
            'path': str(output_path),
            'entries_analyzed': len(self.entries),
            'insights_generated': len(analysis['insights']),
            'recommendations': len(analysis['recommendations'])
        }