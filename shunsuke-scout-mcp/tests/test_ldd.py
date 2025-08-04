"""Tests for LDD (Log-Driven Development) system."""

import pytest
import json
import asyncio
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from yaml_context_engineering.ldd import (
    LoggingEngine,
    MemoryBank,
    LDDConfig,
    LogEntry,
    MemoryEntry
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def ldd_config(temp_dir):
    """Create test LDD configuration."""
    return LDDConfig(
        logsDir=str(temp_dir / 'logs'),
        memoryBankPath=str(temp_dir / '@memory-bank.md'),
        templatePath=str(temp_dir / '@logging_template.md')
    )


@pytest.fixture
def logging_engine(ldd_config):
    """Create test logging engine."""
    return LoggingEngine(ldd_config)


@pytest.fixture
def memory_bank(ldd_config):
    """Create test memory bank."""
    return MemoryBank(ldd_config)


class TestLoggingEngine:
    """Test cases for LoggingEngine."""
    
    @pytest.mark.asyncio
    async def test_create_task_log(self, logging_engine):
        """Test creating a new task log."""
        task_data = {
            'taskName': 'Test URL extraction',
            'agent': 'test-agent',
            'context': {
                'project': 'yaml-context',
                'module': 'web-fetcher'
            }
        }
        
        log_entry = await logging_engine.create_task_log(task_data)
        
        assert log_entry['taskName'] == 'Test URL extraction'
        assert log_entry['agent'] == 'test-agent'
        assert log_entry['status'] == 'Initiated'
        assert log_entry['context']['project'] == 'yaml-context'
        assert 'id' in log_entry
        assert 'date' in log_entry
        assert 'timestamp' in log_entry
    
    @pytest.mark.asyncio
    async def test_update_task_log(self, logging_engine):
        """Test updating a task log."""
        # Create a task first
        task_data = {'taskName': 'Test task'}
        log_entry = await logging_engine.create_task_log(task_data)
        log_id = log_entry['id']
        
        # Update the task
        updates = {
            'status': 'In Progress',
            'results': {'extracted_urls': 5}
        }
        updated_log = await logging_engine.update_task_log(log_id, updates)
        
        assert updated_log['status'] == 'In Progress'
        assert updated_log['results']['extracted_urls'] == 5
    
    @pytest.mark.asyncio
    async def test_add_action(self, logging_engine):
        """Test adding actions to a task."""
        # Create a task
        task_data = {'taskName': 'Test task'}
        log_entry = await logging_engine.create_task_log(task_data)
        log_id = log_entry['id']
        
        # Add actions
        await logging_engine.add_action(log_id, 'Fetching URL content')
        await logging_engine.add_action(log_id, 'Extracting headings', completed=True)
        
        # Get updated log
        updated_log = await logging_engine.get_task_log(log_id)
        
        assert len(updated_log['actions']) == 2
        assert updated_log['actions'][0]['description'] == 'Fetching URL content'
        assert updated_log['actions'][0]['completed'] is False
        assert updated_log['actions'][1]['completed'] is True
    
    @pytest.mark.asyncio
    async def test_add_error(self, logging_engine):
        """Test adding errors to a task."""
        # Create a task
        task_data = {'taskName': 'Test task'}
        log_entry = await logging_engine.create_task_log(task_data)
        log_id = log_entry['id']
        
        # Add error
        await logging_engine.add_error(log_id, 'Connection timeout')
        
        # Get updated log
        updated_log = await logging_engine.get_task_log(log_id)
        
        assert len(updated_log['errors']) == 1
        assert updated_log['errors'][0] == 'Connection timeout'
    
    @pytest.mark.asyncio
    async def test_get_recent_logs(self, logging_engine):
        """Test getting recent logs."""
        # Create multiple tasks
        for i in range(5):
            await logging_engine.create_task_log({
                'taskName': f'Task {i}',
                'agent': 'test-agent' if i % 2 == 0 else 'other-agent'
            })
            await asyncio.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Get recent logs
        recent_logs = await logging_engine.get_recent_logs(limit=3)
        assert len(recent_logs) == 3
        
        # Get logs by agent
        agent_logs = await logging_engine.get_recent_logs(limit=10, agent='test-agent')
        assert len(agent_logs) == 3  # Tasks 0, 2, 4


class TestMemoryBank:
    """Test cases for MemoryBank."""
    
    @pytest.mark.asyncio
    async def test_initialize(self, memory_bank):
        """Test memory bank initialization."""
        await memory_bank.initialize()
        assert memory_bank.memory_path.exists()
        content = memory_bank.memory_path.read_text()
        assert '# 🧠 Memory Bank' in content
    
    @pytest.mark.asyncio
    async def test_append_entry(self, memory_bank):
        """Test appending memory entries."""
        await memory_bank.initialize()
        
        entry_data = {
            'type': 'Learning',
            'agent': 'test-agent',
            'details': {
                'description': 'Discovered optimal extraction pattern',
                'insights': ['Use BeautifulSoup for HTML parsing', 'Cache frequently accessed URLs'],
                'impact': 'Improved extraction speed by 50%'
            },
            'tags': ['optimization', 'performance']
        }
        
        entry = await memory_bank.append_entry(entry_data)
        
        assert entry['type'] == 'Learning'
        assert entry['agent'] == 'test-agent'
        assert len(entry['details']['insights']) == 2
        assert 'optimization' in entry['tags']
        assert 'id' in entry
        
        # Check file content
        content = memory_bank.memory_path.read_text()
        assert 'Discovered optimal extraction pattern' in content
        assert '#optimization' in content
    
    @pytest.mark.asyncio
    async def test_search_memory(self, memory_bank):
        """Test searching memory entries."""
        await memory_bank.initialize()
        
        # Add various entries
        entries_data = [
            {
                'type': 'Learning',
                'description': 'URL extraction pattern',
                'tags': ['extraction', 'url']
            },
            {
                'type': 'Error',
                'description': 'Connection timeout issue',
                'tags': ['error', 'network']
            },
            {
                'type': 'Success',
                'description': 'Successfully extracted 100 URLs',
                'tags': ['extraction', 'success']
            }
        ]
        
        for data in entries_data:
            await memory_bank.append_entry({
                'type': data['type'],
                'details': {'description': data['description'], 'insights': [], 'impact': 'TBD'},
                'tags': data['tags']
            })
        
        # Search by keywords
        results = await memory_bank.search_memory({'keywords': ['extraction']})
        assert len(results) == 2
        
        # Search by type
        results = await memory_bank.search_memory({'type': 'Error'})
        assert len(results) == 1
        assert 'timeout' in results[0]['details']['description']
        
        # Search by tags
        results = await memory_bank.search_memory({'tags': ['success']})
        assert len(results) == 1
    
    @pytest.mark.asyncio
    async def test_analyze_patterns(self, memory_bank):
        """Test pattern analysis."""
        await memory_bank.initialize()
        
        # Add multiple entries
        for i in range(10):
            entry_type = ['Learning', 'Error', 'Success'][i % 3]
            await memory_bank.append_entry({
                'type': entry_type,
                'agent': f'agent-{i % 2}',
                'details': {
                    'description': f'Entry {i}',
                    'insights': [],
                    'impact': 'TBD'
                },
                'tags': ['test', f'tag-{i % 3}']
            })
        
        analysis = await memory_bank.analyze_patterns()
        
        assert 'commonTags' in analysis
        assert 'test' in analysis['commonTags']
        assert analysis['commonTags']['test'] == 10
        
        assert 'agentActivity' in analysis
        assert len(analysis['agentActivity']) == 2
        
        assert 'typeDistribution' in analysis
        assert analysis['typeDistribution']['Learning'] == 4
        assert analysis['typeDistribution']['Error'] == 3
        assert analysis['typeDistribution']['Success'] == 3
        
        assert 'insights' in analysis
        assert len(analysis['insights']) > 0


class TestLDDManagerTool:
    """Test cases for LDD Manager Tool."""
    
    @pytest.mark.asyncio
    async def test_ldd_manager_integration(self, temp_dir):
        """Test LDD Manager tool integration."""
        from yaml_context_engineering.tools.ldd_manager import LDDManagerTool
        
        config = LDDConfig(
            logsDir=str(temp_dir / 'logs'),
            memoryBankPath=str(temp_dir / '@memory-bank.md')
        )
        
        manager = LDDManagerTool(config)
        await manager.initialize()
        
        # Create a task
        result = await manager.execute(
            'create_task',
            task_name='Test extraction task',
            agent='test-agent',
            context={'url': 'https://example.com'}
        )
        
        assert result['success'] is True
        assert 'task_id' in result['result']
        
        task_id = result['result']['task_id']
        
        # Update the task
        result = await manager.execute(
            'update_task',
            task_id=task_id,
            status='In Progress',
            add_action='Fetching content'
        )
        
        assert result['success'] is True
        
        # Add memory
        result = await manager.execute(
            'add_memory',
            description='Found efficient extraction method',
            type='Learning',
            insights=['Use async requests', 'Batch process URLs'],
            tags=['optimization', 'performance']
        )
        
        assert result['success'] is True
        assert 'memory_id' in result['result']
        
        # Search memory
        result = await manager.execute(
            'search_memory',
            keywords=['extraction']
        )
        
        assert result['success'] is True
        assert result['result']['count'] == 1
        
        # Analyze patterns
        result = await manager.execute('analyze_patterns')
        
        assert result['success'] is True
        assert 'insights' in result['result']