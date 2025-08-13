from .base import BaseConnector
import asyncio
import google.generativeai as genai
from config import settings

class Gemini_Connector(BaseConnector):

    def __init__(self):
        super().__init__("Google Gemini")
        print("setting google key",settings.google_api_key)
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.input_rate=settings.gemini_cost_per_1M_input_tokens
        self.output_rate=settings.gemini_cost_per_1M_output_tokens

    async def detect_language_implementation(self, audio_path:str)->tuple[str,float,float]:
        try:
            prompt = """
                Analyze this audio file and detect the primary spoken language. 
                Respond with ONLY the ISO 639-1 language code (e.g., 'en' for English, 'hi' for Hindi, 'ta' for Tamil).
                If multiple languages are present, return the dominant one.
                If no clear language can be detected, respond with 'unknown'.
                """
            audio_file_obj = genai.upload_file(audio_path)
            response = await asyncio.to_thread(
                self.model.generate_content,
                [prompt, audio_file_obj]
            )

            #print("this is the response ",response)

            language_code = response.text.strip().lower()
            
            usage_metadata = getattr(response, 'usage_metadata', None)
            if usage_metadata:
                input_tokens = getattr(usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(usage_metadata, 'candidates_token_count', 0)
                total_tokens = getattr(usage_metadata, 'total_token_count', 0)
                
                tokens = {
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'total_tokens': total_tokens
                }
            
            total_cost=self.get_estimated_cost(tokens=tokens)

            if len(language_code) == 2 and language_code.isalpha():
                return language_code, float(total_tokens), total_cost
            elif language_code == 'unknown':
                return None
            else:
                words = language_code.split()
                for word in words:
                    if len(word) == 2 and word.isalpha():
                        return word
                return None       
                
        except Exception as e:
            raise Exception(f"Google Gemini API error: {str(e)}")

    def get_estimated_cost(self, tokens:dict)->float:
        input_tokens = tokens.get('input_tokens', 0)
        output_tokens = tokens.get('output_tokens', 0)

        # Calculate costs per 1M tokens
        input_cost = (input_tokens / 1_000_000) * self.input_rate
        output_cost = (output_tokens / 1_000_000) * self.output_rate

        total_cost = input_cost + output_cost

        return total_cost
