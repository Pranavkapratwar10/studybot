"""
Written Practice Question Generator using Groq API
"""
import json
import re
from typing import List, Dict, Optional
from llm.groq_client import GroqClient


class WrittenGenerator:
    """Generate written practice questions from text using Groq API"""
    
    def __init__(self):
        self.groq_client = GroqClient()
    
    def generate_questions(self, text: str, num_questions: int = 5, 
                          difficulty: str = "medium", marks_per_question: int = 5) -> List[Dict]:
        """
        Generate written practice questions from the given text
        
        Args:
            text: Source text to generate questions from
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            marks_per_question: Marks allocated for each question
        
        Returns:
            List of question dictionaries with question, marks, key_points
        """
        system_prompt = f"""You are an expert exam question generator. Generate {num_questions} written practice questions from the provided text.

CRITICAL RULES:
1. Return ONLY valid JSON, no other text
2. Questions should require detailed written answers
3. Difficulty: {difficulty}
4. Each question is worth {marks_per_question} marks
5. Include key points that should be covered in the answer

EXACT JSON FORMAT - DO NOT DEVIATE:
{{
  "questions": [
    {{
      "question": "Explain the main concept discussed in the text?",
      "marks": {marks_per_question},
      "key_points": [
        "Point 1 to cover",
        "Point 2 to cover",
        "Point 3 to cover"
      ],
      "difficulty": "{difficulty}"
    }}
  ]
}}

Generate {num_questions} questions following this EXACT format."""

        user_prompt = f"""Text to generate written questions from:\n\n{text[:4000]}\n\nGenerate {num_questions} written practice questions ({marks_per_question} marks each) in JSON format ONLY."""
        
        try:
            response = self.groq_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.5,
                max_tokens=3000
            )
            
            print(f"Written Questions Response (first 500 chars): {response[:500]}")
            
            # Parse JSON from response
            questions_data = self._parse_json_response(response)
            
            if questions_data and "questions" in questions_data:
                print(f"Successfully parsed {len(questions_data['questions'])} questions")
                return questions_data["questions"]
            else:
                print("No questions found in response")
                return self._fallback_parse(response, num_questions, marks_per_question, difficulty)
                
        except Exception as e:
            print(f"Error generating questions: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        try:
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
    
    def _fallback_parse(self, response: str, num_questions: int, 
                       marks: int, difficulty: str) -> List[Dict]:
        """Fallback parser to extract questions from unstructured response"""
        questions = []
        
        # Try to find question patterns
        question_pattern = r'(?:Question|Q)\s*\d+[:\.]?\s*([^\n]+(?:\n(?!(?:Question|Q\d)).*)*)'
        
        question_blocks = re.findall(question_pattern, response, re.IGNORECASE)
        
        for block in question_blocks[:num_questions]:
            try:
                question_text = block.strip()
                questions.append({
                    "question": question_text,
                    "marks": marks,
                    "key_points": ["Generated from document"],
                    "difficulty": difficulty
                })
            except:
                continue
        
        return questions
    
    def evaluate_answer(self, question: str, user_answer: str, 
                       key_points: List[str], total_marks: int) -> tuple:
        """
        Evaluate user's written answer using AI
        
        Returns:
            (score, feedback) tuple
        """
        system_prompt = """You are an expert examiner. Evaluate the student's answer objectively.

Scoring criteria:
- Relevance to the question
- Coverage of key points
- Clarity and coherence
- Depth of understanding
- Grammar and presentation

Return ONLY JSON in this format:
{
  "score": 7.5,
  "feedback": "Detailed feedback here"
}"""

        key_points_text = "\n".join([f"- {point}" for point in key_points])
        
        user_prompt = f"""Question ({total_marks} marks): {question}

Key Points to Cover:
{key_points_text}

Student's Answer:
{user_answer}

Evaluate this answer and give a score out of {total_marks} marks with detailed feedback."""

        try:
            response = self.groq_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse evaluation
            eval_data = self._parse_json_response(response)
            
            if eval_data and "score" in eval_data and "feedback" in eval_data:
                score = float(eval_data["score"])
                # Ensure score is within bounds
                score = max(0, min(score, total_marks))
                return score, eval_data["feedback"]
            else:
                # Fallback scoring
                return self._simple_evaluation(user_answer, key_points, total_marks)
                
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return self._simple_evaluation(user_answer, key_points, total_marks)
    
    def _simple_evaluation(self, answer: str, key_points: List[str], 
                          total_marks: int) -> tuple:
        """Simple fallback evaluation based on keywords"""
        if not answer or len(answer.strip()) < 50:
            return 0, "Answer is too short or empty."
        
        # Check for key point coverage
        answer_lower = answer.lower()
        covered_points = sum(
            1 for point in key_points 
            if any(word.lower() in answer_lower for word in point.split()[:3])
        )
        
        coverage_ratio = covered_points / len(key_points) if key_points else 0.5
        score = round(coverage_ratio * total_marks, 1)
        
        feedback = f"Your answer covers approximately {int(coverage_ratio * 100)}% of the key points. "
        if score >= total_marks * 0.8:
            feedback += "Excellent work!"
        elif score >= total_marks * 0.6:
            feedback += "Good effort, but could be more comprehensive."
        else:
            feedback += "Please review the key concepts and provide more detail."
        
        return score, feedback
    
    def validate_questions(self, questions: List[Dict]) -> List[Dict]:
        """Validate and clean question data"""
        valid_questions = []
        
        for q in questions:
            if self._is_valid_question(q):
                valid_questions.append(q)
        
        return valid_questions
    
    def _is_valid_question(self, question: Dict) -> bool:
        """Check if question has all required fields"""
        required_fields = ["question", "marks"]
        
        if not all(field in question for field in required_fields):
            return False
        
        if not isinstance(question["marks"], (int, float)):
            return False
        
        return True
