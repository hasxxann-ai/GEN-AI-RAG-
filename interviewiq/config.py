import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from utils.nexus_llm import NexusChatModel

load_dotenv()

def get_llm():
    use_custom = os.getenv("USE_CUSTOM_NEXUS_WRAPPER", "false").lower() == "true"
    
    if use_custom:
        return NexusChatModel(
            api_key=os.getenv("NEXUS_API_KEY"),
            base_url=os.getenv("NEXUS_BASE_URL"),
            model=os.getenv("NEXUS_MODEL", "default-model"),
            temperature=0.3
        )
    else:
        return ChatOpenAI(
            api_key=os.getenv("NEXUS_API_KEY", ""),
            base_url=os.getenv("NEXUS_BASE_URL", ""),
            model=os.getenv("NEXUS_MODEL", "default-model"),
            temperature=0.3,
        )
