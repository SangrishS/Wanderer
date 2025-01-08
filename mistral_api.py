import asyncio
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from mistralai import Mistral

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

system_prompt = """
You are a friendly and knowledgeable local travel guide focused on Mumbai tourism. Your goal is to propose unique, memorable, and authentic experiences for visitors and locals alike who want to explore Mumbai—particularly the Churchgate area, but you can include the surrounding neighborhoods as well. Be a bit lax with time estimates.
"""

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def generate_mistral_small_latest_response_idea(prompt: str) -> str:
    client = Mistral(api_key=API_KEY)

    def api_call():
        try:
            response = client.chat.complete(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ]
            )
            print(response)
            if (
                response
                and hasattr(response, "choices")
                and response.choices
                and response.choices[0].message.content
            ):
                print("this is response", response.choices[0].message.content)
                return response.choices[0].message.content
        except Exception as e:
            print(f"Error in Mistral API call: {str(e)}")
        return ""

    try:
        # Run the API call in a separate thread to avoid blocking
        result = await asyncio.to_thread(api_call)
        return result
    except Exception as e:
        print(f"Unexpected error in generate_mistral_small_latest_response_idea: {str(e)}")
        return ""
