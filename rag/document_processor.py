"""
Document processing module for parsing and chunking documents
"""
import os
from pathlib import Path
from typing import List, Dict
import pypdf
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


class DocumentProcessor:
    """Handles document parsing and text extraction"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading TXT file: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from any supported file format"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            return self.extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with metadata
        Returns list of dicts with 'text' and 'metadata' keys
        """
        if not text or len(text.strip()) == 0:
            return []
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create chunk documents with metadata
        chunk_docs = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata['chunk_id'] = i
            chunk_metadata['chunk_count'] = len(chunks)
            
            chunk_docs.append({
                'text': chunk,
                'metadata': chunk_metadata
            })
        
        return chunk_docs
    
    def process_document(self, file_path: str, filename: str, user_id: int) -> List[Dict]:
        """
        Process a document: extract text and create chunks
        Returns list of chunk documents
        """
        # Extract text
        text = self.extract_text(file_path)
        
        if not text:
            raise ValueError(f"No text could be extracted from {filename}")
        
        # Create metadata
        metadata = {
            'filename': filename,
            'user_id': user_id,
            'file_path': file_path,
            'file_type': Path(file_path).suffix
        }
        
        # Chunk text
        chunks = self.chunk_text(text, metadata)
        
        return chunks
    
    def process_multiple_documents(self, file_paths: List[str], filenames: List[str], 
                                   user_id: int) -> List[Dict]:
        """Process multiple documents and return all chunks"""
        all_chunks = []
        
        for file_path, filename in zip(file_paths, filenames):
            try:
                chunks = self.process_document(file_path, filename, user_id)
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        return all_chunks
