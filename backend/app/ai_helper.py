import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

def generate_ai_response(user_message: str, conversation_history: list) -> str:
    # Prepare the conversation history for the API call
    messages = [
        {"role": "system", "content": "You are a helpful language tutor assistant. Provide explanations, corrections, and examples to help the user improve their language skills."}
    ]
    
    # Add conversation history
    for message in conversation_history:
        role = "user" if message.is_user else "assistant"
        messages.append({"role": role, "content": message.content})
    
    # Add the current user message
    messages.append({"role": "user", "content": user_message})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )

        ai_response = response.choices[0].message['content'].strip()
        return ai_response
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        return "I apologize, but I'm having trouble generating a response at the moment. Please try again later."
