# multi_agent_generator/evaluation/evaluator.py
"""
Agent Evaluator - Evaluate and score agent outputs.
No-code approach: Simple configuration for quality assessment.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import re
import time


class MetricType(Enum):
    """Types of evaluation metrics."""
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    COHERENCE = "coherence"
    ACCURACY = "accuracy"
    RESPONSE_TIME = "response_time"
    TOKEN_EFFICIENCY = "token_efficiency"
    TASK_COMPLETION = "task_completion"


@dataclass
class EvaluationMetrics:
    """Container for evaluation metrics."""
    relevance_score: float = 0.0
    completeness_score: float = 0.0
    coherence_score: float = 0.0
    accuracy_score: float = 0.0
    response_time_ms: float = 0.0
    token_count: int = 0
    task_completion_rate: float = 0.0
    
    def overall_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted overall score."""
        if weights is None:
            weights = {
                "relevance": 0.25,
                "completeness": 0.25,
                "coherence": 0.20,
                "accuracy": 0.20,
                "task_completion": 0.10
            }
        
        score = (
            self.relevance_score * weights.get("relevance", 0.2) +
            self.completeness_score * weights.get("completeness", 0.2) +
            self.coherence_score * weights.get("coherence", 0.2) +
            self.accuracy_score * weights.get("accuracy", 0.2) +
            self.task_completion_rate * weights.get("task_completion", 0.2)
        )
        return round(score, 3)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "relevance_score": self.relevance_score,
            "completeness_score": self.completeness_score,
            "coherence_score": self.coherence_score,
            "accuracy_score": self.accuracy_score,
            "response_time_ms": self.response_time_ms,
            "token_count": self.token_count,
            "task_completion_rate": self.task_completion_rate,
            "overall_score": self.overall_score()
        }


@dataclass
class EvaluationResult:
    """Complete evaluation result."""
    query: str
    response: str
    metrics: EvaluationMetrics
    passed: bool
    feedback: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "response": self.response[:500] + "..." if len(self.response) > 500 else self.response,
            "metrics": self.metrics.to_dict(),
            "passed": self.passed,
            "feedback": self.feedback,
            "errors": self.errors,
            "timestamp": self.timestamp
        }


class AgentEvaluator:
    """
    Evaluates agent outputs using multiple quality metrics.
    No-code: Configure thresholds and get automatic evaluation.
    """
    
    def __init__(
        self,
        model_inference=None,
        thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Initialize the evaluator.
        
        Args:
            model_inference: Optional ModelInference for LLM-based evaluation
            thresholds: Custom pass/fail thresholds for metrics
        """
        self.model = model_inference
        self.thresholds = thresholds or {
            "relevance": 0.6,
            "completeness": 0.6,
            "coherence": 0.7,
            "accuracy": 0.6,
            "overall": 0.65
        }
        
        # Custom evaluators registry
        self._custom_evaluators: Dict[str, Callable] = {}
    
    def evaluate(
        self,
        query: str,
        response: str,
        expected_keywords: Optional[List[str]] = None,
        expected_format: Optional[str] = None,
        ground_truth: Optional[str] = None,
        response_time_ms: Optional[float] = None
    ) -> EvaluationResult:
        """
        Evaluate an agent's response.
        
        Args:
            query: The input query
            response: The agent's response
            expected_keywords: Keywords that should appear in response
            expected_format: Expected response format
            ground_truth: Ground truth answer for accuracy
            response_time_ms: Response time in milliseconds
            
        Returns:
            EvaluationResult with all metrics and feedback
        """
        import datetime
        
        metrics = EvaluationMetrics()
        feedback = []
        errors = []
        
        # Basic validation
        if not response or not response.strip():
            return EvaluationResult(
                query=query,
                response=response or "",
                metrics=metrics,
                passed=False,
                feedback=["Response is empty"],
                errors=["Empty response received"],
                timestamp=datetime.datetime.now().isoformat()
            )
        
        # Evaluate relevance
        try:
            metrics.relevance_score = self._evaluate_relevance(query, response, expected_keywords)
            if metrics.relevance_score < self.thresholds["relevance"]:
                feedback.append(f"Relevance score ({metrics.relevance_score:.2f}) below threshold")
        except Exception as e:
            errors.append(f"Relevance evaluation error: {str(e)}")
        
        # Evaluate completeness
        try:
            metrics.completeness_score = self._evaluate_completeness(query, response, expected_keywords)
            if metrics.completeness_score < self.thresholds["completeness"]:
                feedback.append(f"Response may be incomplete (score: {metrics.completeness_score:.2f})")
        except Exception as e:
            errors.append(f"Completeness evaluation error: {str(e)}")
        
        # Evaluate coherence
        try:
            metrics.coherence_score = self._evaluate_coherence(response)
            if metrics.coherence_score < self.thresholds["coherence"]:
                feedback.append(f"Response coherence could be improved (score: {metrics.coherence_score:.2f})")
        except Exception as e:
            errors.append(f"Coherence evaluation error: {str(e)}")
        
        # Evaluate accuracy (if ground truth provided)
        if ground_truth:
            try:
                metrics.accuracy_score = self._evaluate_accuracy(response, ground_truth)
                if metrics.accuracy_score < self.thresholds["accuracy"]:
                    feedback.append(f"Accuracy score ({metrics.accuracy_score:.2f}) below expected")
            except Exception as e:
                errors.append(f"Accuracy evaluation error: {str(e)}")
        else:
            metrics.accuracy_score = 0.7  # Default when no ground truth
        
        # Record response time
        if response_time_ms:
            metrics.response_time_ms = response_time_ms
            if response_time_ms > 30000:  # 30 seconds
                feedback.append(f"Response time ({response_time_ms/1000:.1f}s) is slow")
        
        # Count tokens (approximate)
        metrics.token_count = len(response.split()) * 1.3  # Rough estimate
        
        # Evaluate format (if expected)
        if expected_format:
            format_ok = self._evaluate_format(response, expected_format)
            if not format_ok:
                feedback.append(f"Response format doesn't match expected: {expected_format}")
        
        # Task completion (based on keyword presence)
        metrics.task_completion_rate = self._evaluate_task_completion(query, response)
        
        # Determine pass/fail
        overall = metrics.overall_score()
        passed = overall >= self.thresholds.get("overall", 0.65) and len(errors) == 0
        
        if passed:
            feedback.append(f"✓ Evaluation passed with overall score: {overall:.2f}")
        else:
            feedback.append(f"✗ Evaluation failed with overall score: {overall:.2f}")
        
        return EvaluationResult(
            query=query,
            response=response,
            metrics=metrics,
            passed=passed,
            feedback=feedback,
            errors=errors,
            timestamp=datetime.datetime.now().isoformat()
        )
    
    def _evaluate_relevance(
        self,
        query: str,
        response: str,
        expected_keywords: Optional[List[str]] = None
    ) -> float:
        """Evaluate response relevance to query."""
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Extract query keywords (simple approach)
        query_words = set(re.findall(r'\b\w{4,}\b', query_lower))
        stop_words = {'what', 'where', 'when', 'which', 'that', 'this', 'have', 'from', 'with', 'about', 'would', 'could', 'should'}
        query_words -= stop_words
        
        # Check presence of query keywords in response
        if query_words:
            matches = sum(1 for word in query_words if word in response_lower)
            keyword_score = matches / len(query_words)
        else:
            keyword_score = 0.5
        
        # Check expected keywords
        if expected_keywords:
            expected_matches = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
            expected_score = expected_matches / len(expected_keywords)
            return (keyword_score + expected_score) / 2
        
        # Additional relevance checks
        # Response length relative to query
        length_ratio = min(len(response) / max(len(query) * 3, 50), 1.0)
        
        return (keyword_score * 0.7 + length_ratio * 0.3)
    
    def _evaluate_completeness(
        self,
        query: str,
        response: str,
        expected_keywords: Optional[List[str]] = None
    ) -> float:
        """Evaluate if response completely addresses the query."""
        score = 0.5  # Base score
        
        # Check response length (longer responses tend to be more complete)
        if len(response) > 100:
            score += 0.1
        if len(response) > 300:
            score += 0.1
        if len(response) > 500:
            score += 0.1
        
        # Check for structure (lists, sections, etc.)
        if re.search(r'\d+\.\s|\*\s|-\s', response):
            score += 0.1  # Has list structure
        
        # Check for conclusion/summary
        if re.search(r'in conclusion|in summary|to summarize|overall|finally', response.lower()):
            score += 0.1
        
        # Check expected keywords coverage
        if expected_keywords:
            coverage = sum(1 for kw in expected_keywords if kw.lower() in response.lower())
            score = (score + coverage / len(expected_keywords)) / 2
        
        return min(score, 1.0)
    
    def _evaluate_coherence(self, response: str) -> float:
        """Evaluate response coherence and structure."""
        score = 0.5  # Base score
        
        # Check sentence structure
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) == 0:
            return 0.0
        
        # Average sentence length (not too short, not too long)
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if 5 <= avg_length <= 25:
            score += 0.2
        elif 3 <= avg_length <= 40:
            score += 0.1
        
        # Check for proper capitalization
        proper_caps = sum(1 for s in sentences if s and s[0].isupper())
        if proper_caps / len(sentences) > 0.8:
            score += 0.1
        
        # Check for transitional words
        transitions = ['however', 'therefore', 'furthermore', 'additionally', 'moreover', 
                      'consequently', 'nevertheless', 'thus', 'hence', 'first', 'second',
                      'finally', 'in addition', 'on the other hand']
        if any(t in response.lower() for t in transitions):
            score += 0.1
        
        # Check for logical flow (sentences not too repetitive)
        if len(sentences) > 1:
            unique_starts = len(set(s.split()[0].lower() for s in sentences if s.split()))
            variety_score = unique_starts / len(sentences)
            score += variety_score * 0.1
        
        return min(score, 1.0)
    
    def _evaluate_accuracy(self, response: str, ground_truth: str) -> float:
        """Evaluate response accuracy against ground truth."""
        response_lower = response.lower()
        truth_lower = ground_truth.lower()
        
        # Extract key phrases from ground truth
        truth_words = set(re.findall(r'\b\w{4,}\b', truth_lower))
        
        if not truth_words:
            return 0.5
        
        # Check overlap
        matches = sum(1 for word in truth_words if word in response_lower)
        base_score = matches / len(truth_words)
        
        # Check for contradictions (simple approach)
        negations = ['not', "n't", 'never', 'no ', 'none', 'neither']
        truth_has_negation = any(n in truth_lower for n in negations)
        response_has_negation = any(n in response_lower for n in negations)
        
        if truth_has_negation != response_has_negation:
            base_score *= 0.8  # Potential contradiction
        
        return base_score
    
    def _evaluate_format(self, response: str, expected_format: str) -> bool:
        """Check if response matches expected format."""
        format_checks = {
            "numbered_list": r'^\d+\.',
            "bullet_list": r'^[\*\-\•]',
            "json": r'^\s*[\{\[]',
            "markdown": r'^#|^\*\*|\*\*$',
            "code": r'```|def |class |function',
            "table": r'\|.*\|',
        }
        
        if expected_format in format_checks:
            pattern = format_checks[expected_format]
            return bool(re.search(pattern, response, re.MULTILINE))
        
        return True  # Unknown format, assume OK
    
    def _evaluate_task_completion(self, query: str, response: str) -> float:
        """Evaluate if the task in the query was completed."""
        # Extract task indicators from query
        task_words = ['list', 'explain', 'describe', 'compare', 'analyze', 
                     'summarize', 'create', 'write', 'find', 'calculate']
        
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Check for task-specific completions
        score = 0.5
        
        if 'list' in query_lower:
            if re.search(r'\d+\.|•|-\s', response):
                score += 0.3
        
        if 'compare' in query_lower:
            if 'vs' in response_lower or 'compared' in response_lower or 'difference' in response_lower:
                score += 0.3
        
        if 'explain' in query_lower or 'describe' in query_lower:
            if len(response) > 200:
                score += 0.3
        
        if 'summarize' in query_lower:
            if len(response) < len(query) * 5:  # Summary should be concise
                score += 0.3
        
        # General completion indicator
        if len(response) > 50:
            score += 0.2
        
        return min(score, 1.0)
    
    def register_custom_evaluator(
        self,
        name: str,
        evaluator_fn: Callable[[str, str], float]
    ):
        """
        Register a custom evaluation function.
        
        Args:
            name: Name of the custom metric
            evaluator_fn: Function that takes (query, response) and returns score 0-1
        """
        self._custom_evaluators[name] = evaluator_fn
    
    def batch_evaluate(
        self,
        test_cases: List[Dict[str, Any]]
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple test cases.
        
        Args:
            test_cases: List of dicts with 'query', 'response', and optional params
            
        Returns:
            List of EvaluationResult objects
        """
        results = []
        for case in test_cases:
            result = self.evaluate(
                query=case.get("query", ""),
                response=case.get("response", ""),
                expected_keywords=case.get("expected_keywords"),
                expected_format=case.get("expected_format"),
                ground_truth=case.get("ground_truth"),
                response_time_ms=case.get("response_time_ms")
            )
            results.append(result)
        return results
    
    def generate_report(self, results: List[EvaluationResult]) -> str:
        """
        Generate a summary report from evaluation results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Markdown formatted report
        """
        if not results:
            return "No evaluation results to report."
        
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        
        avg_relevance = sum(r.metrics.relevance_score for r in results) / total
        avg_completeness = sum(r.metrics.completeness_score for r in results) / total
        avg_coherence = sum(r.metrics.coherence_score for r in results) / total
        avg_overall = sum(r.metrics.overall_score() for r in results) / total
        
        report = f"""# Agent Evaluation Report

## Summary
- **Total Tests**: {total}
- **Passed**: {passed} ({passed/total*100:.1f}%)
- **Failed**: {total - passed} ({(total-passed)/total*100:.1f}%)

## Average Scores
| Metric | Score |
|--------|-------|
| Relevance | {avg_relevance:.2f} |
| Completeness | {avg_completeness:.2f} |
| Coherence | {avg_coherence:.2f} |
| **Overall** | **{avg_overall:.2f}** |

## Detailed Results

"""
        
        for i, result in enumerate(results, 1):
            status = "✓ PASSED" if result.passed else "✗ FAILED"
            report += f"""### Test {i}: {status}
- **Query**: {result.query[:100]}...
- **Overall Score**: {result.metrics.overall_score():.2f}
- **Feedback**: {'; '.join(result.feedback[:3])}

"""
        
        return report


def evaluate_agent_output(
    query: str,
    response: str,
    expected_keywords: Optional[List[str]] = None,
    **kwargs
) -> EvaluationResult:
    """
    Convenience function to evaluate a single agent output.
    
    Args:
        query: Input query
        response: Agent response
        expected_keywords: Keywords expected in response
        **kwargs: Additional evaluation parameters
        
    Returns:
        EvaluationResult
    """
    evaluator = AgentEvaluator()
    return evaluator.evaluate(query, response, expected_keywords, **kwargs)
