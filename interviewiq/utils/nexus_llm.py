import os
import requests
from typing import Any, List, Mapping, Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration

class NexusChatModel(BaseChatModel):
    """Fallback custom wrapper for Nexus API if not OpenAI-compatible."""
    
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "default-model"
    temperature: float = 0.3
    
    @property
    def _llm_type(self) -> str:
        return "nexus-chat"
        
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        
        # Convert LangChain messages to a dict format
        formatted_messages = []
        for m in messages:
            if isinstance(m, SystemMessage):
                formatted_messages.append({"role": "system", "content": m.content})
            elif isinstance(m, HumanMessage):
                formatted_messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                formatted_messages.append({"role": "assistant", "content": m.content})
                
        # TODO: Define the endpoint path
        endpoint = f"{self.base_url}/chat/completions" 
        
        # TODO: Define the auth header
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # TODO: Define the request body
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.temperature
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # TODO: Parse the response
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])
            
        except Exception as e:
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=f"Error: {str(e)}"))])

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model": self.model, "temperature": self.temperature}
