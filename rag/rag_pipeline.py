"""
RAG (Retrieval-Augmented Generation) pipeline
"""
from typing import List, Dict, Tuple, Optional
from rag.vector_store import VectorStore
from llm.groq_client import GroqClient
from llm.prompts import get_exam_mode_prompt, get_fallback_prompt, SYSTEM_PROMPT


class RAGPipeline:
    """Complete RAG pipeline for question answering"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_client = GroqClient()
        self.min_relevance_threshold = 0.7  # Adjust based on testing
    
    def query(self, user_id: int, question: str, exam_mode: str = "viva",
              top_k: int = 5) -> Tuple[str, List[str], bool]:
        """
        Process a query through the RAG pipeline
        
        Returns:
            answer: Generated answer string
            sources: List of source filenames
            used_context: Boolean indicating if context was found and used
        """
        # Step 1: Retrieve relevant chunks
        search_results = self.vector_store.search(user_id, question, top_k)
        
        # Check if we have relevant results
        if not search_results:
            # Fallback: Generate answer without context
            answer = self._generate_fallback_answer(question, exam_mode)
            return answer, [], False
        
        # Step 2: Prepare context from retrieved chunks
        context = self._prepare_context(search_results)
        sources = self._extract_sources(search_results)
        
        # Step 3: Generate answer using LLM
        answer = self._generate_answer(context, question, exam_mode)
        
        return answer, sources, True
    
    def _prepare_context(self, search_results: List[Dict]) -> str:
        """Prepare context string from search results"""
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            text = result['text']
            filename = result['metadata'].get('filename', 'Unknown')
            context_parts.append(f"[Source {i}: {filename}]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _extract_sources(self, search_results: List[Dict]) -> List[str]:
        """Extract unique source filenames"""
        sources = set()
        for result in search_results:
            filename = result['metadata'].get('filename', 'Unknown')
            sources.add(filename)
        return list(sources)
    
    def _generate_answer(self, context: str, question: str, exam_mode: str) -> str:
        """Generate answer using LLM with context"""
        system_prompt, user_prompt = get_exam_mode_prompt(exam_mode, context, question)
        answer = self.llm_client.generate_response(system_prompt, user_prompt)
        return answer
    
    def _generate_fallback_answer(self, question: str, exam_mode: str) -> str:
        """Generate answer without context (fallback)"""
        fallback_message = get_fallback_prompt(question, exam_mode)
        
        # Generate general answer
        system_prompt = SYSTEM_PROMPT
        user_prompt = f"{fallback_message}\n\nQuestion: {question}\n\nAnswer:"
        
        answer = self.llm_client.generate_response(system_prompt, user_prompt)
        
        # Prepend warning
        warning = "⚠️ **Note:** No relevant information found in your study materials. This is a general answer.\n\n"
        return warning + answer
    
    def add_documents_to_store(self, user_id: int, chunks: List[Dict]) -> int:
        """Add document chunks to vector store"""
        return self.vector_store.add_documents(user_id, chunks)
    
    def get_document_count(self, user_id: int) -> int:
        """Get number of chunks in user's collection"""
        return self.vector_store.get_document_count(user_id)
