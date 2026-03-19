import json
from utils.mistral_client import call_mistral
from prompts.kg_prompt import KG_SYSTEM_PROMPT

def extract_kg(chunk):

    prompt = f"""
Extract entities and relationships from the text.

Text:
{chunk.page_content}
"""

    response = call_mistral(KG_SYSTEM_PROMPT, prompt)
    
    try:
        # Try direct JSON parsing first
        return json.loads(response)
    except json.JSONDecodeError:
        # Try extracting JSON from markdown code blocks
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON. Response: {response}")
            return {"entities": [], "relationships": []}