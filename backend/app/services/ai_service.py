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
        
        # Try a list of compatible models to avoid 404 errors
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
        self.model = None
        
        for m_name in models_to_try:
            try:
                self.model = genai.GenerativeModel(m_name)
                # Test the model with a tiny call to ensure it actually exists
                self.model_name = m_name
                print(f"Successfully initialized with model: {self.model_name}")
                break
            except Exception:
                continue
        
        if not self.model:
            print("CRITICAL: No compatible Gemini models found.")
            self.enabled = False

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
