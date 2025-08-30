import requests
import json
from typing import List, Dict, Any
import time

class LLMServer:
    def __init__(self, base_url: str = "http://localhost:1234", model_name: str = "itlwas/hermes-3-llama-3.1-8b"):
        """
        Initialize LLM Server connection for LM Studio
        
        Args:
            base_url: LM Studio server URL (default: http://localhost:1234)
            model_name: Model name to use (default: itlwas/hermes-3-llama-3.1-8b)
        """
        self.base_url = base_url
        self.model_name = model_name
        self.api_url = f"{base_url}/v1/chat/completions"
        
    def _make_request(self, prompt: str, system_prompt: str = None) -> str:
        """
        Make a request to the LM Studio API (OpenAI-compatible)
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated response text
        """
        # Prepare messages for chat completion
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            # Extract content from the first choice
            if result.get('choices') and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            else:
                return ""
            
        except requests.exceptions.RequestException as e:
            print(f"Error making LLM request: {e}")
            return ""
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            return ""
    
    def generate_summary(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate a summary from conversation history
        
        Args:
            conversation_history: List of conversation turns with 'user' and 'assistant' keys
            
        Returns:
            Summary of the conversation
        """
        if not conversation_history:
            return ""
            
        # Format conversation for the prompt
        conversation_text = ""
        for turn in conversation_history:
            if 'user' in turn:
                conversation_text += f"User: {turn['user']}\n"
            if 'assistant' in turn:
                conversation_text += f"Assistant: {turn['assistant']}\n"
        
        system_prompt = """You are an expert at analyzing conversations and extracting key insights. 
        Your task is to provide a concise summary of the conversation that captures the main points 
        about the target audience the user is looking for."""
        
        prompt = f"""Based on the following conversation, provide a clear and concise summary of what the user is looking for in their target audience:

{conversation_text}

Summary:"""
        
        return self._make_request(prompt, system_prompt)
    
    def extract_keywords(self, conversation_summary: str) -> List[str]:
        """
        Extract 10 relevant keywords from the conversation summary
        
        Args:
            conversation_summary: Summary of the conversation
            
        Returns:
            List of 10 keywords
        """
        if not conversation_summary:
            return []
            
        system_prompt = """You are an expert at keyword extraction for audience targeting. 
        Your task is to extract exactly 10 relevant keywords that would be useful for finding 
        the target audience described in the summary. Focus on terms that would help identify 
        people with similar interests, needs, or characteristics."""
        
        prompt = f"""Based on this summary, extract exactly 10 keywords that would be useful for finding the target audience:

Summary: {conversation_summary}

Provide exactly 10 keywords, one per line:
1. """
        
        response = self._make_request(prompt, system_prompt)
        
        # Parse the response to extract keywords
        keywords = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('Summary:') and not line.startswith('Keywords:'):
                # Remove numbering if present
                if '. ' in line:
                    keyword = line.split('. ', 1)[1]
                else:
                    keyword = line
                
                if keyword and len(keyword) > 2:  # Filter out very short keywords
                    keywords.append(keyword.lower())
        
        # Ensure we return exactly 10 keywords
        if len(keywords) > 10:
            keywords = keywords[:10]
        elif len(keywords) < 10:
            # Add some default keywords if we don't have enough
            default_keywords = [
                "target audience", "social media", "marketing", "business", "customers",
                "online presence", "digital marketing", "lead generation", "sales", "growth"
            ]
            for default in default_keywords:
                if len(keywords) < 10 and default not in keywords:
                    keywords.append(default)
        
        return keywords[:10]
    
    def process_conversation(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process conversation history to generate summary and extract keywords
        
        Args:
            conversation_history: List of conversation turns
            
        Returns:
            Dictionary containing summary and keywords
        """
        # Generate summary from conversation
        summary = self.generate_summary(conversation_history)
        
        # Extract keywords from summary
        keywords = self.extract_keywords(summary)
        
        return {
            "summary": summary,
            "keywords": keywords,
            "conversation_length": len(conversation_history)
        }
    
    def test_connection(self) -> bool:
        """
        Test if the LM Studio server is accessible
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Test with a simple request to check if server is running
            test_payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10,
                "stream": False
            }
            response = requests.post(self.api_url, json=test_payload, timeout=5)
            return response.status_code == 200
        except:
            return False

# Global LLM server instance
llm_server = LLMServer()

def get_llm_summary_and_keywords(conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Convenience function to get summary and keywords from conversation history
    
    Args:
        conversation_history: List of conversation turns
        
    Returns:
        Dictionary with summary and keywords
    """
    return llm_server.process_conversation(conversation_history)

def test_llm_connection() -> bool:
    """
    Test if LLM server is accessible
    
    Returns:
        True if accessible, False otherwise
    """
    return llm_server.test_connection()
