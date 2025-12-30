# multi_agent_generator/evaluation/benchmark.py
"""
Benchmark - Performance benchmarking for agent systems.
No-code approach: Simple benchmarks with automatic reporting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
import time
import statistics


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    success_rate: float
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time_ms": round(self.total_time_ms, 2),
            "avg_time_ms": round(self.avg_time_ms, 2),
            "min_time_ms": round(self.min_time_ms, 2),
            "max_time_ms": round(self.max_time_ms, 2),
            "std_dev_ms": round(self.std_dev_ms, 2),
            "success_rate": round(self.success_rate, 3),
            "errors": self.errors[:5],  # Limit errors
            "metadata": self.metadata
        }
    
    def summary(self) -> str:
        """Get a text summary of the benchmark result."""
        return f"""
Benchmark: {self.name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Iterations: {self.iterations}
Success Rate: {self.success_rate * 100:.1f}%
Avg Time: {self.avg_time_ms:.2f}ms
Min Time: {self.min_time_ms:.2f}ms
Max Time: {self.max_time_ms:.2f}ms
Std Dev: {self.std_dev_ms:.2f}ms
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


class Benchmark:
    """
    Benchmarking tool for agent systems.
    No-code: Configure and run benchmarks easily.
    """
    
    def __init__(self, name: str = "Agent Benchmark"):
        """
        Initialize the benchmark.
        
        Args:
            name: Name for this benchmark suite
        """
        self.name = name
        self.results: List[BenchmarkResult] = []
        self._benchmarks: Dict[str, Dict[str, Any]] = {}
    
    def register(
        self,
        name: str,
        func: Callable,
        iterations: int = 10,
        warmup: int = 1,
        timeout_ms: float = 60000
    ):
        """
        Register a benchmark.
        
        Args:
            name: Benchmark name
            func: Function to benchmark (no args, returns any)
            iterations: Number of iterations
            warmup: Warmup iterations (not counted)
            timeout_ms: Timeout per iteration
        """
        self._benchmarks[name] = {
            "func": func,
            "iterations": iterations,
            "warmup": warmup,
            "timeout_ms": timeout_ms
        }
    
    def run(self, name: Optional[str] = None) -> List[BenchmarkResult]:
        """
        Run benchmarks.
        
        Args:
            name: Specific benchmark to run, or None for all
            
        Returns:
            List of BenchmarkResult objects
        """
        results = []
        
        benchmarks_to_run = {name: self._benchmarks[name]} if name else self._benchmarks
        
        for bench_name, config in benchmarks_to_run.items():
            result = self._run_single(bench_name, config)
            results.append(result)
            self.results.append(result)
        
        return results
    
    def _run_single(self, name: str, config: Dict[str, Any]) -> BenchmarkResult:
        """Run a single benchmark."""
        func = config["func"]
        iterations = config["iterations"]
        warmup = config["warmup"]
        timeout_ms = config["timeout_ms"]
        
        times = []
        errors = []
        successes = 0
        
        # Warmup
        for _ in range(warmup):
            try:
                func()
            except Exception:
                pass
        
        # Actual benchmark
        for i in range(iterations):
            start = time.perf_counter()
            try:
                func()
                end = time.perf_counter()
                elapsed_ms = (end - start) * 1000
                
                if elapsed_ms > timeout_ms:
                    errors.append(f"Iteration {i+1}: Timeout ({elapsed_ms:.0f}ms > {timeout_ms}ms)")
                else:
                    times.append(elapsed_ms)
                    successes += 1
                    
            except Exception as e:
                end = time.perf_counter()
                elapsed_ms = (end - start) * 1000
                times.append(elapsed_ms)  # Still record time
                errors.append(f"Iteration {i+1}: {str(e)[:100]}")
        
        # Calculate statistics
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            total_time = sum(times)
        else:
            avg_time = min_time = max_time = std_dev = total_time = 0
        
        return BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time_ms=total_time,
            avg_time_ms=avg_time,
            min_time_ms=min_time,
            max_time_ms=max_time,
            std_dev_ms=std_dev,
            success_rate=successes / iterations if iterations > 0 else 0,
            errors=errors,
            metadata={
                "warmup_iterations": warmup,
                "timeout_ms": timeout_ms
            }
        )
    
    def compare(self, results: Optional[List[BenchmarkResult]] = None) -> str:
        """
        Compare benchmark results.
        
        Args:
            results: Results to compare, or use stored results
            
        Returns:
            Comparison report as markdown
        """
        results = results or self.results
        
        if not results:
            return "No benchmark results to compare."
        
        report = f"# Benchmark Comparison: {self.name}\n\n"
        report += "| Benchmark | Avg (ms) | Min (ms) | Max (ms) | Success Rate |\n"
        report += "|-----------|----------|----------|----------|-------------|\n"
        
        for result in results:
            report += f"| {result.name} | {result.avg_time_ms:.2f} | {result.min_time_ms:.2f} | {result.max_time_ms:.2f} | {result.success_rate*100:.1f}% |\n"
        
        # Find fastest
        if len(results) > 1:
            fastest = min(results, key=lambda r: r.avg_time_ms)
            slowest = max(results, key=lambda r: r.avg_time_ms)
            
            report += f"\n**Fastest**: {fastest.name} ({fastest.avg_time_ms:.2f}ms)\n"
            report += f"**Slowest**: {slowest.name} ({slowest.avg_time_ms:.2f}ms)\n"
            
            if slowest.avg_time_ms > 0:
                speedup = slowest.avg_time_ms / fastest.avg_time_ms
                report += f"**Speedup**: {speedup:.2f}x\n"
        
        return report
    
    def generate_report(self, results: Optional[List[BenchmarkResult]] = None) -> str:
        """
        Generate detailed benchmark report.
        
        Args:
            results: Results to report, or use stored results
            
        Returns:
            Detailed markdown report
        """
        results = results or self.results
        
        if not results:
            return "No benchmark results to report."
        
        report = f"""# Benchmark Report: {self.name}

## Summary

| Metric | Value |
|--------|-------|
| Total Benchmarks | {len(results)} |
| Total Iterations | {sum(r.iterations for r in results)} |
| Overall Success Rate | {sum(r.success_rate for r in results) / len(results) * 100:.1f}% |

## Detailed Results

"""
        
        for result in results:
            status = "✓" if result.success_rate == 1.0 else "⚠" if result.success_rate >= 0.8 else "✗"
            
            report += f"""### {status} {result.name}

| Metric | Value |
|--------|-------|
| Iterations | {result.iterations} |
| Success Rate | {result.success_rate * 100:.1f}% |
| Average Time | {result.avg_time_ms:.2f}ms |
| Min Time | {result.min_time_ms:.2f}ms |
| Max Time | {result.max_time_ms:.2f}ms |
| Std Deviation | {result.std_dev_ms:.2f}ms |

"""
            
            if result.errors:
                report += "**Errors:**\n"
                for error in result.errors[:3]:
                    report += f"- {error}\n"
                report += "\n"
        
        return report


class AgentBenchmark(Benchmark):
    """
    Specialized benchmark for agent systems.
    Provides pre-built benchmarks for common agent operations.
    """
    
    def __init__(self, agent_func: Callable, name: str = "Agent Benchmark"):
        """
        Initialize agent benchmark.
        
        Args:
            agent_func: Function that invokes the agent (takes query, returns response)
            name: Benchmark name
        """
        super().__init__(name)
        self.agent_func = agent_func
        self._setup_default_benchmarks()
    
    def _setup_default_benchmarks(self):
        """Setup default agent benchmarks."""
        
        # Simple query benchmark
        def simple_query():
            return self.agent_func("Hello, how are you?")
        
        self.register(
            name="Simple Query",
            func=simple_query,
            iterations=5,
            warmup=1
        )
        
        # Complex query benchmark
        def complex_query():
            return self.agent_func(
                "Analyze the pros and cons of microservices architecture "
                "compared to monolithic architecture for a startup company."
            )
        
        self.register(
            name="Complex Query",
            func=complex_query,
            iterations=3,
            warmup=1
        )
        
        # Long output benchmark
        def long_output():
            return self.agent_func(
                "Write a detailed explanation of how neural networks work, "
                "including backpropagation, activation functions, and optimization."
            )
        
        self.register(
            name="Long Output",
            func=long_output,
            iterations=3,
            warmup=1,
            timeout_ms=120000
        )
    
    def add_custom_benchmark(
        self,
        name: str,
        query: str,
        iterations: int = 5
    ):
        """
        Add a custom query benchmark.
        
        Args:
            name: Benchmark name
            query: Query to benchmark
            iterations: Number of iterations
        """
        def custom_query():
            return self.agent_func(query)
        
        self.register(
            name=name,
            func=custom_query,
            iterations=iterations
        )
    
    def run_quick(self) -> BenchmarkResult:
        """Run a quick single-iteration benchmark."""
        def quick_test():
            return self.agent_func("Quick test query")
        
        config = {
            "func": quick_test,
            "iterations": 1,
            "warmup": 0,
            "timeout_ms": 30000
        }
        
        return self._run_single("Quick Test", config)


def run_benchmark(
    func: Callable,
    iterations: int = 10,
    name: str = "Benchmark"
) -> BenchmarkResult:
    """
    Convenience function to run a simple benchmark.
    
    Args:
        func: Function to benchmark
        iterations: Number of iterations
        name: Benchmark name
        
    Returns:
        BenchmarkResult
    """
    benchmark = Benchmark(name)
    benchmark.register(name, func, iterations)
    results = benchmark.run()
    return results[0] if results else None
