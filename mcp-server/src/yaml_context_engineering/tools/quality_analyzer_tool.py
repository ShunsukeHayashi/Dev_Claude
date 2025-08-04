"""
Quality Analyzer MCP Tool

Provides quality analysis capabilities through MCP interface.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from ..quality_analyzer import QualityAnalyzer, QualityReport
from .base import BaseTool

logger = logging.getLogger(__name__)


class QualityAnalyzerTool(BaseTool):
    """MCP tool for quality analysis of extracted contexts."""
    
    def __init__(self, output_directory: str = "generated_contexts"):
        """Initialize the quality analyzer tool."""
        super().__init__()
        self.output_directory = Path(output_directory)
        self.analyzer = QualityAnalyzer()
    
    @property
    def name(self) -> str:
        return "quality_analyzer"
    
    @property
    def description(self) -> str:
        return "Analyze the quality of extracted context files"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["analyze_file", "analyze_directory", "compare_files", "suggest_improvements"],
                    "description": "The quality analysis action to perform"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to analyze (for analyze_file action)"
                },
                "directory_path": {
                    "type": "string",
                    "description": "Path to directory to analyze (for analyze_directory action)"
                },
                "file_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of file paths to compare (for compare_files action)"
                },
                "include_recommendations": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include improvement recommendations in the analysis"
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
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute quality analysis based on the specified action."""
        action = kwargs.get('action')
        
        try:
            if action == "analyze_file":
                return await self._analyze_file(kwargs)
            elif action == "analyze_directory":
                return await self._analyze_directory(kwargs)
            elif action == "compare_files":
                return await self._compare_files(kwargs)
            elif action == "suggest_improvements":
                return await self._suggest_improvements(kwargs)
            else:
                return self._error_response(f"Unknown action: {action}")
        
        except Exception as e:
            logger.error(f"Quality analysis error: {e}")
            return self._error_response(str(e))
    
    async def _analyze_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single file's quality."""
        file_path = params.get('file_path')
        if not file_path:
            return self._error_response("file_path is required for analyze_file action")
        
        # Resolve path
        path = Path(file_path)
        if not path.is_absolute():
            path = self.output_directory / path
        
        if not path.exists():
            return self._error_response(f"File not found: {path}")
        
        # Analyze file
        report = await self.analyzer.analyze_file(path)
        
        # Filter issues by severity if requested
        severity_filter = params.get('severity_filter', 'all')
        if severity_filter != 'all':
            report.issues = [
                issue for issue in report.issues 
                if issue.severity == severity_filter
            ]
        
        # Convert report to dict
        return {
            "status": "success",
            "file": str(path),
            "quality_report": self._report_to_dict(report),
            "summary": self._generate_summary(report),
            "action_required": report.metrics.overall_score < 70
        }
    
    async def _analyze_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze all files in a directory."""
        directory_path = params.get('directory_path', str(self.output_directory))
        
        directory = Path(directory_path)
        if not directory.is_absolute():
            directory = self.output_directory / directory
        
        if not directory.exists():
            return self._error_response(f"Directory not found: {directory}")
        
        # Analyze all files
        reports = await self.analyzer.analyze_directory(directory)
        
        if not reports:
            return {
                "status": "success",
                "message": "No files found to analyze",
                "directory": str(directory)
            }
        
        # Generate summary
        summary_text = self.analyzer.generate_summary_report(reports)
        
        # Convert reports to simplified format
        file_summaries = {}
        for file_path, report in reports.items():
            file_summaries[Path(file_path).name] = {
                "overall_score": report.metrics.overall_score,
                "issues_count": len(report.issues),
                "critical_issues": sum(1 for i in report.issues if i.severity == "critical"),
                "needs_attention": report.metrics.overall_score < 70
            }
        
        return {
            "status": "success",
            "directory": str(directory),
            "files_analyzed": len(reports),
            "summary_report": summary_text,
            "file_summaries": file_summaries,
            "average_score": sum(r.metrics.overall_score for r in reports.values()) / len(reports)
        }
    
    async def _compare_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare quality between multiple files."""
        file_paths = params.get('file_paths', [])
        
        if len(file_paths) < 2:
            return self._error_response("At least 2 files required for comparison")
        
        reports = {}
        for file_path in file_paths:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.output_directory / path
            
            if path.exists():
                report = await self.analyzer.analyze_file(path)
                reports[str(path)] = report
        
        if len(reports) < 2:
            return self._error_response("Could not analyze enough files for comparison")
        
        # Generate comparison
        comparison = {
            "files": {},
            "best_file": None,
            "worst_file": None,
            "biggest_differences": []
        }
        
        best_score = -1
        worst_score = 101
        
        for file_path, report in reports.items():
            file_name = Path(file_path).name
            comparison["files"][file_name] = {
                "overall_score": report.metrics.overall_score,
                "completeness": report.metrics.completeness_score,
                "consistency": report.metrics.consistency_score,
                "accuracy": report.metrics.accuracy_score,
                "usability": report.metrics.usability_score,
                "issues": len(report.issues),
                "strengths": report.strengths
            }
            
            if report.metrics.overall_score > best_score:
                best_score = report.metrics.overall_score
                comparison["best_file"] = file_name
            
            if report.metrics.overall_score < worst_score:
                worst_score = report.metrics.overall_score
                comparison["worst_file"] = file_name
        
        # Find biggest differences
        metrics = ['completeness', 'consistency', 'accuracy', 'usability']
        for metric in metrics:
            scores = [comparison["files"][f][metric] for f in comparison["files"]]
            if max(scores) - min(scores) > 20:
                comparison["biggest_differences"].append({
                    "metric": metric,
                    "range": f"{min(scores):.1f} - {max(scores):.1f}",
                    "difference": max(scores) - min(scores)
                })
        
        return {
            "status": "success",
            "comparison": comparison,
            "recommendation": self._generate_comparison_recommendation(comparison)
        }
    
    async def _suggest_improvements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest improvements for a file or directory."""
        file_path = params.get('file_path')
        
        if file_path:
            # Single file improvements
            path = Path(file_path)
            if not path.is_absolute():
                path = self.output_directory / path
            
            if not path.exists():
                return self._error_response(f"File not found: {path}")
            
            report = await self.analyzer.analyze_file(path)
            
            improvements = {
                "file": str(path),
                "current_score": report.metrics.overall_score,
                "target_score": 85.0,
                "priority_actions": [],
                "detailed_suggestions": {},
                "estimated_improvement": 0
            }
            
            # Prioritize improvements
            if report.metrics.completeness_score < 70:
                improvements["priority_actions"].append({
                    "action": "Improve content completeness",
                    "impact": "High",
                    "steps": [
                        "Add missing metadata fields",
                        "Expand short sections",
                        "Include all hierarchy levels"
                    ]
                })
                improvements["estimated_improvement"] += 15
            
            if report.metrics.consistency_score < 75:
                improvements["priority_actions"].append({
                    "action": "Fix structural consistency",
                    "impact": "Medium",
                    "steps": [
                        "Correct heading hierarchy",
                        "Standardize formatting",
                        "Use consistent list markers"
                    ]
                })
                improvements["estimated_improvement"] += 10
            
            if report.metrics.accuracy_score < 80:
                improvements["priority_actions"].append({
                    "action": "Verify metadata accuracy",
                    "impact": "Medium",
                    "steps": [
                        "Fix timestamp formats",
                        "Validate URLs",
                        "Correct language tags"
                    ]
                })
                improvements["estimated_improvement"] += 5
            
            if report.metrics.usability_score < 70:
                improvements["priority_actions"].append({
                    "action": "Enhance usability",
                    "impact": "High",
                    "steps": [
                        "Add table of contents",
                        "Include examples",
                        "Fix broken links",
                        "Add language to code blocks"
                    ]
                })
                improvements["estimated_improvement"] += 10
            
            # Group issues by category
            for issue in report.issues:
                if issue.category not in improvements["detailed_suggestions"]:
                    improvements["detailed_suggestions"][issue.category] = []
                
                improvements["detailed_suggestions"][issue.category].append({
                    "issue": issue.description,
                    "severity": issue.severity,
                    "fix": issue.recommendation
                })
            
            improvements["projected_score"] = min(
                95, 
                report.metrics.overall_score + improvements["estimated_improvement"]
            )
            
            return {
                "status": "success",
                "improvements": improvements,
                "quick_wins": self._identify_quick_wins(report),
                "long_term_goals": report.improvements
            }
        
        else:
            # Directory-wide improvements
            directory = Path(params.get('directory_path', self.output_directory))
            reports = await self.analyzer.analyze_directory(directory)
            
            if not reports:
                return {
                    "status": "success",
                    "message": "No files found to analyze"
                }
            
            # Aggregate common issues
            common_issues = {}
            for report in reports.values():
                for issue in report.issues:
                    key = (issue.category, issue.description)
                    if key not in common_issues:
                        common_issues[key] = {
                            "count": 0,
                            "severity": issue.severity,
                            "recommendation": issue.recommendation
                        }
                    common_issues[key]["count"] += 1
            
            # Sort by frequency
            sorted_issues = sorted(
                common_issues.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )[:10]
            
            return {
                "status": "success",
                "directory": str(directory),
                "files_analyzed": len(reports),
                "common_issues": [
                    {
                        "category": issue[0][0],
                        "description": issue[0][1],
                        "occurrences": issue[1]["count"],
                        "severity": issue[1]["severity"],
                        "recommendation": issue[1]["recommendation"]
                    }
                    for issue in sorted_issues
                ],
                "global_recommendations": [
                    "Standardize metadata format across all files",
                    "Implement consistent heading hierarchy",
                    "Add examples to all documentation",
                    "Include table of contents for long documents",
                    "Validate all URLs and internal links"
                ]
            }
    
    def _report_to_dict(self, report: QualityReport) -> Dict[str, Any]:
        """Convert QualityReport to dictionary."""
        return {
            "timestamp": report.timestamp,
            "scores": {
                "overall": report.metrics.overall_score,
                "completeness": report.metrics.completeness_score,
                "consistency": report.metrics.consistency_score,
                "accuracy": report.metrics.accuracy_score,
                "usability": report.metrics.usability_score
            },
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "description": issue.description,
                    "recommendation": issue.recommendation
                }
                for issue in report.issues
            ],
            "improvements": report.improvements,
            "strengths": report.strengths,
            "confidence": report.confidence
        }
    
    def _generate_summary(self, report: QualityReport) -> str:
        """Generate a text summary of the report."""
        summary = f"Overall Quality Score: {report.metrics.overall_score:.1f}/100\n"
        
        # Add score breakdown
        summary += f"\nScore Breakdown:\n"
        summary += f"- Completeness: {report.metrics.completeness_score:.1f}\n"
        summary += f"- Consistency: {report.metrics.consistency_score:.1f}\n"
        summary += f"- Accuracy: {report.metrics.accuracy_score:.1f}\n"
        summary += f"- Usability: {report.metrics.usability_score:.1f}\n"
        
        # Add issue summary
        if report.issues:
            critical = sum(1 for i in report.issues if i.severity == "critical")
            high = sum(1 for i in report.issues if i.severity == "high")
            summary += f"\nIssues Found: {len(report.issues)}"
            if critical > 0:
                summary += f" ({critical} critical)"
            if high > 0:
                summary += f" ({high} high priority)"
            summary += "\n"
        
        # Add strengths
        if report.strengths:
            summary += f"\nStrengths: {', '.join(report.strengths)}\n"
        
        # Add top recommendation
        if report.improvements:
            summary += f"\nTop Recommendation: {report.improvements[0]}\n"
        
        return summary
    
    def _generate_comparison_recommendation(self, comparison: Dict[str, Any]) -> str:
        """Generate recommendation based on file comparison."""
        rec = f"Best performing file: {comparison['best_file']}\n"
        rec += f"Needs most improvement: {comparison['worst_file']}\n"
        
        if comparison['biggest_differences']:
            rec += "\nFocus areas for improvement:\n"
            for diff in comparison['biggest_differences']:
                rec += f"- {diff['metric'].title()}: varies by {diff['difference']:.1f} points\n"
        
        return rec
    
    def _identify_quick_wins(self, report: QualityReport) -> List[Dict[str, str]]:
        """Identify quick improvements that can boost score."""
        quick_wins = []
        
        # Check for easy metadata fixes
        low_severity_metadata = [
            i for i in report.issues 
            if i.severity == "low" and i.category == "metadata"
        ]
        if low_severity_metadata:
            quick_wins.append({
                "action": "Fix metadata issues",
                "effort": "5 minutes",
                "impact": f"+{len(low_severity_metadata) * 2} points"
            })
        
        # Check for formatting issues
        formatting_issues = [
            i for i in report.issues 
            if i.category == "formatting"
        ]
        if formatting_issues:
            quick_wins.append({
                "action": "Standardize formatting",
                "effort": "10 minutes",
                "impact": f"+{len(formatting_issues) * 3} points"
            })
        
        # Check for missing examples
        if "Add examples" in str(report.improvements):
            quick_wins.append({
                "action": "Add 2-3 examples",
                "effort": "15 minutes",
                "impact": "+5 points"
            })
        
        return quick_wins[:3]  # Return top 3 quick wins
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "status": "error",
            "error": message
        }