import os
import requests
import json

class PitchAgent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.api_url = "https://api.mistral.ai/v1/chat/completions"

    def _fix_incomplete_json(self, json_text):
        """
        Attempts to fix incomplete JSON by adding missing closing braces and quotes.
        Returns a valid JSON object or falls back to default structure.
        """
        try:
            # Count opening and closing braces
            open_braces = json_text.count('{')
            close_braces = json_text.count('}')
            
            # Add missing closing braces
            if open_braces > close_braces:
                json_text += '}' * (open_braces - close_braces)
            
            # Try to fix incomplete strings by adding closing quotes
            # Look for unclosed strings (quotes that don't have a matching closing quote)
            lines = json_text.split('\n')
            fixed_lines = []
            
            for line in lines:
                # If line ends with a quote but no closing quote, add one
                if line.strip().endswith('"') and not line.strip().endswith('",'):
                    line = line.rstrip() + '",'
                # If line ends with text but no quote, add quote and comma
                elif line.strip() and not line.strip().endswith(('"', ',', '{', '}', ']')):
                    line = line.rstrip() + '",'
                fixed_lines.append(line)
            
            json_text = '\n'.join(fixed_lines)
            
            # Try parsing the fixed JSON
            return json.loads(json_text)
            
        except Exception as e:
            print(f"Could not fix incomplete JSON: {e}")
            # Return a default structure with extracted content
            return self._extract_partial_data(json_text)
    
    def _extract_partial_data(self, text):
        """
        Extracts partial data from incomplete JSON text using regex patterns.
        """
        import re
        result = {
            "problem": f"Problem for AI in Stock Exchange",
            "solution": f"Solution for AI in Stock Exchange", 
            "market": "Market size and opportunity",
            "business_model": "Business model details"
        }
        
        # Try to extract problem
        problem_match = re.search(r'"problem"\s*:\s*"([^"]*)', text)
        if problem_match:
            result["problem"] = problem_match.group(1)
        
        # Try to extract solution
        solution_match = re.search(r'"solution"\s*:\s*"([^"]*)', text)
        if solution_match:
            result["solution"] = solution_match.group(1)
        
        # Try to extract market
        market_match = re.search(r'"market"\s*:\s*"([^"]*)', text)
        if market_match:
            result["market"] = market_match.group(1)
        
        # Try to extract business_model
        business_match = re.search(r'"business_model"\s*:\s*"([^"]*)', text)
        if business_match:
            result["business_model"] = business_match.group(1)
        
        return result

    def generate_pitch(self, topic):
        """
        Calls Mistral API to generate a startup pitch for the given topic.
        Returns: dict with keys: problem, solution, market, business_model
        """
        prompt = f"""Generate a startup pitch for the domain: {topic}. 

Return ONLY a valid JSON object with these exact keys:
- "problem": A brief description of the problem being solved
- "solution": A brief description of the proposed solution  
- "market": Market size and opportunity information
- "business_model": Business model and revenue strategy

Ensure the JSON is complete and properly formatted. Do not include any text outside the JSON object."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2048
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            try:
                result = response.json()
            except Exception as json_err:
                print("Mistral API raw response:", response.text)
                raise json_err
            pitch_text = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            import re
            # Extract JSON from Markdown code block if present
            match = re.search(r'```json\s*(\{.*?\})\s*```', pitch_text, re.DOTALL)
            if match:
                pitch_text_clean = match.group(1)
            else:
                # Try to find JSON object directly in the text
                json_match = re.search(r'(\{.*\})', pitch_text, re.DOTALL)
                if json_match:
                    pitch_text_clean = json_match.group(1)
                else:
                    pitch_text_clean = pitch_text
            try:
                pitch_json = json.loads(pitch_text_clean)
            except Exception as parse_err:
                print("Mistral API pitch text:", pitch_text_clean)
                # Try to fix incomplete JSON by adding missing closing braces
                pitch_json = self._fix_incomplete_json(pitch_text_clean)
            return pitch_json
        except Exception as e:
            print(f"Mistral API error: {e}")
            return {
                "problem": f"Problem for {topic}",
                "solution": f"Solution for {topic}",
                "market": "Market size and opportunity",
                "business_model": "Business model details"
            }


if __name__ == "__main__":
    agent = PitchAgent()
    result = agent.generate_pitch("AI in healthcare")
    print(json.dumps(result, indent=2))
