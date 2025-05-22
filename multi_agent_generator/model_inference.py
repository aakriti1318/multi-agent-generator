"""
Model inference utilities for multiple LLM providers.
"""
from typing import Dict, Any, Optional, List, Union
import os
import json

class BaseModelInference:
    """Base class for model inference implementations."""
    
    def generate_text(self, prompt: str, guardrails: bool = False) -> str:
        """Generate text based on the prompt."""
        raise NotImplementedError("Subclasses must implement generate_text method")
    
    def generate_text_stream(self, prompt: str, guardrails: bool = False) -> List[str]:
        """Generate text in a streaming fashion."""
        raise NotImplementedError("Subclasses must implement generate_text_stream method")


class OpenAIModelInference(BaseModelInference):
    """
    Wrapper for OpenAI model inference.
    
    This class provides a simplified interface for text generation
    using OpenAI's models.
    """
    
    def __init__(
        self,
        model_id: str,
        params: Dict[str, Any],
        credentials: Optional[Dict[str, str]] = None,
        project_id: Optional[str] = None  # Not used for OpenAI, kept for API compatibility
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            model_id: The ID of the model to use (e.g., "gpt-4o")
            params: Generation parameters (like max_tokens, temperature, etc.)
            credentials: Optional API credentials
            project_id: Not used for OpenAI, kept for API compatibility
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package is not installed. Install it with 'pip install openai'")
            
        self.model_id = model_id
        self.params = params
        
        # Get API key from credentials or environment
        api_key = None
        if credentials and "api_key" in credentials:
            api_key = credentials["api_key"]
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            
        self.client = OpenAI(api_key=api_key)
    
    def generate_text(
        self, 
        prompt: str, 
        guardrails: bool = False  # Kept for API compatibility
    ) -> str:
        """
        Generate text based on the prompt.
        
        Args:
            prompt: The text prompt to generate from
            guardrails: Not used for OpenAI, kept for API compatibility
            
        Returns:
            The generated text response
        """
        try:
            # For system/user formatted prompts (e.g., Llama format)
            messages = self._extract_messages_from_prompt(prompt)
            
            # Generate text using the model
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=self.params.get("max_new_tokens", 1000),
                temperature=self.params.get("temperature", 0.7),
                top_p=self.params.get("top_p", 1.0),
                frequency_penalty=self.params.get("frequency_penalty", 0.0),
                presence_penalty=self.params.get("presence_penalty", 0.0)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in text generation: {e}")
            return f"Error generating text: {str(e)}"
    
    def generate_text_stream(
        self, 
        prompt: str, 
        guardrails: bool = False  # Kept for API compatibility
    ) -> List[str]:
        """
        Generate text in a streaming fashion.
        
        Args:
            prompt: The text prompt to generate from
            guardrails: Not used for OpenAI, kept for API compatibility
            
        Returns:
            List of text chunks from the stream
        """
        try:
            # For system/user formatted prompts
            messages = self._extract_messages_from_prompt(prompt)
            
            # Generate text using the model with streaming
            responses = []
            stream = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=self.params.get("max_new_tokens", 1000),
                temperature=self.params.get("temperature", 0.7),
                top_p=self.params.get("top_p", 1.0),
                frequency_penalty=self.params.get("frequency_penalty", 0.0),
                presence_penalty=self.params.get("presence_penalty", 0.0),
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    responses.append(chunk.choices[0].delta.content)
            
            return responses
            
        except Exception as e:
            print(f"Error in streaming text generation: {e}")
            return [f"Error generating text: {str(e)}"]
    
    def _extract_messages_from_prompt(self, prompt: str) -> List[Dict[str, str]]:
        """
        Convert a formatted prompt string to OpenAI messages format.
        
        This handles Llama-style prompt formats like:
        <|begin_of_text|>
        <|system|>
        System prompt
        <|user|>
        User message
        <|assistant|>
        
        Args:
            prompt: The formatted prompt string
            
        Returns:
            List of message dictionaries for OpenAI API
        """
        messages = []
        
        # Check if this is a formatted prompt
        if "<|system|>" in prompt:
            # Split by the markers
            parts = prompt.split("<|")
            
            for part in parts:
                if not part.strip():
                    continue
                    
                # Extract role and content
                if "system|>" in part:
                    content = part.replace("system|>", "", 1).strip()
                    if content:
                        messages.append({"role": "system", "content": content})
                elif "user|>" in part:
                    content = part.replace("user|>", "", 1).strip()
                    if content:
                        messages.append({"role": "user", "content": content})
                elif "assistant|>" in part:
                    # We don't include the assistant part in the prompt
                    pass
        else:
            # Simple prompt - just use as user message
            messages.append({"role": "user", "content": prompt})
            
        return messages


class WatsonXModelInference(BaseModelInference):
    """
    Wrapper for IBM WatsonX model inference.
    
    This class provides a simplified interface for text generation
    using IBM WatsonX models.
    """
    
    def __init__(
        self,
        model_id: str,
        params: Dict[str, Any],
        credentials: Optional[Dict[str, str]] = None,
        project_id: Optional[str] = None
    ):
        """
        Initialize the WatsonX model.
        
        Args:
            model_id: The ID of the model to use (e.g., "meta-llama/llama-3-3-70b-instruct")
            params: Generation parameters (decoding_method, max_new_tokens, etc.)
            credentials: Required API credentials with url and apikey
            project_id: Required WatsonX project ID
        """
        try:
            from ibm_watsonx_ai.foundation_models import ModelInference
        except ImportError:
            raise ImportError("IBM WatsonX AI package is not installed. Install it with 'pip install ibm-watsonx-ai'")
            
        self.model_id = model_id
        self.params = params
        
        # Get credentials from input or environment
        if credentials:
            self.credentials = credentials
        else:
            self.credentials = {
                "url": os.getenv("WATSONX_URL", "https://eu-de.ml.cloud.ibm.com"),
                "apikey": os.getenv("WATSONX_API_KEY")
            }
            
        self.project_id = project_id or os.getenv("WATSONX_PROJECT_ID")
            
        # Initialize the model
        self.model = ModelInference(
            model_id=self.model_id,
            params=self.params,
            credentials=self.credentials,
            project_id=self.project_id
        )
    
    def generate_text(
        self, 
        prompt: str, 
        guardrails: bool = True
    ) -> str:
        """
        Generate text based on the prompt.
        
        Args:
            prompt: The text prompt to generate from
            guardrails: Whether to enable WatsonX guardrails
            
        Returns:
            The generated text response
        """
        try:
            # Generate text using the WatsonX model
            return self.model.generate_text(prompt=prompt, guardrails=guardrails)
            
        except Exception as e:
            print(f"Error in WatsonX text generation: {e}")
            return f"Error generating text: {str(e)}"
    
    def generate_text_stream(
        self, 
        prompt: str, 
        guardrails: bool = True
    ) -> List[str]:
        """
        Generate text in a streaming fashion.
        
        Args:
            prompt: The text prompt to generate from
            guardrails: Whether to enable WatsonX guardrails
            
        Returns:
            List of text chunks from the stream
        """
        # Note: If WatsonX doesn't support streaming directly, this returns a list with a single item
        return [self.generate_text(prompt, guardrails)]


class OllamaModelInference(BaseModelInference):
    """
    Wrapper for Ollama model inference.
    
    This class provides a simplified interface for text generation
    using Ollama's models.
    """
    
    def __init__(
        self,
        model_id: str,
        params: Dict[str, Any],
        credentials: Optional[Dict[str, str]] = None,
        project_id: Optional[str] = None  # Not used for Ollama, kept for API compatibility
    ):
        """
        Initialize the Ollama client.
        
        Args:
            model_id: The ID of the model to use
            params: Generation parameters (like max_tokens, temperature, etc.)
            credentials: Optional API credentials
            project_id: Not used for Ollama, kept for API compatibility
        """
        try:
            from ollama import Ollama
        except ImportError:
            raise ImportError("Ollama package is not installed. Install it with 'pip install ollama'")
            
        self.model_id = model_id
        self.params = params
        
        # Get API key from credentials or environment
        api_key = None
        if credentials and "api_key" in credentials:
            api_key = credentials["api_key"]
        else:
            api_key = os.getenv("OLLAMA_API_KEY")
            
        self.client = Ollama(api_key=api_key)
    
    def generate_text(
        self, 
        prompt: str, 
        guardrails: bool = False  # Kept for API compatibility
    ) -> str:
        """
        Generate text based on the prompt.
        
        Args:
            prompt: The text prompt to generate from
            guardrails: Not used for Ollama, kept for API compatibility
            
        Returns:
            The generated text response
        """
        try:
            # Generate text using the model
            response = self.client.generate(
                model=self.model_id,
                prompt=prompt,
                max_tokens=self.params.get("max_new_tokens", 1000),
                temperature=self.params.get("temperature", 0.7),
                top_p=self.params.get("top_p", 1.0),
                frequency_penalty=self.params.get("frequency_penalty", 0.0),
                presence_penalty=self.params.get("presence_penalty", 0.0)
            )
            
            return response['choices'][0]['text']
            
        except Exception as e:
            print(f"Error in text generation: {e}")
            return f"Error generating text: {str(e)}"
    
    def generate_text_stream(
        self, 
        prompt: str, 
        guardrails: bool = False  # Kept for API compatibility
    ) -> List[str]:
        """
        Generate text in a streaming fashion.
        
        Args:
            prompt: The text prompt to generate from
            guardrails: Not used for Ollama, kept for API compatibility
            
        Returns:
            List of text chunks from the stream
        """
        try:
            # Generate text using the model with streaming
            responses = []
            stream = self.client.generate_stream(
                model=self.model_id,
                prompt=prompt,
                max_tokens=self.params.get("max_new_tokens", 1000),
                temperature=self.params.get("temperature", 0.7),
                top_p=self.params.get("top_p", 1.0),
                frequency_penalty=self.params.get("frequency_penalty", 0.0),
                presence_penalty=self.params.get("presence_penalty", 0.0)
            )
            
            for chunk in stream:
                if chunk['choices'][0]['text']:
                    responses.append(chunk['choices'][0]['text'])
            
            return responses
            
        except Exception as e:
            print(f"Error in streaming text generation: {e}")
            return [f"Error generating text: {str(e)}"]


def create_model_inference(
    provider: str,
    model_id: str,
    params: Dict[str, Any],
    credentials: Optional[Dict[str, str]] = None,
    project_id: Optional[str] = None
) -> BaseModelInference:
    """
    Factory function to create the appropriate model inference instance.
    
    Args:
        provider: The LLM provider ("openai", "watsonx", or "ollama")
        model_id: The ID of the model to use
        params: Generation parameters
        credentials: Optional API credentials
        project_id: Optional project ID (required for WatsonX)
        
    Returns:
        An instance of the appropriate model inference class
    """
    if provider.lower() == "openai":
        return OpenAIModelInference(
            model_id=model_id,
            params=params,
            credentials=credentials
        )
    elif provider.lower() == "watsonx":
        return WatsonXModelInference(
            model_id=model_id,
            params=params,
            credentials=credentials,
            project_id=project_id
        )
    elif provider.lower() == "ollama":
        return OllamaModelInference(
            model_id=model_id,
            params=params,
            credentials=credentials
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'openai', 'watsonx', or 'ollama'.")
