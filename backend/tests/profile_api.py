import asyncio
import aiohttp
import json
import sys
import os

# Add the parent directory of 'app' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

API_URL = f"http://localhost:{settings.BACKEND_PORT}"

async def profile_create_message():
    try:
        async with aiohttp.ClientSession() as session:
            # First, create a conversation
            async with session.post(f"{API_URL}/conversation/test/conversations") as response:
                print(f"Response status: {response.status}")
                conversation = await response.json()
                print("Create Conversation Response:", json.dumps(conversation, indent=2))
                conversation_id = conversation['id']

            # Now, create a message in that conversation
            message_data = {
                "content": "Hello, can you help me practice English?"
            }
            async with session.post(
                f"{API_URL}/conversation/test/conversations/{conversation_id}/messages",
                json=message_data
            ) as response:
                print(f"Response status: {response.status}")
                result = await response.json()
                print("Create Message Response:", json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error in profile_create_message: {e}")
        print(f"Response status: {getattr(response, 'status', 'N/A')}")
        print(f"Response content: {await getattr(response, 'text', lambda: 'N/A')()}")

async def profile_create_voice_message():
    try:
        async with aiohttp.ClientSession() as session:
            # First, create a conversation
            async with session.post(f"{API_URL}/conversation/test/conversations") as response:
                print(f"Response status: {response.status}")
                conversation = await response.json()
                print("Create Conversation Response:", json.dumps(conversation, indent=2))
                conversation_id = conversation['id']

            # Now, create a voice message in that conversation
            # For this test, we'll use a dummy audio content
            voice_message_data = {
                "audio_content": "dummy audio content"
            }
            async with session.post(
                f"{API_URL}/conversation/test/conversations/{conversation_id}/voice_messages",
                json=voice_message_data
            ) as response:
                print(f"Response status: {response.status}")
                result = await response.json()
                print("Create Voice Message Response:", json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error in profile_create_voice_message: {e}")
        print(f"Response status: {getattr(response, 'status', 'N/A')}")
        print(f"Response content: {await getattr(response, 'text', lambda: 'N/A')()}")

async def main():
    await profile_create_message()
    await profile_create_voice_message()

if __name__ == "__main__":
    asyncio.run(main())
