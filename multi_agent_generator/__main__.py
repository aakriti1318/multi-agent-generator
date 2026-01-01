# mutli-agent-generator/__main__.py
"""
Command line interface for multi-agent-generator.
"""
import argparse
import json
from dotenv import load_dotenv
from .generator import AgentGenerator
from .frameworks import (
    create_crewai_code,
    create_crewai_flow_code,
    create_langgraph_code,
    create_react_code,
    create_agno_code
)
from .tools.tool_generator import ToolGenerator
from .tools.tool_registry import get_tool_registry, ToolCategory
from .evaluation.evaluator import AgentEvaluator
from .orchestration.orchestrator import Orchestrator
from .orchestration.patterns import PatternType

# Load environment variables from .env file if present
load_dotenv()


def main():
    """Command line entry point."""
    parser = argparse.ArgumentParser(
        description="Generate multi-agent AI code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate agent code
  multi-agent-generator "Create a research assistant" --framework langgraph

  # Generate a custom tool
  multi-agent-generator --tool "Create a tool to fetch weather data from an API"

  # Evaluate agent output
  multi-agent-generator --evaluate --query "What is AI?" --response "AI is artificial intelligence..."

  # Suggest orchestration pattern
  multi-agent-generator --orchestrate "I need agents to debate and reach consensus"

  # List available tools
  multi-agent-generator --list-tools

  # List orchestration patterns
  multi-agent-generator --list-patterns
        """
    )
    parser.add_argument("prompt", nargs="?", help="Plain English description of what you need")
    parser.add_argument(
        "--framework", 
        choices=["crewai", "crewai-flow", "langgraph", "react", "react-lcel", "agno"], 
        default="crewai",
        help="Agent framework to use (default: crewai)"
    )
    parser.add_argument(
        "--process",
        choices=["sequential", "hierarchical"],
        default="sequential",
        help="Process type for CrewAI (default: sequential)"
    )
    parser.add_argument(
        "--provider",
        default="openai",
        help="LLM provider to use (e.g., openai, watsonx, ollama, anthropic, groq, etc.)"
    )
    parser.add_argument(
        "--output", 
        help="Output file path (default: print to console)"
    )
    parser.add_argument(
        "--format",
        choices=["code", "json", "both"],
        default="code",
        help="Output format (default: code)"
    )
    
    # Tool generation arguments
    parser.add_argument(
        "--tool",
        metavar="DESCRIPTION",
        help="Generate a custom tool from description"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available tools in the registry"
    )
    parser.add_argument(
        "--tool-category",
        choices=[c.value for c in ToolCategory],
        help="Filter tools by category when using --list-tools"
    )
    
    # Evaluation arguments
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Evaluate agent output quality"
    )
    parser.add_argument(
        "--query",
        help="Query/prompt for evaluation (used with --evaluate)"
    )
    parser.add_argument(
        "--response",
        help="Agent response to evaluate (used with --evaluate)"
    )
    parser.add_argument(
        "--expected",
        help="Expected output for accuracy comparison (optional, used with --evaluate)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Minimum passing score threshold (default: 0.7)"
    )
    
    # Orchestration arguments
    parser.add_argument(
        "--orchestrate",
        metavar="DESCRIPTION",
        help="Get orchestration pattern suggestion for a task description"
    )
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="List all available orchestration patterns"
    )
    parser.add_argument(
        "--pattern",
        choices=[p.value for p in PatternType],
        help="Generate code for a specific orchestration pattern"
    )
    parser.add_argument(
        "--num-agents",
        type=int,
        default=3,
        help="Number of agents for orchestration (default: 3)"
    )
    

    args = parser.parse_args()
    
    # Handle tool listing
    if args.list_tools:
        handle_list_tools(args.tool_category)
        return
    
    # Handle tool generation
    if args.tool:
        handle_tool_generation(args.tool, args.output)
        return
    
    # Handle evaluation
    if args.evaluate:
        if not args.query or not args.response:
            parser.error("--evaluate requires both --query and --response")
        handle_evaluation(args.query, args.response, args.expected, args.threshold, args.output)
        return
    
    # Handle orchestration pattern listing
    if args.list_patterns:
        handle_list_patterns()
        return
    
    # Handle orchestration suggestion
    if args.orchestrate:
        handle_orchestration(args.orchestrate, args.pattern, args.num_agents, args.framework, args.output)
        return
    
    # Handle pattern code generation
    if args.pattern:
        handle_orchestration(None, args.pattern, args.num_agents, args.framework, args.output)
        return
    
    # Default: agent code generation (requires prompt)
    if not args.prompt:
        parser.error("prompt is required for agent code generation")
    
    # Initialize generator
    generator = AgentGenerator(provider=args.provider)
    print(f"Analyzing prompt using {args.provider.upper()}...")
    config = generator.analyze_prompt(args.prompt, args.framework)
    
    # Add process type to config for CrewAI frameworks
    if args.framework in ["crewai", "crewai-flow"]:
        config["process"] = args.process
        print(f"Using {args.process} process for CrewAI...")
    
    # Generate code based on the framework
    print(f"Generating {args.framework} code...")
    if args.framework == "crewai":
        code = create_crewai_code(config)
    elif args.framework == "crewai-flow":
        code = create_crewai_flow_code(config)
    elif args.framework == "langgraph":
        code = create_langgraph_code(config)
    elif args.framework == "react":
        code = create_react_code(config)
    elif args.framework == "react-lcel":
        from .frameworks.react_generator import create_react_lcel_code
        code = create_react_lcel_code(config)
    elif args.framework == "agno":
        code = create_agno_code(config)

    else:
        print(f"Unsupported framework: {args.framework}")
        return
    
    # Prepare output
    if args.format == "code":
        output = code
    elif args.format == "json":
        output = json.dumps(config, indent=2)
    else:  # both
        output = f"// Configuration:\n{json.dumps(config, indent=2)}\n\n// Generated Code:\n{code}"
    
    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Output successfully written to {args.output}")
    else:
        print(output)


def handle_list_tools(category_filter: str = None):
    """List all available tools in the registry."""
    registry = get_tool_registry()
    
    if category_filter:
        category = ToolCategory(category_filter)
        tools = registry.list_by_category(category)
        print(f"\n📦 Tools in category '{category_filter}':\n")
    else:
        tools = registry.list_all()
        print("\n📦 All Available Tools:\n")
    
    if not tools:
        print("  No tools found.")
        return
    
    # Group by category if not filtered
    if not category_filter:
        from collections import defaultdict
        by_category = defaultdict(list)
        for tool in tools:
            by_category[tool.category.value].append(tool)
        
        for cat, cat_tools in sorted(by_category.items()):
            print(f"  [{cat.upper()}]")
            for tool in cat_tools:
                print(f"    • {tool.name}: {tool.description}")
            print()
    else:
        for tool in tools:
            print(f"  • {tool.name}: {tool.description}")
            if tool.parameters:
                print(f"    Parameters: {list(tool.parameters.keys())}")


def handle_tool_generation(description: str, output_file: str = None):
    """Generate a custom tool from description."""
    print(f"🔧 Generating tool from description...")
    print(f"   \"{description}\"\n")
    
    generator = ToolGenerator()
    tool = generator.generate_from_description(description)
    
    output = f'''# Auto-generated tool: {tool.name}
# Category: {tool.category.value}
# Description: {tool.description}

{tool.code}

# Tool metadata
TOOL_INFO = {{
    "name": "{tool.name}",
    "description": "{tool.description}",
    "category": "{tool.category.value}",
    "parameters": {json.dumps(tool.parameters, indent=8)}
}}
'''
    
    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
        print(f"✅ Tool generated and saved to {output_file}")
    else:
        print(output)
    
    print(f"\n📋 Tool Summary:")
    print(f"   Name: {tool.name}")
    print(f"   Category: {tool.category.value}")
    print(f"   Parameters: {list(tool.parameters.keys()) if tool.parameters else 'None'}")


def handle_evaluation(query: str, response: str, expected: str = None, threshold: float = 0.7, output_file: str = None):
    """Evaluate agent output quality."""
    print("📊 Evaluating agent output...\n")
    
    evaluator = AgentEvaluator(thresholds={"overall": threshold})
    
    if expected:
        result = evaluator.evaluate(query, response, ground_truth=expected)
    else:
        result = evaluator.evaluate(query, response)
    
    # Display results
    metrics = result.metrics
    status = "✅ PASSED" if result.passed else "❌ FAILED"
    
    output_lines = [
        f"Evaluation Results: {status}",
        f"{'=' * 50}",
        f"Query: {query[:100]}{'...' if len(query) > 100 else ''}",
        f"Response: {response[:100]}{'...' if len(response) > 100 else ''}",
        "",
        "Metrics:",
        f"  • Relevance:        {metrics.relevance_score:.2f}",
        f"  • Completeness:     {metrics.completeness_score:.2f}",
        f"  • Coherence:        {metrics.coherence_score:.2f}",
        f"  • Accuracy:         {metrics.accuracy_score:.2f}",
        f"  • Task Completion:  {metrics.task_completion_rate:.2f}",
        f"  • Response Time:    {metrics.response_time_ms:.2f}ms",
        f"  • Token Count:      {metrics.token_count}",
        "",
        f"Overall Score: {metrics.overall_score():.3f} (threshold: {threshold})",
    ]
    
    if result.feedback:
        output_lines.append("\nFeedback:")
        for fb in result.feedback:
            output_lines.append(f"  • {fb}")
    
    if result.errors:
        output_lines.append("\nErrors:")
        for err in result.errors:
            output_lines.append(f"  ⚠️  {err}")
    
    output = "\n".join(output_lines)
    
    if output_file:
        # Write JSON format to file
        with open(output_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        print(output)
        print(f"\n📄 Full results saved to {output_file}")
    else:
        print(output)


def handle_list_patterns():
    """List all available orchestration patterns."""
    orchestrator = Orchestrator()
    patterns = orchestrator.list_available_patterns()
    
    print("\n🔄 Available Orchestration Patterns:\n")
    
    for pattern in patterns:
        print(f"  [{pattern['name'].upper()}]")
        print(f"    Description: {pattern['description']}")
        print(f"    Use Cases:")
        for use_case in pattern.get('use_cases', [])[:3]:
            print(f"      • {use_case}")
        print()


def handle_orchestration(description: str = None, pattern_name: str = None, num_agents: int = 3, framework: str = "langgraph", output_file: str = None):
    """Handle orchestration pattern suggestion and code generation."""
    from .orchestration.orchestrator import OrchestrationConfig
    from .orchestration.patterns import get_pattern
    
    orchestrator = Orchestrator()
    
    # Determine pattern
    if pattern_name:
        pattern_type = PatternType(pattern_name)
        print(f"🔄 Using orchestration pattern: {pattern_name}")
    elif description:
        pattern_type = orchestrator.suggest_pattern(description)
        print(f"🔄 Analyzing task description...")
        print(f"   \"{description}\"\n")
        print(f"📌 Recommended pattern: {pattern_type.value}")
    else:
        print("Error: Either --orchestrate or --pattern is required")
        return
    
    # Generate orchestration code
    print(f"\n🏗️  Generating {pattern_type.value} orchestration code for {framework}...\n")
    
    # Create configuration from description or pattern
    if description:
        config = orchestrator.create_config_from_description(description, num_agents, framework)
    else:
        # Generate agents for the pattern
        agents = orchestrator._generate_agents_for_pattern(pattern_type, "Generic task", num_agents)
        template = get_pattern(pattern_type).get_config_template()
        config = OrchestrationConfig(
            pattern=pattern_type,
            agents=agents,
            settings=template.get("settings", {}),
            framework=framework
        )
    
    code = orchestrator.generate_code(config)
    
    if output_file:
        with open(output_file, "w") as f:
            f.write(code)
        print(f"✅ Orchestration code saved to {output_file}")
    else:
        print(code)
    
    print(f"\n📋 Orchestration Summary:")
    print(f"   Pattern: {pattern_type.value}")
    print(f"   Framework: {framework}")
    print(f"   Agents: {[a['name'] for a in config.agents]}")


if __name__ == "__main__":
    main()
