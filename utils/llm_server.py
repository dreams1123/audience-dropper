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
            conversation_history: List of conversation turns with 'role' and 'content' keys
            
        Returns:
            Summary of the conversation
        """
        if not conversation_history:
            return ""
            
        # Format conversation for the prompt
        conversation_text = ""
        for turn in conversation_history:
            role = turn.get('role', '')
            content = turn.get('content', '')
            if role == 'user':
                conversation_text += f"User: {content}\n"
            elif role == 'assistant':
                conversation_text += f"Assistant: {content}\n"
        
        system_prompt = """You are an expert at analyzing conversations and extracting key insights for audience targeting. 
        Your task is to provide a concise summary that captures:
        1. Who the user is looking for (target audience)
        2. What specific problems or situations their target audience faces
        3. What exact phrases and language patterns people use when talking about these problems
        4. What product/service the user offers
        
        Keep the summary brief and focused on the most important natural language patterns people use when discussing their problems online."""
        
        prompt = f"""Based on the following conversation between a user and an AI assistant about audience targeting, provide a concise summary:

{conversation_text}

Provide a brief summary that includes:
- Target audience description
- Key phrases and language patterns people use
- What the user offers
- Main problems people face

Keep it short and focused on natural, conversational language people use on social media.

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
            
        system_prompt = """You are an expert at extracting natural language phrases and keywords that people actually use when talking about their problems and needs on social media. 
        
        Your task is to extract exactly 10 phrases and keywords that match how people naturally express themselves when:
        1. Talking about their problems or challenges
        2. Asking for help or recommendations
        3. Discussing their situation with family/friends
        4. Seeking solutions or services
        5. Sharing their experiences
        
        Focus on natural, conversational language that people would actually type in social media posts, comments, or searches."""
        
        prompt = f"""Based on this summary, extract exactly 10 natural language phrases and keywords that people would actually use when talking about this topic on social media:

Summary: {conversation_summary}

Provide exactly 10 phrases/keywords, one per line. Focus on:
- Exact phrases people would say (e.g., "I have breast cancer", "my wife has breast cancer")
- Questions people ask (e.g., "does anyone know a good doctor for...")
- Natural expressions (e.g., "just diagnosed with...", "fighting...")
- Family references (e.g., "my mom has...", "my sister has...")
- Help-seeking language (e.g., "looking for treatment", "need support for...")

Make these sound like real conversations people have online. Use quotes for exact phrases when appropriate.

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
                    # Clean up the keyword
                    keyword = keyword.lower().strip()
                    # Remove common prefixes/suffixes
                    keyword = keyword.replace('keyword:', '').replace('term:', '').strip()
                    if keyword and keyword not in keywords:
                        keywords.append(keyword)
        
        # Ensure we return exactly 10 keywords
        if len(keywords) > 10:
            keywords = keywords[:10]
        elif len(keywords) < 10:
            # Add some default keywords if we don't have enough
            default_keywords = [
                "I need help with", "looking for solutions", "my business is struggling",
                "need support", "anyone know a good", "recommendations for",
                "just started", "trying to find", "need advice", "help me with"
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
    
    def generate_phrases_from_keywords(self, keywords: List[str]) -> List[str]:
        """
        Generate exactly 10 natural phrases from keywords that people would use on social media
        
        Args:
            keywords: List of keywords to generate phrases from
            
        Returns:
            List of exactly 10 phrases
        """
        if not keywords:
            return []
            
        system_prompt = """You are an expert at creating natural language phrases that people actually use when talking about their problems and needs on social media platforms like Facebook, Twitter, Reddit, and GoFundMe.

Your task is to generate exactly 10 natural, conversational phrases that people would actually type when discussing the topics represented by the given keywords."""
        
        keywords_text = ", ".join(keywords[:5])  # Use first 5 keywords to avoid too long prompt
        
        prompt = f"""Based on these keywords: {keywords_text}

Generate exactly 10 natural phrases that people would actually use when posting on social media about these topics. Make them sound like real conversations people have online.

Focus on:
- How people naturally express their problems or needs
- Questions they would ask for help or recommendations
- Personal statements about their situation
- Family-related references when appropriate
- Emotional, human language (not clinical or formal)

Examples of natural phrase styles:
- "I need help with..."
- "My mom was just diagnosed with..."  
- "Does anyone know a good..."
- "Looking for support for..."
- "Just found out I have..."

Generate exactly 10 phrases, one per line, numbered 1-10:

1. """
        
        response = self._make_request(prompt, system_prompt)
        
        # Parse the response to extract phrases
        phrases = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('Based on') and not line.startswith('Here are'):
                # Remove numbering if present
                if '. ' in line and line[0].isdigit():
                    phrase = line.split('. ', 1)[1] if len(line.split('. ', 1)) > 1 else line
                else:
                    phrase = line
                
                if phrase and len(phrase) > 5:  # Filter out very short phrases
                    # Clean up the phrase
                    phrase = phrase.strip().strip('"').strip("'")
                    if phrase and phrase not in phrases:
                        phrases.append(phrase)
        
        # Ensure we return exactly 10 phrases
        if len(phrases) > 10:
            phrases = phrases[:10]
        elif len(phrases) < 10:
            # Add default phrases if we don't have enough
            default_phrases = [
                "I need help with this situation",
                "Looking for advice and support", 
                "Anyone been through something similar?",
                "My family member is struggling with this",
                "Seeking recommendations from the community",
                "Does anyone know where to get help?",
                "Just diagnosed and need guidance",
                "Support group recommendations needed",
                "Looking for treatment options",
                "Anyone have experience with this?"
            ]
            for default in default_phrases:
                if len(phrases) < 10 and default not in phrases:
                    phrases.append(default)
        
        return phrases[:10]
    
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

def get_llm_phrases_from_keywords(keywords: List[str]) -> List[str]:
    """
    Generate 10 phrases from keywords using LLM
    
    Args:
        keywords: List of keywords to generate phrases from
        
    Returns:
        List of 10 phrases
    """
    return llm_server.generate_phrases_from_keywords(keywords)

def test_llm_connection() -> bool:
    """
    Test if LLM server is accessible
    
    Returns:
        True if accessible, False otherwise
    """
    return llm_server.test_connection()
