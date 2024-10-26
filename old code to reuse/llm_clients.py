import os
import logging
import json
from typing import List, Dict
from google.cloud import aiplatform
import openai
import anthropic
from anthropic import Anthropic
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel
from groq import AsyncGroq
from types import SimpleNamespace
import aiosqlite
from dotenv import load_dotenv

# Load environment variables from the root .env file
load_dotenv()

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, agent_config):
        self.config = SimpleNamespace(**agent_config)
        self.client = self._initialize_client()

    def _get_api_key(self, provider):
        if provider.lower() == "groq":
            return os.getenv("GROQ_API_KEY")
        elif provider.lower() == "google":
            return os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        elif provider.lower() == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif provider.lower() == "deepseek":
            return os.getenv("DEEPSEEK_API_KEY")
        elif provider.lower() == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _initialize_client(self):
        if self.config.provider.lower() == "groq":
            return AsyncGroq(api_key=self._get_api_key("groq"))
        elif self.config.provider.lower() == "google":
            credentials = service_account.Credentials.from_service_account_file(self._get_api_key("google"))
            aiplatform.init(project=os.getenv("PROJECT_ID"), location=os.getenv("REGION"), credentials=credentials)
            return GenerativeModel(model_name=self.config.model, credentials=credentials)
        elif self.config.provider.lower() == "anthropic":
            return Anthropic(api_key=self._get_api_key("anthropic"))
        elif self.config.provider.lower() in ["openai", "deepseek"]:
            return None
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    async def generate_response(self, messages):
        try:
            logger.info(f"Generating response for messages: {messages}")
            response = await self._call_external_api(messages)
            logger.info(f"{self.config.provider} response: {response}")
            if not response:
                logger.error(f"Received null response from {self.config.provider}")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None

    async def _call_external_api(self, messages):
        if self.config.provider.lower() == "groq":
            response = await self.client.chat.completions.create(
                model=os.getenv("GROQ_MODEL_ID"),
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty
            )
            return response.choices[0].message.content
        elif self.config.provider.lower() == "google":
            try:
                chat = self.client.start_chat()
                response = await chat.send_message_async(" ".join([m['content'] for m in messages]))
                return response.text
            except Exception as e:
                logger.error(f"Error calling Google API: {e}")
                return None
        elif self.config.provider.lower() in ["openai", "deepseek"]:
            api_key = self._get_api_key(self.config.provider)
            base_url = "https://api.openai.com/v1" if self.config.provider.lower() == "openai" else "https://api.deepseek.com"

            top_p = max(0.01, self.config.top_p) if self.config.provider.lower() == "deepseek" else self.config.top_p

            async with openai.AsyncOpenAI(api_key=api_key, base_url=base_url) as client:
                response = await client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    top_p=top_p,
                    frequency_penalty=self.config.frequency_penalty,
                    presence_penalty=self.config.presence_penalty
                )
                return response.choices[0].message.content
        elif self.config.provider.lower() == "anthropic":
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                messages=messages,
                temperature=self.config.temperature,
            )
            return response.content[0].text
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

async def get_agent_config(db, agent_name: str) -> Dict:
    async with db.execute("""
        SELECT name, system_prompt, provider, model, endpoint, temperature, max_tokens, top_p, frequency_penalty, presence_penalty
        FROM agents
        WHERE name = ?
    """, (agent_name,)) as cursor:
        row = await cursor.fetchone()
        if row:
            return dict(zip([
                'name', 'system_prompt', 'provider', 'model', 'endpoint', 'temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty'
            ], row))
        else:
            logger.warning(f"No configuration found for agent: {agent_name}")
            return None

async def get_llm_client(db, agent_name: str) -> LLMClient:
    agent_config = await get_agent_config(db, agent_name)
    if not agent_config or agent_config.get('provider', '').lower() not in ["groq", "google", "openai", "anthropic", "deepseek"]:
        logger.warning(f"Invalid or missing provider for agent {agent_name}. Using default: groq")
        agent_config = {'provider': 'groq', 'name': agent_name}
    return LLMClient(agent_config)
