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
        system_prompt = f"""You are an expert MCQ generator. You MUST generate {num_questions} multiple choice questions from the provided text.

CRITICAL RULES:
1. Return ONLY valid JSON, no other text
2. Each question MUST have exactly 4 options (A, B, C, D)
3. One correct answer (A, B, C, or D)
4. Difficulty: {difficulty}

EXACT JSON FORMAT - DO NOT DEVIATE:
{{
  "questions": [
    {{
      "question": "What is the main topic?",
      "options": {{
        "A": "Option one",
        "B": "Option two",
        "C": "Option three",
        "D": "Option four"
      }},
      "correct_answer": "A",
      "explanation": "Why A is correct"
    }}
  ]
}}

Generate {num_questions} questions following this EXACT format."""

        user_prompt = f"""Text to generate MCQs from:\n\n{text[:4000]}\n\nGenerate {num_questions} MCQs in JSON format ONLY."""
        
        try:
            response = self.groq_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.5,  # Lower temperature for more structured output
                max_tokens=3000   # Increased token limit
            )
            
            print(f"MCQ Response (first 500 chars): {response[:500]}")  # Debug
            
            # Extract JSON from response
            mcqs_data = self._parse_json_response(response)
            
            if mcqs_data and "questions" in mcqs_data:
                print(f"Successfully parsed {len(mcqs_data['questions'])} questions")
                return mcqs_data["questions"]
            else:
                print("No questions found in response")
                # Try alternative parsing
                return self._fallback_parse(response, num_questions)
                
        except Exception as e:
            print(f"Error generating MCQs: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        try:
            # Try direct JSON parse
            return json.loads(response)
        except:
            pass
        
        # Try to extract JSON from markdown code blocks
        patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'\{.*?"questions".*?\].*?\}',
        ]
        
        for pattern in patterns:
            json_match = re.search(pattern, response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1) if '```' in pattern else json_match.group(0)
                    return json.loads(json_str)
                except:
                    continue
        
        return None
    
    def _fallback_parse(self, response: str, num_questions: int) -> List[Dict]:
        """Fallback parser to extract questions from unstructured response"""
        questions = []
        
        # Try to find question patterns
        question_pattern = r'(?:Question|Q)\s*\d+[:\.]?\s*([^\n]+(?:\n(?!(?:A\.|B\.|C\.|D\.|Question|Q\d)).*)*)'
        options_pattern = r'([A-D])\.\s*([^\n]+)'
        correct_pattern = r'(?:Correct|Answer)[:\s]*([A-D])'
        
        question_blocks = re.findall(question_pattern, response, re.IGNORECASE)
        
        for block in question_blocks[:num_questions]:
            try:
                # Extract question text
                question_text = block.strip()
                
                # Find options
                options_matches = re.findall(options_pattern, question_text)
                if len(options_matches) >= 4:
                    options = {opt[0]: opt[1].strip() for opt in options_matches[:4]}
                    
                    # Find correct answer
                    correct_match = re.search(correct_pattern, question_text, re.IGNORECASE)
                    correct_answer = correct_match.group(1) if correct_match else "A"
                    
                    # Clean question text (remove options)
                    question_only = re.split(r'\n[A-D]\.', question_text)[0].strip()
                    
                    questions.append({
                        "question": question_only,
                        "options": options,
                        "correct_answer": correct_answer,
                        "explanation": "Generated from document"
                    })
            except:
                continue
        
        return questions
    
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
