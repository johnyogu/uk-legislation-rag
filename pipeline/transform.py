from typing import List, Dict
import re

class LegislationTransformer:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize legislation text"""
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove page numbers and headers
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'© Crown Copyright \d+', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    @staticmethod
    def split_into_chunks(text: str, max_length: int = 512) -> List[Dict[str, str]]:
        """Split legislation text into manageable chunks"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para.split())
            
            if current_length + para_length > max_length and current_chunk:
                chunks.append({
                    "text": ' '.join(current_chunk),
                    "chunk_number": len(chunks) + 1
                })
                current_chunk = []
                current_length = 0
                
            current_chunk.append(para)
            current_length += para_length
            
        if current_chunk:
            chunks.append({
                "text": ' '.join(current_chunk),
                "chunk_number": len(chunks) + 1
            })
            
        return chunks