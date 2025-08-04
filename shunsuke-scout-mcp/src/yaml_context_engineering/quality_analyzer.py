"""
Quality Analysis System for YAML Context Engineering

This module provides comprehensive quality analysis for extracted contexts,
including completeness checks, consistency validation, and improvement suggestions.
"""

import re
import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import yaml
from ruamel.yaml import YAML
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Quality metrics for extracted content."""
    
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    accuracy_score: float = 0.0
    usability_score: float = 0.0
    overall_score: float = 0.0
    
    def calculate_overall(self) -> float:
        """Calculate overall score from individual metrics."""
        scores = [
            self.completeness_score,
            self.consistency_score,
            self.accuracy_score,
            self.usability_score
        ]
        self.overall_score = statistics.mean(scores)
        return self.overall_score


@dataclass
class QualityIssue:
    """Represents a quality issue found during analysis."""
    
    severity: str  # critical, high, medium, low
    category: str  # structure, content, metadata, formatting
    description: str
    location: Optional[str] = None
    recommendation: str = ""
    impact_score: float = 0.0


@dataclass
class QualityReport:
    """Complete quality analysis report."""
    
    file_path: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    metrics: QualityMetrics = field(default_factory=QualityMetrics)
    issues: List[QualityIssue] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    confidence: float = 0.0
    analysis_version: str = "1.0.0"


class QualityAnalyzer:
    """Analyzes the quality of extracted contexts."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the quality analyzer."""
        self.config = config or {}
        self.yaml_parser = YAML()
        self.yaml_parser.preserve_quotes = True
        
        # Quality thresholds
        self.thresholds = self.config.get('thresholds', {
            'completeness': 70,
            'consistency': 75,
            'accuracy': 80,
            'usability': 70
        })
        
        # Required metadata fields
        self.required_metadata = [
            'title', 'source_url', 'extraction_timestamp',
            'extracted_by', 'hierarchy_levels'
        ]
        
        # Heading patterns
        self.heading_patterns = {
            'L1': re.compile(r'^#\s+(.+)$', re.MULTILINE),
            'L2': re.compile(r'^##\s+(.+)$', re.MULTILINE),
            'L3': re.compile(r'^###\s+(.+)$', re.MULTILINE),
            'L4': re.compile(r'^####\s+(.+)$', re.MULTILINE)
        }
    
    async def analyze_file(self, file_path: Path) -> QualityReport:
        """Analyze a single extracted context file."""
        logger.info(f"Analyzing quality of: {file_path}")
        
        report = QualityReport(file_path=str(file_path))
        
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            
            # Parse YAML frontmatter and content
            metadata, body = self._parse_file(content)
            
            # Run analysis components
            await self._analyze_completeness(metadata, body, report)
            await self._analyze_consistency(metadata, body, report)
            await self._analyze_accuracy(metadata, body, report)
            await self._analyze_usability(metadata, body, report)
            
            # Calculate overall metrics
            report.metrics.calculate_overall()
            
            # Generate recommendations
            self._generate_recommendations(report)
            
            # Calculate confidence
            report.confidence = self._calculate_confidence(report)
            
            logger.info(f"Quality analysis complete. Overall score: {report.metrics.overall_score:.1f}")
            
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            report.issues.append(QualityIssue(
                severity="critical",
                category="system",
                description=f"Analysis error: {str(e)}",
                recommendation="Fix file format or content errors"
            ))
        
        return report
    
    def _parse_file(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter and body content."""
        parts = content.split('---', 2)
        
        if len(parts) >= 3 and parts[0].strip() == '':
            # Has frontmatter
            try:
                metadata = self.yaml_parser.load(parts[1])
                body = parts[2].strip()
            except Exception as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}")
                metadata = {}
                body = content
        else:
            # No frontmatter
            metadata = {}
            body = content
        
        return metadata or {}, body
    
    async def _analyze_completeness(self, metadata: Dict[str, Any], body: str, report: QualityReport):
        """Analyze content completeness."""
        score = 100.0
        
        # Check metadata completeness
        missing_metadata = []
        for field in self.required_metadata:
            if field not in metadata:
                missing_metadata.append(field)
                score -= 5
        
        if missing_metadata:
            report.issues.append(QualityIssue(
                severity="medium",
                category="metadata",
                description=f"Missing required metadata fields: {', '.join(missing_metadata)}",
                recommendation="Add missing metadata fields to frontmatter"
            ))
        
        # Check content length
        word_count = len(body.split())
        if word_count < 100:
            score -= 20
            report.issues.append(QualityIssue(
                severity="high",
                category="content",
                description=f"Content too short ({word_count} words)",
                recommendation="Ensure comprehensive content extraction"
            ))
        
        # Check heading structure
        headings = self._extract_headings(body)
        if not headings.get('L1'):
            score -= 10
            report.issues.append(QualityIssue(
                severity="medium",
                category="structure",
                description="No top-level (L1) headings found",
                recommendation="Ensure proper heading hierarchy starting with L1"
            ))
        
        # Check for empty sections
        empty_sections = self._find_empty_sections(body)
        if empty_sections:
            score -= len(empty_sections) * 5
            report.issues.append(QualityIssue(
                severity="low",
                category="content",
                description=f"Empty sections found: {', '.join(empty_sections[:3])}{'...' if len(empty_sections) > 3 else ''}",
                recommendation="Remove empty sections or add content"
            ))
        
        report.metrics.completeness_score = max(0, score)
        
        if score >= 90:
            report.strengths.append("Comprehensive content with complete metadata")
    
    async def _analyze_consistency(self, metadata: Dict[str, Any], body: str, report: QualityReport):
        """Analyze structural consistency."""
        score = 100.0
        
        # Check heading hierarchy consistency
        headings = self._extract_headings(body)
        hierarchy_issues = self._check_heading_hierarchy(headings)
        
        if hierarchy_issues:
            score -= len(hierarchy_issues) * 5
            for issue in hierarchy_issues:
                report.issues.append(QualityIssue(
                    severity="low",
                    category="structure",
                    description=issue,
                    recommendation="Fix heading hierarchy to be sequential"
                ))
        
        # Check formatting consistency
        formatting_issues = self._check_formatting_consistency(body)
        if formatting_issues:
            score -= len(formatting_issues) * 3
            for issue in formatting_issues:
                report.issues.append(issue)
        
        # Check metadata consistency
        if metadata.get('hierarchy_levels'):
            declared_levels = set(metadata['hierarchy_levels'])
            actual_levels = set(headings.keys())
            
            if declared_levels != actual_levels:
                score -= 10
                report.issues.append(QualityIssue(
                    severity="medium",
                    category="metadata",
                    description=f"Declared hierarchy levels {declared_levels} don't match actual {actual_levels}",
                    recommendation="Update hierarchy_levels to match content"
                ))
        
        report.metrics.consistency_score = max(0, score)
        
        if score >= 85:
            report.strengths.append("Consistent structure and formatting")
    
    async def _analyze_accuracy(self, metadata: Dict[str, Any], body: str, report: QualityReport):
        """Analyze content accuracy and metadata correctness."""
        score = 100.0
        
        # Check timestamp formats
        timestamp_fields = ['extraction_timestamp', 'last_updated']
        for field in timestamp_fields:
            if field in metadata:
                if not self._is_valid_iso_timestamp(metadata[field]):
                    score -= 5
                    report.issues.append(QualityIssue(
                        severity="low",
                        category="metadata",
                        description=f"Invalid timestamp format in {field}",
                        recommendation="Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)"
                    ))
        
        # Check URL validity
        if 'source_url' in metadata:
            if not self._is_valid_url(metadata['source_url']):
                score -= 10
                report.issues.append(QualityIssue(
                    severity="medium",
                    category="metadata",
                    description="Invalid source URL format",
                    recommendation="Ensure source_url is a valid URL"
                ))
        
        # Check language detection
        if 'language' in metadata:
            detected_lang = self._detect_language(body)
            if detected_lang and detected_lang != metadata['language']:
                score -= 5
                report.issues.append(QualityIssue(
                    severity="low",
                    category="metadata",
                    description=f"Language mismatch: declared '{metadata['language']}' but detected '{detected_lang}'",
                    recommendation="Verify and correct the language tag"
                ))
        
        # Check extraction confidence
        if 'extraction_confidence' in metadata:
            conf = metadata['extraction_confidence']
            if not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
                score -= 5
                report.issues.append(QualityIssue(
                    severity="low",
                    category="metadata",
                    description="Invalid extraction confidence value",
                    recommendation="Confidence should be a number between 0 and 1"
                ))
        
        report.metrics.accuracy_score = max(0, score)
        
        if score >= 90:
            report.strengths.append("Accurate metadata and proper formatting")
    
    async def _analyze_usability(self, metadata: Dict[str, Any], body: str, report: QualityReport):
        """Analyze content usability and accessibility."""
        score = 100.0
        
        # Check for table of contents or navigation
        has_toc = any(keyword in body.lower() for keyword in ['table of contents', 'contents', '目次'])
        if not has_toc and len(self._extract_headings(body).get('L2', [])) > 5:
            score -= 10
            report.improvements.append("Add a table of contents for better navigation")
        
        # Check for code blocks with language specification
        code_blocks = re.findall(r'```(\w*)\n', body)
        unspecified_blocks = sum(1 for lang in code_blocks if not lang)
        if unspecified_blocks > 0:
            score -= unspecified_blocks * 2
            report.issues.append(QualityIssue(
                severity="low",
                category="formatting",
                description=f"{unspecified_blocks} code blocks without language specification",
                recommendation="Add language identifiers to code blocks (e.g., ```python)"
            ))
        
        # Check for broken internal links
        internal_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', body)
        if internal_links:
            headings = self._extract_all_heading_ids(body)
            broken_links = [(text, anchor) for text, anchor in internal_links if anchor not in headings]
            if broken_links:
                score -= len(broken_links) * 3
                report.issues.append(QualityIssue(
                    severity="medium",
                    category="content",
                    description=f"{len(broken_links)} broken internal links found",
                    recommendation="Fix internal link anchors to match heading IDs"
                ))
        
        # Check readability
        avg_sentence_length = self._calculate_avg_sentence_length(body)
        if avg_sentence_length > 30:
            score -= 5
            report.improvements.append("Consider breaking long sentences for better readability")
        
        # Check for helpful elements
        has_examples = 'example' in body.lower() or '例' in body
        has_summary = any(keyword in body.lower() for keyword in ['summary', 'overview', '概要'])
        
        if has_examples:
            report.strengths.append("Includes helpful examples")
        else:
            score -= 5
            report.improvements.append("Add examples to illustrate concepts")
        
        if has_summary:
            report.strengths.append("Includes summary sections")
        
        report.metrics.usability_score = max(0, score)
        
        if score >= 85:
            report.strengths.append("Highly usable with good navigation and examples")
    
    def _extract_headings(self, body: str) -> Dict[str, List[str]]:
        """Extract all headings by level."""
        headings = {}
        for level, pattern in self.heading_patterns.items():
            matches = pattern.findall(body)
            if matches:
                headings[level] = matches
        return headings
    
    def _extract_all_heading_ids(self, body: str) -> set:
        """Extract all possible heading anchor IDs."""
        heading_ids = set()
        for pattern in self.heading_patterns.values():
            for match in pattern.finditer(body):
                heading_text = match.group(1)
                # Convert to anchor ID (simplified)
                anchor_id = re.sub(r'[^\w\s-]', '', heading_text.lower())
                anchor_id = re.sub(r'[-\s]+', '-', anchor_id)
                heading_ids.add(anchor_id)
        return heading_ids
    
    def _find_empty_sections(self, body: str) -> List[str]:
        """Find sections with no content."""
        empty_sections = []
        lines = body.split('\n')
        
        for i, line in enumerate(lines):
            if re.match(r'^#+\s+(.+)$', line):
                heading = line.strip()
                # Check if next non-empty line is another heading
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and re.match(r'^#+\s+', lines[j]):
                    empty_sections.append(heading)
        
        return empty_sections
    
    def _check_heading_hierarchy(self, headings: Dict[str, List[str]]) -> List[str]:
        """Check for heading hierarchy issues."""
        issues = []
        
        # Check if L2 exists without L1
        if 'L2' in headings and 'L1' not in headings:
            issues.append("L2 headings found without L1 parent")
        
        # Check if L3 exists without L2
        if 'L3' in headings and 'L2' not in headings:
            issues.append("L3 headings found without L2 parent")
        
        # Check if L4 exists without L3
        if 'L4' in headings and 'L3' not in headings:
            issues.append("L4 headings found without L3 parent")
        
        return issues
    
    def _check_formatting_consistency(self, body: str) -> List[QualityIssue]:
        """Check for formatting consistency issues."""
        issues = []
        
        # Check for inconsistent list markers
        unordered_lists = re.findall(r'^(\s*)([-*+])\s+', body, re.MULTILINE)
        if unordered_lists:
            markers = set(marker for _, marker in unordered_lists)
            if len(markers) > 1:
                issues.append(QualityIssue(
                    severity="low",
                    category="formatting",
                    description=f"Inconsistent list markers used: {markers}",
                    recommendation="Use consistent list markers (preferably '-')"
                ))
        
        # Check for inconsistent code fence styles
        code_fences = re.findall(r'^(```|~~~)', body, re.MULTILINE)
        if len(set(code_fences)) > 1:
            issues.append(QualityIssue(
                severity="low",
                category="formatting",
                description="Inconsistent code fence styles (``` and ~~~)",
                recommendation="Use consistent code fence style (preferably ```)"
            ))
        
        return issues
    
    def _is_valid_iso_timestamp(self, timestamp: str) -> bool:
        """Check if timestamp is in valid ISO format."""
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Simple language detection based on character patterns."""
        # This is a simplified detection - in production, use a proper library
        japanese_chars = re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', text)
        if len(japanese_chars) > len(text) * 0.1:
            return 'ja'
        
        # Default to English for now
        return 'en'
    
    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length in words."""
        sentences = re.split(r'[.!?。！？]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0
        
        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)
    
    def _generate_recommendations(self, report: QualityReport):
        """Generate improvement recommendations based on analysis."""
        # Add recommendations based on scores
        if report.metrics.completeness_score < self.thresholds['completeness']:
            report.improvements.append("Focus on extracting more comprehensive content")
        
        if report.metrics.consistency_score < self.thresholds['consistency']:
            report.improvements.append("Improve structural consistency and formatting")
        
        if report.metrics.accuracy_score < self.thresholds['accuracy']:
            report.improvements.append("Verify and correct metadata accuracy")
        
        if report.metrics.usability_score < self.thresholds['usability']:
            report.improvements.append("Enhance content usability with navigation aids")
        
        # Add specific recommendations based on issues
        critical_issues = [i for i in report.issues if i.severity == "critical"]
        if critical_issues:
            report.improvements.insert(0, "Address critical issues immediately")
        
        high_issues = [i for i in report.issues if i.severity == "high"]
        if len(high_issues) > 3:
            report.improvements.insert(1, "Prioritize fixing high-severity issues")
    
    def _calculate_confidence(self, report: QualityReport) -> float:
        """Calculate analysis confidence based on completeness and issues."""
        base_confidence = 0.9
        
        # Reduce confidence for critical issues
        critical_count = sum(1 for i in report.issues if i.severity == "critical")
        base_confidence -= critical_count * 0.1
        
        # Reduce confidence for low scores
        if report.metrics.overall_score < 50:
            base_confidence -= 0.2
        elif report.metrics.overall_score < 70:
            base_confidence -= 0.1
        
        return max(0.3, min(1.0, base_confidence))
    
    async def analyze_directory(self, directory: Path) -> Dict[str, QualityReport]:
        """Analyze all context files in a directory."""
        reports = {}
        
        for file_path in directory.glob("**/*.md"):
            if file_path.name.startswith('@'):
                continue  # Skip special files
            
            try:
                report = await self.analyze_file(file_path)
                reports[str(file_path)] = report
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")
        
        return reports
    
    def generate_summary_report(self, reports: Dict[str, QualityReport]) -> str:
        """Generate a summary report for multiple files."""
        if not reports:
            return "No files analyzed."
        
        # Calculate aggregate metrics
        avg_scores = {
            'completeness': statistics.mean(r.metrics.completeness_score for r in reports.values()),
            'consistency': statistics.mean(r.metrics.consistency_score for r in reports.values()),
            'accuracy': statistics.mean(r.metrics.accuracy_score for r in reports.values()),
            'usability': statistics.mean(r.metrics.usability_score for r in reports.values()),
            'overall': statistics.mean(r.metrics.overall_score for r in reports.values())
        }
        
        # Count issues by severity
        issue_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for report in reports.values():
            for issue in report.issues:
                issue_counts[issue.severity] += 1
        
        # Build summary
        summary = f"""# Quality Analysis Summary Report

## Overview
- **Files Analyzed**: {len(reports)}
- **Analysis Date**: {datetime.utcnow().isoformat()}Z
- **Average Overall Score**: {avg_scores['overall']:.1f}/100

## Average Scores by Category
- **Completeness**: {avg_scores['completeness']:.1f}/100
- **Consistency**: {avg_scores['consistency']:.1f}/100
- **Accuracy**: {avg_scores['accuracy']:.1f}/100
- **Usability**: {avg_scores['usability']:.1f}/100

## Issues Summary
- **Critical**: {issue_counts['critical']}
- **High**: {issue_counts['high']}
- **Medium**: {issue_counts['medium']}
- **Low**: {issue_counts['low']}

## Top Performing Files
"""
        # Add top 5 files
        sorted_reports = sorted(reports.items(), 
                              key=lambda x: x[1].metrics.overall_score, 
                              reverse=True)[:5]
        
        for path, report in sorted_reports:
            summary += f"- {Path(path).name}: {report.metrics.overall_score:.1f}/100\n"
        
        summary += "\n## Files Needing Attention\n"
        
        # Add bottom 5 files
        bottom_reports = sorted(reports.items(), 
                              key=lambda x: x[1].metrics.overall_score)[:5]
        
        for path, report in bottom_reports:
            if report.metrics.overall_score < 70:
                summary += f"- {Path(path).name}: {report.metrics.overall_score:.1f}/100\n"
        
        return summary


# CLI integration
async def analyze_quality_command(args):
    """CLI command to analyze quality."""
    from pathlib import Path
    
    analyzer = QualityAnalyzer()
    
    if args.file:
        # Analyze single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return
        
        report = await analyzer.analyze_file(file_path)
        
        # Print report
        print(f"\n=== Quality Report for {file_path.name} ===")
        print(f"Overall Score: {report.metrics.overall_score:.1f}/100")
        print(f"\nScores:")
        print(f"  Completeness: {report.metrics.completeness_score:.1f}")
        print(f"  Consistency: {report.metrics.consistency_score:.1f}")
        print(f"  Accuracy: {report.metrics.accuracy_score:.1f}")
        print(f"  Usability: {report.metrics.usability_score:.1f}")
        
        if report.issues:
            print(f"\nIssues ({len(report.issues)}):")
            for issue in sorted(report.issues, key=lambda x: ['critical', 'high', 'medium', 'low'].index(x.severity)):
                print(f"  [{issue.severity}] {issue.description}")
                if issue.recommendation:
                    print(f"    → {issue.recommendation}")
        
        if report.improvements:
            print(f"\nRecommended Improvements:")
            for imp in report.improvements:
                print(f"  • {imp}")
        
        if report.strengths:
            print(f"\nStrengths:")
            for strength in report.strengths:
                print(f"  ✓ {strength}")
    
    else:
        # Analyze directory
        directory = Path(args.directory or "generated_contexts")
        if not directory.exists():
            print(f"Error: Directory not found: {directory}")
            return
        
        print(f"Analyzing files in {directory}...")
        reports = await analyzer.analyze_directory(directory)
        
        if not reports:
            print("No files found to analyze.")
            return
        
        # Generate and print summary
        summary = analyzer.generate_summary_report(reports)
        print(summary)
        
        # Save detailed reports if requested
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(summary)
            print(f"\nDetailed report saved to: {output_path}")


if __name__ == "__main__":
    # Test the quality analyzer
    import asyncio
    
    async def test():
        analyzer = QualityAnalyzer()
        
        # Create a test file
        test_content = """---
title: Test Document
source_url: https://example.com
extraction_timestamp: 2025-08-04T10:00:00Z
extracted_by: test
hierarchy_levels: ["L1", "L2"]
---

# Main Title

This is a test document.

## Section 1

Content for section 1.

## Section 2

### Subsection 2.1

Content for subsection.
"""
        
        test_file = Path("test_quality.md")
        test_file.write_text(test_content)
        
        # Analyze
        report = await analyzer.analyze_file(test_file)
        
        print(f"Overall Score: {report.metrics.overall_score}")
        print(f"Issues: {len(report.issues)}")
        
        # Cleanup
        test_file.unlink()
    
    asyncio.run(test())