"""
Command line interface for multi-agent-generator.
"""
import argparse
import json
import os
from dotenv import load_dotenv
from .generator import AgentGenerator
from .frameworks import (
    create_crewai_code,
    create_crewai_flow_code,
    create_langgraph_code,
    create_react_code
)

# Load environment variables from .env file if present
load_dotenv()

def main():
    """Command line entry point."""
    parser = argparse.ArgumentParser(description="Generate multi-agent AI code")
    parser.add_argument("prompt", help="Plain English description of what you need")
    parser.add_argument(
        "--framework", 
        choices=["crewai", "crewai-flow", "langgraph", "react"], 
        default="crewai",
        help="Agent framework to use (default: crewai)"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "watsonx", "ollama"],
        default="openai",
        help="LLM provider to use (default: openai)"
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
    
    args = parser.parse_args()
    
    # Check for API keys in environment
    if args.provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key using:")
        print("export OPENAI_API_KEY=your_api_key_here")
        return
    
    if args.provider == "watsonx" and (not os.getenv("WATSONX_API_KEY") or not os.getenv("WATSONX_PROJECT_ID")):
        print("Error: WatsonX credentials not found in environment variables.")
        print("Please set your WatsonX credentials using:")
        print("export WATSONX_API_KEY=your_api_key_here")
        print("export WATSONX_PROJECT_ID=your_project_id_here")
        return

    if args.provider == "ollama" and not os.getenv("OLLAMA_API_KEY"):
        print("Error: OLLAMA_API_KEY environment variable not found.")
        print("Please set your Ollama API key using:")
        print("export OLLAMA_API_KEY=your_api_key_here")
        return
    
    # Analyze the prompt with specified provider
    generator = AgentGenerator(provider=args.provider)
    print(f"Analyzing prompt using {args.provider.upper()}...")
    config = generator.analyze_prompt(args.prompt, args.framework)
    
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

if __name__ == "__main__":
    main()
