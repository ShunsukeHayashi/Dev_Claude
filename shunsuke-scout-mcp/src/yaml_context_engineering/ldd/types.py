"""Type definitions for LDD system."""

from typing import Dict, List, Optional, TypedDict, Literal
from dataclasses import dataclass
from datetime import datetime


class Action(TypedDict, total=False):
    """Single action in a task."""
    description: str
    completed: bool
    timestamp: str


class TaskContext(TypedDict, total=False):
    """Context information for a task."""
    project: Optional[str]
    module: Optional[str]
    url: Optional[str]
    extraction_config: Optional[Dict]


class LogEntry(TypedDict):
    """A single log entry in the LDD system."""
    id: str
    date: str
    timestamp: str
    agent: str
    taskName: str
    status: Literal['Initiated', 'In Progress', 'Completed', 'Failed', 'Blocked']
    context: TaskContext
    actions: List[Action]
    errors: List[str]
    results: Optional[Dict]
    nextSteps: List[str]
    references: List[str]


class MemoryDetails(TypedDict):
    """Details for a memory entry."""
    description: str
    insights: List[str]
    impact: str
    source_urls: Optional[List[str]]
    extraction_patterns: Optional[List[str]]


class MemoryEntry(TypedDict):
    """A single memory bank entry."""
    id: str
    date: str
    timestamp: str
    type: Literal['Learning', 'Discovery', 'Pattern', 'Error', 'Success', 'Insight']
    agent: str
    details: MemoryDetails
    relatedTasks: List[str]
    tags: List[str]


@dataclass
class LogRotation:
    """Log rotation configuration."""
    maxSize: int = 10 * 1024 * 1024  # 10MB
    maxAge: int = 30  # days
    maxFiles: int = 100


@dataclass
class LDDConfig:
    """Configuration for LDD system."""
    logsDir: str = './logs'
    memoryBankPath: str = './@memory-bank.md'
    templatePath: str = './@logging_template.md'
    enableAutoLogging: bool = True
    logRotation: LogRotation = None
    
    def __post_init__(self):
        if self.logRotation is None:
            self.logRotation = LogRotation()


class SearchQuery(TypedDict, total=False):
    """Search query parameters."""
    keywords: List[str]
    type: Optional[str]
    agent: Optional[str]
    tags: Optional[List[str]]
    dateFrom: Optional[str]
    dateTo: Optional[str]
    limit: int


class PatternAnalysis(TypedDict):
    """Pattern analysis results."""
    commonTags: Dict[str, int]
    agentActivity: Dict[str, int]
    typeDistribution: Dict[str, int]
    errorPatterns: List[str]
    successPatterns: List[str]
    insights: List[str]
    recommendations: List[str]