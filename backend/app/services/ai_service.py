import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.enabled = bool(api_key)
        self.model = None

        if not self.enabled:
            print("GOOGLE_API_KEY not found. AI chat responses are disabled.")
            return

        genai.configure(api_key=api_key)
        
        # Auto-detect the best available model
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    self.model_name = m.name
                    self.model = genai.GenerativeModel(self.model_name)
                    print(f"Successfully initialized with model: {self.model_name}")
                    break
        except Exception as e:
            print(f"Error listing models: {e}")
            # Fallback to a common name just in case
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def generate_response(self, prompt: str, image_path: str = None):
        if not self.enabled or self.model is None:
            return "AI service is unavailable because GOOGLE_API_KEY is not configured."

        try:
            content = [prompt]
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path)
                content.append(img)
            
            response = await self.model.generate_content_async(content)
            return response.text
        except Exception as e:
            return f"Error generating AI response: {str(e)}"

    async def get_multimodal_description(self, image_path: str):
        prompt = "Describe this e-commerce product in detail. Include product name, category, features, and target audience. Format as a clean description."
        return await self.generate_response(prompt, image_path)

ai_service = AIService()
