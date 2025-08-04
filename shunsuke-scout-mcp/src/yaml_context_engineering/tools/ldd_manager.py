"""LDD Manager Tool for MCP Server.

This tool provides Log-Driven Development capabilities within the MCP server,
allowing agents to track tasks, store insights, and analyze patterns.
"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

from ..ldd import LoggingEngine, MemoryBank, LDDConfig
from ..utils.logging import get_logger


class LDDManagerTool:
    """Tool for managing LDD system operations."""
    
    def __init__(self, config: Optional[LDDConfig] = None):
        """Initialize the LDD manager."""
        self.config = config or LDDConfig()
        self.logger = get_logger(__name__)
        self.logging_engine = LoggingEngine(self.config)
        self.memory_bank = MemoryBank(self.config)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the LDD system."""
        if not self._initialized:
            await self.memory_bank.initialize()
            self._initialized = True
            self.logger.info("LDD system initialized")
    
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute LDD management action."""
        await self.initialize()
        
        actions = {
            'create_task': self._create_task,
            'update_task': self._update_task,
            'add_memory': self._add_memory,
            'search_memory': self._search_memory,
            'analyze_patterns': self._analyze_patterns,
            'get_recent_tasks': self._get_recent_tasks
        }
        
        if action not in actions:
            return {
                'success': False,
                'error': f'Unknown action: {action}',
                'available_actions': list(actions.keys())
            }
        
        try:
            result = await actions[action](**kwargs)
            return {
                'success': True,
                'action': action,
                'result': result
            }
        except Exception as e:
            self.logger.error(f"LDD action failed: {action}", error=str(e))
            return {
                'success': False,
                'action': action,
                'error': str(e)
            }
    
    async def _create_task(self, task_name: str, agent: str = None, 
                          context: Dict = None, **kwargs) -> Dict[str, Any]:
        """Create a new task log."""
        task_data = {
            'taskName': task_name,
            'agent': agent or 'yaml-context-agent',
            'status': 'Initiated',
            'context': context or {},
            'actions': [],
            'errors': [],
            'nextSteps': [],
            'references': []
        }
        
        # Add any additional fields from kwargs
        for key, value in kwargs.items():
            if key not in task_data:
                task_data[key] = value
        
        log_entry = await self.logging_engine.create_task_log(task_data)
        
        return {
            'task_id': log_entry['id'],
            'status': log_entry['status'],
            'message': f"Task '{task_name}' created successfully"
        }
    
    async def _update_task(self, task_id: str, status: str = None,
                          add_action: str = None, add_error: str = None,
                          results: Dict = None, **kwargs) -> Dict[str, Any]:
        """Update an existing task."""
        updates = {}
        
        if status:
            updates['status'] = status
        
        if add_action:
            # Get current log to add action
            log = await self.logging_engine.get_task_log(task_id)
            if log:
                await self.logging_engine.add_action(task_id, add_action)
        
        if add_error:
            await self.logging_engine.add_error(task_id, add_error)
        
        if results:
            updates['results'] = results
        
        # Apply any other updates
        for key, value in kwargs.items():
            if key not in ['task_id', 'add_action', 'add_error']:
                updates[key] = value
        
        if updates:
            updated_log = await self.logging_engine.update_task_log(task_id, updates)
            return {
                'task_id': task_id,
                'status': updated_log['status'],
                'message': 'Task updated successfully'
            }
        else:
            return {
                'task_id': task_id,
                'message': 'No updates provided'
            }
    
    async def _add_memory(self, description: str, type: str = 'Learning',
                         insights: List[str] = None, tags: List[str] = None,
                         task_id: str = None, **kwargs) -> Dict[str, Any]:
        """Add an entry to memory bank."""
        entry_data = {
            'type': type,
            'agent': kwargs.get('agent', 'yaml-context-agent'),
            'details': {
                'description': description,
                'insights': insights or [],
                'impact': kwargs.get('impact', 'To be determined')
            },
            'relatedTasks': [task_id] if task_id else [],
            'tags': tags or []
        }
        
        # Add source URLs if provided
        if 'source_urls' in kwargs:
            entry_data['details']['source_urls'] = kwargs['source_urls']
        
        # Add extraction patterns if provided
        if 'extraction_patterns' in kwargs:
            entry_data['details']['extraction_patterns'] = kwargs['extraction_patterns']
        
        memory_entry = await self.memory_bank.append_entry(entry_data)
        
        return {
            'memory_id': memory_entry['id'],
            'type': memory_entry['type'],
            'message': 'Memory entry added successfully'
        }
    
    async def _search_memory(self, keywords: List[str] = None,
                           type: str = None, agent: str = None,
                           tags: List[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Search memory bank."""
        query = {
            'keywords': keywords,
            'type': type,
            'agent': agent,
            'tags': tags,
            'limit': limit
        }
        
        # Remove None values
        query = {k: v for k, v in query.items() if v is not None}
        
        results = await self.memory_bank.search_memory(query)
        
        return {
            'count': len(results),
            'entries': [
                {
                    'id': entry['id'],
                    'type': entry['type'],
                    'date': entry['date'],
                    'description': entry['details']['description'],
                    'tags': entry['tags']
                }
                for entry in results
            ]
        }
    
    async def _analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in LDD system."""
        analysis = await self.memory_bank.analyze_patterns()
        
        return {
            'total_entries': len(self.memory_bank.entries),
            'common_tags': dict(list(analysis['commonTags'].items())[:10]),  # Top 10
            'agent_activity': analysis['agentActivity'],
            'type_distribution': analysis['typeDistribution'],
            'insights': analysis['insights'],
            'recommendations': analysis['recommendations']
        }
    
    async def _get_recent_tasks(self, limit: int = 10, 
                               agent: str = None) -> Dict[str, Any]:
        """Get recent task logs."""
        logs = await self.logging_engine.get_recent_logs(limit, agent)
        
        return {
            'count': len(logs),
            'tasks': [
                {
                    'id': log['id'],
                    'name': log['taskName'],
                    'status': log['status'],
                    'agent': log['agent'],
                    'date': log['date'],
                    'errors': len(log['errors']),
                    'actions': len(log['actions'])
                }
                for log in logs
            ]
        }


# Tool definition for MCP server
LDD_MANAGER_TOOL = {
    "name": "ldd_manager",
    "description": """Manage Log-Driven Development system for tracking tasks, storing insights, and analyzing patterns.

Actions:
- create_task: Create a new task log
- update_task: Update an existing task
- add_memory: Add an insight to memory bank
- search_memory: Search memory bank
- analyze_patterns: Analyze patterns and get insights
- get_recent_tasks: Get recent task logs""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create_task", "update_task", "add_memory", 
                        "search_memory", "analyze_patterns", "get_recent_tasks"],
                "description": "The LDD action to perform"
            },
            "task_name": {
                "type": "string",
                "description": "Name of the task (for create_task)"
            },
            "task_id": {
                "type": "string",
                "description": "ID of the task (for update_task)"
            },
            "status": {
                "type": "string",
                "enum": ["Initiated", "In Progress", "Completed", "Failed", "Blocked"],
                "description": "Task status"
            },
            "description": {
                "type": "string",
                "description": "Description for memory entry"
            },
            "type": {
                "type": "string",
                "enum": ["Learning", "Discovery", "Pattern", "Error", "Success", "Insight"],
                "description": "Type of memory entry"
            },
            "insights": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of insights"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags for categorization"
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Keywords for searching"
            },
            "agent": {
                "type": "string",
                "description": "Agent name"
            },
            "context": {
                "type": "object",
                "description": "Context information for task"
            },
            "limit": {
                "type": "integer",
                "description": "Limit for search results",
                "default": 10
            }
        },
        "required": ["action"]
    }
}