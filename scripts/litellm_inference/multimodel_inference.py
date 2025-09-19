import os
from typing import Dict, List, Optional, Union
from pydantic import BaseModel
from dotenv import load_dotenv
from litellm import completion  # Unified API

# Load environment variables
load_dotenv()

class Message(BaseModel):
    role: str  
    content: str

class ModelInference:
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None, 
        **default_params
    ):
        """
        Unified LiteLLM-based model inference class.
        """
        self.model = model
        self.api_key = api_key or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or os.getenv("API_BASE")
        self.default_params = default_params

    def generate_text(
        self,
        messages: List[Union[Dict, Message]],
        **override_params
    ) -> str:
        """
        Synchronously generate text.
        """
        try:
            msg_list = [
                m.dict() if isinstance(m, Message) else m for m in messages
            ]
            response = completion(
                model=self.model,
                messages=msg_list,
                api_key=self.api_key,
                api_base=self.api_base,
                **{**self.default_params, **override_params}
            )
            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"Model inference failed: {e}")