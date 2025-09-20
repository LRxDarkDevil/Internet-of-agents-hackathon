import os
from PIL import Image, ImageDraw, ImageFont
import requests
import base64


class DesignAgent:
    def __init__(self):
        self.api_key = os.getenv("AI_ML_API_KEY")

    def generate_logo(self, pitch_json, output_path):
        """
        Calls AIMLAPI to generate a logo/slide for the pitch.
        Saves image to output_path.
        """
        prompt = f"Create a minimalist logo for a startup solving: {pitch_json.get('problem')}. Include the text '{pitch_json.get('solution','Startup')}'."
        url = "https://api.aimlapi.com/v1/images/generations/"
        payload = {
            "model": "flux/schnell",
            "prompt": prompt
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "content-type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            print("AIMLAPI raw response:", result)
            # Expect image URL in result['images'][0]['url']
            if "images" in result and result["images"]:
                img_info = result["images"][0]
                img_url = img_info.get("url")
                if img_url:
                    img_response = requests.get(img_url)
                    img_response.raise_for_status()
                    from io import BytesIO
                    image = Image.open(BytesIO(img_response.content))
                    image.save(output_path)
                else:
                    raise ValueError("No image URL found in AIMLAPI response")
            else:
                raise ValueError("No image returned from AIMLAPI")
        except Exception as e:
            print(f"AIMLAPI Image API error: {e}")
            # Fallback to dummy image
            img = Image.new('RGB', (512, 256), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((10, 10), "Startup Logo", fill=(255, 255, 0))
            img.save(output_path)
