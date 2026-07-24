"""
MCQ Generator using Groq API
"""
import json
import re
from typing import List, Dict, Optional
from llm.groq_client import GroqClient


class MCQGenerator:
    """Generate MCQs from text using Groq API"""
    
    def __init__(self):
        self.groq_client = GroqClient()
    
    def generate_mcqs(self, text: str, num_questions: int = 10, 
                     difficulty: str = "medium") -> List[Dict]:
        """
        Generate MCQs from the given text
        
        Args:
            text: Source text to generate MCQs from
            num_questions: Number of MCQs to generate
            difficulty: Difficulty level (easy, medium, hard)
        
        Returns:
            List of MCQ dictionaries with question, options, correct_answer
        """
        system_prompt = f"""You are an expert MCQ generator. Generate {num_questions} multiple choice questions from the provided text.

Requirements:
- Difficulty level: {difficulty}
- Each question should have 4 options (A, B, C, D)
- Mark the correct answer
- Questions should test understanding, not just memorization
- Cover different topics from the text

Return ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": {{
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
      }},
      "correct_answer": "A",
      "explanation": "Brief explanation of why this is correct"
    }}
  ]
}}"""

        user_prompt = f"""Generate {num_questions} MCQs from this text:\n\n{text[:4000]}"""
        
        try:
            response = self.groq_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract JSON from response
            mcqs_data = self._parse_json_response(response)
            
            if mcqs_data and "questions" in mcqs_data:
                return mcqs_data["questions"]
            else:
                return []
                
        except Exception as e:
            print(f"Error generating MCQs: {e}")
            return []
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        try:
            # Try direct JSON parse
            return json.loads(response)
        except:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # Try to find JSON object in text
            json_match = re.search(r'\{.*"questions".*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass
            
            return None
    
    def validate_mcqs(self, mcqs: List[Dict]) -> List[Dict]:
        """Validate and clean MCQ data"""
        valid_mcqs = []
        
        for mcq in mcqs:
            if self._is_valid_mcq(mcq):
                valid_mcqs.append(mcq)
        
        return valid_mcqs
    
    def _is_valid_mcq(self, mcq: Dict) -> bool:
        """Check if MCQ has all required fields"""
        required_fields = ["question", "options", "correct_answer"]
        
        if not all(field in mcq for field in required_fields):
            return False
        
        if not isinstance(mcq["options"], dict):
            return False
        
        if len(mcq["options"]) != 4:
            return False
        
        if mcq["correct_answer"] not in mcq["options"]:
            return False
        
        return True
