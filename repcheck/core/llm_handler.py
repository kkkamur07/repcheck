import requests
from typing import Optional

class OllamaHandler:
    """Simple OLLAMA handler for error analysis."""
    
    def __init__(self, model: str = "granite3.3:2b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.api_url = f"{base_url}/api/generate"
    
    def is_available(self) -> bool:
        """Check if OLLAMA is running."""
        try:
            response = requests.get(f"{self.api_url.replace('/api/generate', '/api/tags')}", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def ask(self, prompt: str) -> Optional[str]:
        """Send prompt to OLLAMA and get response."""
        if not self.is_available():
            return None
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return None
            
        except:
            return None
    
    def analyze_error(self, script_path: str, error: str, language: str = "R") -> Optional[str]:
        """Analyze script error for any programming language."""
        prompt = f"""You are a {language} programming expert. Analyze this error and explain the likely cause and how to fix it.

Script: {script_path}
Error: {error}

Keep response under 100 words."""
        
        return self.ask(prompt)