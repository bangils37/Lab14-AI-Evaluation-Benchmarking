import os
import glob
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from pathlib import Path

class DocumentRetriever:
    """
    RAG Retriever: Tải tài liệu, chunk theo sections giống synthetic_gen.py, embedding, và similarity search.
    """
    
    def __init__(self, data_path: str = "data/heart_health", model_name: str = "all-MiniLM-L6-v2"):
        self.data_path = data_path
        self.model = SentenceTransformer(model_name)
        
        # Storage
        self.chunks: List[str] = []
        self.chunk_embeddings: np.ndarray = None
        self.chunk_metadata: List[Dict] = []
        
        # Load documents
        self._load_and_chunk_documents()
        self._create_embeddings()
    
    def _strip_front_matter(self, text: str) -> str:
        """Loại bỏ YAML front matter ở đầu file markdown nếu có."""
        if not text.startswith("---"):
            return text
        parts = text.split("---", 2)
        if len(parts) < 3:
            return text
        return parts[2].strip()
    
    def _split_markdown_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Tách nội dung markdown thành các section dựa trên heading.
        Giống như synthetic_gen.py để đảm bảo consistency.
        """
        lines = text.splitlines()
        document_title = ""
        sections: List[Dict[str, str]] = []
        current_heading = ""
        current_lines: List[str] = []

        def flush_section():
            body = "\n".join(line.rstrip() for line in current_lines).strip()
            if not body:
                return

            title_parts = []
            if document_title:
                title_parts.append(f"Tiêu đề tài liệu: {document_title}")
            if current_heading:
                title_parts.append(f"Mục: {current_heading}")

            section_text = "\n".join(title_parts + [body]).strip()
            sections.append(
                {
                    "section_title": current_heading or document_title or "untitled_section",
                    "text": section_text,
                }
            )

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                current_lines.append("")
                continue

            if line.startswith("# "):
                if not document_title:
                    document_title = line[2:].strip()
                    continue

            if re.match(r"^##+\s+", line):
                flush_section()
                current_heading = re.sub(r"^##+\s+", "", line).strip()
                current_lines = []
                continue

            current_lines.append(raw_line)

        flush_section()

        if not sections:
            fallback_text = text.strip()
            if fallback_text:
                sections.append(
                    {
                        "section_title": document_title or "full_document",
                        "text": fallback_text,
                    }
                )

        return sections
    
    def _load_and_chunk_documents(self):
        """
        Tải tất cả .md files từ data_path, chia thành sections giống synthetic_gen.py.
        """
        print(f"📂 Loading documents from {self.data_path}...")
        
        root = Path(self.data_path)
        md_files = sorted(root.glob("*.md"))
        
        if not md_files:
            print(f"⚠️  No markdown files found in {self.data_path}")
            return
        
        for file_path in md_files:
            content = file_path.read_text(encoding="utf-8")
            content = self._strip_front_matter(content)
            sections = self._split_markdown_sections(content)
            
            print(f"   📄 {file_path.name} → {len(sections)} sections")
            
            for section_index, section in enumerate(sections):
                # Create chunk_id matching golden_set format: heart_health_01_section_0
                chunk_id = f"{file_path.stem}_section_{section_index}"
                
                self.chunks.append(section["text"])
                self.chunk_metadata.append({
                    "chunk_id": chunk_id,
                    "source": file_path.name,
                    "section_title": section["section_title"],
                    "section_index": section_index
                })
        
        print(f"✅ Loaded {len(md_files)} files, created {len(self.chunks)} sections\n")
    
    def _create_embeddings(self):
        """
        Tạo embeddings cho tất cả chunks.
        """
        if not self.chunks:
            print("⚠️  No chunks to embed")
            return
            
        print(f"🔄 Creating embeddings for {len(self.chunks)} chunks...")
        self.chunk_embeddings = self.model.encode(self.chunks, show_progress_bar=True)
        print(f"✅ Embeddings created (shape: {self.chunk_embeddings.shape})\n")
    
    def retrieve(self, query: str, top_k: int = 3) -> Tuple[List[str], List[str], List[float]]:
        """
        Retrieve top_k most similar chunks cho query.
        
        Returns:
            - retrieved_texts: Danh sách text của chunks
            - chunk_ids: Danh sách chunk IDs (matching golden_set format)
            - scores: Similarity scores
        """
        if not self.chunks or self.chunk_embeddings is None:
            return [], [], []
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate similarity
        similarities = cosine_similarity([query_embedding], self.chunk_embeddings)[0]
        
        # Get top_k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        retrieved_texts = [self.chunks[i] for i in top_indices]
        chunk_ids = [self.chunk_metadata[i]["chunk_id"] for i in top_indices]
        scores = [float(similarities[i]) for i in top_indices]
        
        return retrieved_texts, chunk_ids, scores
    
    def get_chunk_by_id(self, chunk_id: str) -> str:
        """Get chunk text by ID."""
        for i, metadata in enumerate(self.chunk_metadata):
            if metadata["chunk_id"] == chunk_id:
                return self.chunks[i]
        return ""


# Global retriever instance
_retriever_instance = None

def get_retriever(data_path: str = "data/heart_health") -> DocumentRetriever:
    """Get or create retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = DocumentRetriever(data_path=data_path)
    return _retriever_instance
