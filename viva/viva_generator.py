"""
Viva Question Generator - Generate and evaluate viva-voce questions
"""
import json
import re
from typing import List, Dict, Tuple
from llm.groq_client import GroqClient


class VivaGenerator:
    """Generate viva questions and evaluate answers"""
    
    def __init__(self):
        self.groq_client = GroqClient()
    
    def generate_viva_questions(self, text: str, num_questions: int = 10, 
                               difficulty: str = "medium") -> List[Dict]:
        """
        Generate viva questions from text
        
        Args:
            text: Document text
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy/medium/hard)
        
        Returns:
            List of question dictionaries
        """
        # Truncate text if too long
        max_chars = 4000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        difficulty_instructions = {
            "easy": "Generate basic recall and understanding questions.",
            "medium": "Generate analytical and application-based questions.",
            "hard": "Generate complex evaluation and synthesis questions that require deep understanding."
        }
        
        prompt = f"""Based on the following text, generate {num_questions} viva-voce (oral exam) questions.

{difficulty_instructions.get(difficulty, difficulty_instructions['medium'])}

Text:
{text}

Generate questions in the following JSON format:
[
    {{
        "question": "Question text here?",
        "key_points": ["Point 1", "Point 2", "Point 3"]
    }}
]

Requirements:
1. Questions should be open-ended and require detailed answers
2. Include 3-5 key points that a good answer should cover
3. Questions should test understanding, not just recall
4. Make questions suitable for oral examination
5. Vary the depth and focus of questions

Generate ONLY the JSON array, no other text."""

        try:
            response = self.groq_client.generate_response(prompt, temperature=0.7)
            
            # Extract JSON from response
            questions = self._extract_json_from_response(response)
            
            if not questions:
                return []
            
            # Limit to requested number
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Error generating viva questions: {e}")
            return []
    
    def evaluate_answer(self, question: str, user_answer: str, 
                       expected_points: List[str]) -> Tuple[int, str]:
        """
        Evaluate user's answer using AI
        
        Args:
            question: The viva question
            user_answer: User's answer
            expected_points: Key points that should be covered
        
        Returns:
            Tuple of (score out of 10, feedback text)
        """
        if not user_answer or len(user_answer.strip()) < 20:
            return 0, "Answer is too short or empty. Please provide a detailed response."
        
        expected_points_text = "\n".join([f"- {point}" for point in expected_points])
        
        prompt = f"""You are evaluating a student's viva-voce answer. Rate the answer on a scale of 0-10.

Question:
{question}

Key Points to Cover:
{expected_points_text}

Student's Answer:
{user_answer}

Evaluation Criteria:
1. Accuracy and correctness (0-3 points)
2. Completeness - covering key points (0-3 points)
3. Clarity and explanation (0-2 points)
4. Understanding and depth (0-2 points)

Provide your evaluation in this JSON format:
{{
    "score": <number 0-10>,
    "feedback": "<constructive feedback explaining the score, what was good, and what could be improved>"
}}

Be fair but constructive. Focus on helping the student improve.

Generate ONLY the JSON object, no other text."""

        try:
            response = self.groq_client.generate_response(prompt, temperature=0.3)
            
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                score = int(evaluation.get('score', 5))
                feedback = evaluation.get('feedback', 'Good effort!')
                
                # Ensure score is in valid range
                score = max(0, min(10, score))
                
                return score, feedback
            else:
                # Fallback scoring based on length and keyword matching
                return self._simple_evaluation(user_answer, expected_points)
                
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            # Fallback to simple evaluation
            return self._simple_evaluation(user_answer, expected_points)
    
    def _simple_evaluation(self, answer: str, expected_points: List[str]) -> Tuple[int, str]:
        """Simple fallback evaluation based on keywords and length"""
        answer_lower = answer.lower()
        
        # Check for key point coverage
        points_covered = 0
        for point in expected_points:
            keywords = point.lower().split()
            if any(keyword in answer_lower for keyword in keywords if len(keyword) > 3):
                points_covered += 1
        
        # Calculate score
        if not expected_points:
            coverage_score = 5
        else:
            coverage_score = int((points_covered / len(expected_points)) * 6)
        
        # Length-based score
        word_count = len(answer.split())
        if word_count >= 100:
            length_score = 4
        elif word_count >= 50:
            length_score = 3
        elif word_count >= 30:
            length_score = 2
        else:
            length_score = 1
        
        total_score = coverage_score + length_score
        total_score = max(0, min(10, total_score))
        
        feedback = f"Your answer covers {points_covered}/{len(expected_points)} key points. "
        if total_score >= 8:
            feedback += "Excellent response with good detail!"
        elif total_score >= 6:
            feedback += "Good answer, but could include more key points."
        else:
            feedback += "Try to cover more key concepts and provide more detail."
        
        return total_score, feedback
    
    def _extract_json_from_response(self, response: str) -> List[Dict]:
        """Extract JSON array from LLM response"""
        try:
            # Try to find JSON array in response
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                return questions
            
            # Try parsing entire response
            questions = json.loads(response)
            return questions
            
        except json.JSONDecodeError:
            # Try to extract question-like structures manually
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> List[Dict]:
        """Fallback parser if JSON parsing fails"""
        questions = []
        
        # Try to find questions (lines ending with ?)
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if '?' in line and len(line) > 20:
                # Extract question
                question_match = re.search(r'["\']?([^"\']+\?)["\']?', line)
                if question_match:
                    question_text = question_match.group(1).strip()
                    questions.append({
                        'question': question_text,
                        'key_points': []
                    })
        
        return questions[:20]  # Limit to reasonable number
