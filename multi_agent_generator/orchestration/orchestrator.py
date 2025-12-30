# multi_agent_generator/orchestration/orchestrator.py
"""
Orchestrator - High-level interface for creating orchestrated multi-agent systems.
No-code approach: Users describe their needs and get complete orchestration code.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .patterns import (
    PatternType,
    OrchestrationPattern,
    get_pattern,
    list_patterns,
)


@dataclass
class OrchestrationConfig:
    """Configuration for an orchestrated system."""
    pattern: PatternType
    agents: List[Dict[str, Any]]
    settings: Dict[str, Any]
    framework: str = "langgraph"


class Orchestrator:
    """
    High-level orchestrator for creating multi-agent systems.
    Provides a no-code interface for pattern selection and configuration.
    """
    
    def __init__(self, model_inference=None):
        """
        Initialize the orchestrator.
        
        Args:
            model_inference: Optional ModelInference for LLM-based suggestions
        """
        self.model = model_inference
        
    def list_available_patterns(self) -> List[Dict[str, Any]]:
        """List all available orchestration patterns."""
        return list_patterns()
    
    def get_pattern_template(self, pattern_type: PatternType) -> Dict[str, Any]:
        """Get the configuration template for a pattern."""
        pattern = get_pattern(pattern_type)
        return pattern.get_config_template()
    
    def suggest_pattern(self, description: str) -> PatternType:
        """
        Suggest the best pattern based on task description.
        
        Args:
            description: Natural language description of the task
            
        Returns:
            Recommended PatternType
        """
        description_lower = description.lower()
        
        # Pattern matching rules
        patterns_keywords = {
            PatternType.SUPERVISOR: [
                "coordinate", "manage", "delegate", "oversee", "lead", "manager",
                "supervisor", "boss", "assign", "project manager"
            ],
            PatternType.DEBATE: [
                "debate", "argue", "discuss", "consensus", "pros and cons",
                "perspectives", "opinions", "decide", "evaluate options"
            ],
            PatternType.VOTING: [
                "vote", "poll", "majority", "election", "choose", "select",
                "democratic", "ensemble", "aggregate opinions"
            ],
            PatternType.PIPELINE: [
                "pipeline", "sequential", "steps", "stages", "workflow",
                "transform", "process", "chain", "one after another"
            ],
            PatternType.MAP_REDUCE: [
                "parallel", "chunk", "split", "combine", "aggregate",
                "distribute", "large", "scale", "summarize multiple"
            ]
        }
        
        # Score each pattern
        scores = {}
        for pattern_type, keywords in patterns_keywords.items():
            score = sum(1 for kw in keywords if kw in description_lower)
            scores[pattern_type] = score
        
        # Return highest scoring pattern
        best_pattern = max(scores, key=scores.get)
        
        # If no clear match, default to Supervisor
        if scores[best_pattern] == 0:
            return PatternType.SUPERVISOR
            
        return best_pattern
    
    def create_config_from_description(
        self,
        description: str,
        num_agents: int = 3,
        framework: str = "langgraph"
    ) -> OrchestrationConfig:
        """
        Create orchestration configuration from natural language description.
        
        Args:
            description: Natural language description of what's needed
            num_agents: Number of agents to create
            framework: Target framework
            
        Returns:
            OrchestrationConfig ready for code generation
        """
        # Suggest pattern
        pattern_type = self.suggest_pattern(description)
        pattern = get_pattern(pattern_type)
        
        # Generate agents based on pattern
        agents = self._generate_agents_for_pattern(pattern_type, description, num_agents)
        
        # Get default settings
        template = pattern.get_config_template()
        settings = template.get("settings", {})
        
        return OrchestrationConfig(
            pattern=pattern_type,
            agents=agents,
            settings=settings,
            framework=framework
        )
    
    def _generate_agents_for_pattern(
        self,
        pattern_type: PatternType,
        description: str,
        num_agents: int
    ) -> List[Dict[str, Any]]:
        """Generate appropriate agents for the pattern."""
        
        if pattern_type == PatternType.SUPERVISOR:
            agents = [
                {
                    "name": "supervisor",
                    "role": "Project Coordinator",
                    "goal": "Coordinate team members and ensure quality output",
                    "backstory": "Experienced project manager"
                }
            ]
            for i in range(num_agents - 1):
                agents.append({
                    "name": f"worker_{i+1}",
                    "role": f"Specialist {i+1}",
                    "goal": f"Complete assigned tasks efficiently",
                    "backstory": f"Expert in their domain"
                })
                
        elif pattern_type == PatternType.DEBATE:
            agents = [
                {
                    "name": "advocate",
                    "role": "Advocate",
                    "goal": "Present arguments in favor",
                    "position": "pro"
                },
                {
                    "name": "critic",
                    "role": "Critic",
                    "goal": "Present counter-arguments",
                    "position": "con"
                }
            ]
            if num_agents > 2:
                agents.append({
                    "name": "moderator",
                    "role": "Moderator",
                    "goal": "Facilitate debate and synthesize conclusions",
                    "position": "neutral"
                })
                
        elif pattern_type == PatternType.VOTING:
            agents = []
            for i in range(num_agents):
                agents.append({
                    "name": f"voter_{i+1}",
                    "role": f"Expert Voter {i+1}",
                    "goal": "Evaluate options and cast informed vote",
                    "weight": 1
                })
                
        elif pattern_type == PatternType.PIPELINE:
            stage_names = ["Initial Processor", "Enhancer", "Quality Checker", "Finalizer"]
            agents = []
            for i in range(num_agents):
                stage_name = stage_names[i] if i < len(stage_names) else f"Stage {i+1}"
                agents.append({
                    "name": f"stage_{i+1}",
                    "role": stage_name,
                    "goal": f"Process and transform data at stage {i+1}"
                })
                
        elif pattern_type == PatternType.MAP_REDUCE:
            agents = []
            # Mappers
            for i in range(num_agents - 1):
                agents.append({
                    "name": f"mapper_{i+1}",
                    "role": f"Parallel Processor {i+1}",
                    "goal": "Process a chunk of the input data"
                })
            # Reducer
            agents.append({
                "name": "reducer",
                "role": "Aggregator",
                "goal": "Combine and synthesize all mapper outputs"
            })
        else:
            # Default agents
            agents = [{
                "name": f"agent_{i+1}",
                "role": f"Agent {i+1}",
                "goal": "Complete assigned tasks"
            } for i in range(num_agents)]
        
        return agents
    
    def generate_code(self, config: OrchestrationConfig) -> str:
        """
        Generate complete orchestration code from configuration.
        
        Args:
            config: OrchestrationConfig with pattern, agents, and settings
            
        Returns:
            Generated Python code
        """
        pattern = get_pattern(config.pattern)
        
        # Prepare config dict
        config_dict = {
            "agents": config.agents,
            "settings": config.settings
        }
        
        return pattern.generate_code(config_dict, config.framework)
    
    def validate_config(self, config: OrchestrationConfig) -> List[str]:
        """
        Validate orchestration configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        pattern = get_pattern(config.pattern)
        
        # Pattern-specific validation
        config_dict = {"agents": config.agents, "settings": config.settings}
        errors.extend(pattern.validate_config(config_dict))
        
        # General validation
        if not config.agents:
            errors.append("At least one agent is required")
            
        if config.framework not in ["langgraph", "crewai", "crewai-flow"]:
            errors.append(f"Unsupported framework: {config.framework}")
        
        return errors


def create_orchestrated_system(
    description: str,
    num_agents: int = 3,
    framework: str = "langgraph",
    pattern: Optional[PatternType] = None
) -> str:
    """
    Convenience function to create an orchestrated multi-agent system.
    
    Args:
        description: Natural language description of the system
        num_agents: Number of agents to create
        framework: Target framework (langgraph, crewai, crewai-flow)
        pattern: Optional specific pattern (auto-detected if not provided)
        
    Returns:
        Generated Python code for the orchestrated system
    """
    orchestrator = Orchestrator()
    
    if pattern:
        # Use specified pattern
        agents = orchestrator._generate_agents_for_pattern(pattern, description, num_agents)
        template = get_pattern(pattern).get_config_template()
        config = OrchestrationConfig(
            pattern=pattern,
            agents=agents,
            settings=template.get("settings", {}),
            framework=framework
        )
    else:
        # Auto-detect pattern
        config = orchestrator.create_config_from_description(description, num_agents, framework)
    
    return orchestrator.generate_code(config)
