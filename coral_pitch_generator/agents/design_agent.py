import os
from PIL import Image, ImageDraw, ImageFont
import openai
import requests


class DesignAgent:
    def __init__(self):
        self.api_key = os.getenv("OpenAI_API_KEY")
        openai.api_key = self.api_key

    def generate_logo(self, pitch_json, output_path):
        """
        Calls OpenAI DALL·E API to generate a logo/slide for the pitch.
        Saves image to output_path.
        """
        from io import BytesIO
        prompt = f"Create a minimalist logo for a startup solving: {pitch_json.get('problem')}. Include the text '{pitch_json.get('solution','Startup')}'."
        try:
            response = openai.images.generate(
                prompt=prompt,
                n=1,
                size="512x512"
            )
            image_url = response.data[0].url
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            image = Image.open(BytesIO(img_response.content))
            image.save(output_path)
        except Exception as e:
            print(f"OpenAI Image API error: {e}")
            # Fallback to dummy image
            img = Image.new('RGB', (512, 256), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((10,10), "Startup Logo", fill=(255,255,0))
            img.save(output_path)
