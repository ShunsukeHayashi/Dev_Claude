"""Logging Engine for LDD system."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import asyncio
from nanoid import generate

from ..utils.logging import get_logger
from .types import LogEntry, LDDConfig, TaskContext


class LoggingEngine:
    """Manages task logs for the LDD system."""
    
    def __init__(self, config: LDDConfig):
        """Initialize the logging engine."""
        self.config = config
        self.logger = get_logger(__name__)
        self.logs_dir = Path(config.logsDir)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure log directories exist."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        (self.logs_dir / 'tasks').mkdir(exist_ok=True)
        (self.logs_dir / 'system').mkdir(exist_ok=True)
        (self.logs_dir / 'feedback').mkdir(exist_ok=True)
        (self.logs_dir / 'metrics').mkdir(exist_ok=True)
    
    def _generate_id(self) -> str:
        """Generate unique ID for log entries."""
        return generate(size=12)
    
    def _get_timestamp(self) -> tuple[str, str]:
        """Get current date and timestamp."""
        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        timestamp = now.isoformat()
        return date, timestamp
    
    async def create_task_log(self, task_data: Dict) -> LogEntry:
        """Create a new task log."""
        date, timestamp = self._get_timestamp()
        log_id = self._generate_id()
        
        log_entry: LogEntry = {
            'id': log_id,
            'date': date,
            'timestamp': timestamp,
            'agent': task_data.get('agent', 'yaml-context-agent'),
            'taskName': task_data['taskName'],
            'status': task_data.get('status', 'Initiated'),
            'context': task_data.get('context', {}),
            'actions': task_data.get('actions', []),
            'errors': task_data.get('errors', []),
            'results': task_data.get('results'),
            'nextSteps': task_data.get('nextSteps', []),
            'references': task_data.get('references', [])
        }
        
        # Save log file
        log_path = self.logs_dir / 'tasks' / f'{date}_{log_id}.json'
        with open(log_path, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        self.logger.info(f"Created task log: {log_id}", task=task_data['taskName'])
        return log_entry
    
    async def update_task_log(self, log_id: str, updates: Dict) -> LogEntry:
        """Update an existing task log."""
        # Find the log file
        log_files = list(self.logs_dir.glob(f'tasks/*_{log_id}.json'))
        if not log_files:
            raise ValueError(f"Task log not found: {log_id}")
        
        log_path = log_files[0]
        
        # Load existing log
        with open(log_path, 'r') as f:
            log_entry = json.load(f)
        
        # Apply updates
        if 'status' in updates:
            log_entry['status'] = updates['status']
        
        if 'actions' in updates:
            log_entry['actions'] = updates['actions']
        
        if 'errors' in updates:
            log_entry['errors'] = updates['errors']
        
        if 'results' in updates:
            log_entry['results'] = updates['results']
        
        if 'nextSteps' in updates:
            log_entry['nextSteps'] = updates['nextSteps']
        
        # Update timestamp
        _, timestamp = self._get_timestamp()
        log_entry['timestamp'] = timestamp
        
        # Save updated log
        with open(log_path, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        self.logger.info(f"Updated task log: {log_id}", status=log_entry['status'])
        return log_entry
    
    async def add_action(self, log_id: str, action: str, completed: bool = False) -> LogEntry:
        """Add an action to a task log."""
        log_entry = await self.get_task_log(log_id)
        if not log_entry:
            raise ValueError(f"Task log not found: {log_id}")
        
        _, timestamp = self._get_timestamp()
        log_entry['actions'].append({
            'description': action,
            'completed': completed,
            'timestamp': timestamp
        })
        
        return await self.update_task_log(log_id, {'actions': log_entry['actions']})
    
    async def complete_action(self, log_id: str, action_index: int) -> LogEntry:
        """Mark an action as completed."""
        log_entry = await self.get_task_log(log_id)
        if not log_entry:
            raise ValueError(f"Task log not found: {log_id}")
        
        if action_index >= len(log_entry['actions']):
            raise ValueError(f"Action index out of range: {action_index}")
        
        log_entry['actions'][action_index]['completed'] = True
        return await self.update_task_log(log_id, {'actions': log_entry['actions']})
    
    async def add_error(self, log_id: str, error: str) -> LogEntry:
        """Add an error to a task log."""
        log_entry = await self.get_task_log(log_id)
        if not log_entry:
            raise ValueError(f"Task log not found: {log_id}")
        
        log_entry['errors'].append(error)
        return await self.update_task_log(log_id, {'errors': log_entry['errors']})
    
    async def get_task_log(self, log_id: str) -> Optional[LogEntry]:
        """Retrieve a task log by ID."""
        log_files = list(self.logs_dir.glob(f'tasks/*_{log_id}.json'))
        if not log_files:
            return None
        
        with open(log_files[0], 'r') as f:
            return json.load(f)
    
    async def get_recent_logs(self, limit: int = 10, agent: Optional[str] = None) -> List[LogEntry]:
        """Get recent task logs."""
        log_files = sorted(
            self.logs_dir.glob('tasks/*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        logs = []
        for log_file in log_files[:limit * 2]:  # Read more to filter
            with open(log_file, 'r') as f:
                log_entry = json.load(f)
                if agent is None or log_entry['agent'] == agent:
                    logs.append(log_entry)
                    if len(logs) >= limit:
                        break
        
        return logs
    
    async def get_logs_by_status(self, status: str, limit: int = 50) -> List[LogEntry]:
        """Get logs by status."""
        log_files = sorted(
            self.logs_dir.glob('tasks/*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        logs = []
        for log_file in log_files:
            with open(log_file, 'r') as f:
                log_entry = json.load(f)
                if log_entry['status'] == status:
                    logs.append(log_entry)
                    if len(logs) >= limit:
                        break
        
        return logs
    
    async def archive_old_logs(self) -> int:
        """Archive old logs based on retention policy."""
        # TODO: Implement log rotation based on config
        return 0