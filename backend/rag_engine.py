import os
import re
import math
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DocumentChunk:
    def __init__(self, chunk_id: str, document: str, page: int, text: str):
        self.chunk_id = chunk_id
        self.document = document
        self.page = page
        self.text = text.strip()

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "document": self.document,
            "page": self.page,
            "text": self.text
        }

class RAGEngine:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "..", "data")
        self.chunks: List[DocumentChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.documents_metadata = []
        self.load_and_index()

    def parse_pdf(self, file_path: str, doc_name: str) -> List[DocumentChunk]:
        chunks = []
        try:
            reader = PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                page_num = page_idx + 1
                raw_text = page.extract_text() or ""
                # Clean text
                cleaned = re.sub(r'\s+', ' ', raw_text).strip()
                if not cleaned:
                    continue
                
                # Split by sections or paragraphs
                sentences = re.split(r'(?<=[.!?])\s+', cleaned)
                current_chunk = []
                current_len = 0
                
                for s in sentences:
                    current_chunk.append(s)
                    current_len += len(s)
                    if current_len >= 320:
                        chunk_text = " ".join(current_chunk)
                        chunk_id = f"{doc_name}_p{page_num}_c{len(chunks)}"
                        chunks.append(DocumentChunk(chunk_id, doc_name, page_num, chunk_text))
                        # Keep overlapping tail
                        overlap = current_chunk[-1:] if len(current_chunk) > 1 else []
                        current_chunk = overlap
                        current_len = sum(len(x) for x in current_chunk)
                
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunk_id = f"{doc_name}_p{page_num}_c{len(chunks)}"
                    chunks.append(DocumentChunk(chunk_id, doc_name, page_num, chunk_text))
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        return chunks

    def load_and_index(self):
        self.chunks = []
        self.documents_metadata = []
        
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(self.data_dir, filename)
                    doc_chunks = self.parse_pdf(pdf_path, filename)
                    self.chunks.extend(doc_chunks)
                    pages_count = max([c.page for c in doc_chunks]) if doc_chunks else 0
                    self.documents_metadata.append({
                        "filename": filename,
                        "pages": pages_count,
                        "chunks_count": len(doc_chunks)
                    })

        # Build TF-IDF dense matrix with n-grams
        if self.chunks:
            corpus = [c.text for c in self.chunks]
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),
                stop_words='english',
                sublinear_tf=True
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            print(f"[RAG] Indexed {len(self.chunks)} chunks across {len(self.documents_metadata)} documents.")

    def add_uploaded_pdf(self, file_path: str, doc_name: str) -> Dict[str, Any]:
        new_chunks = self.parse_pdf(file_path, doc_name)
        if not new_chunks:
            return {"status": "error", "message": "Failed to extract text from PDF"}
        
        self.chunks.extend(new_chunks)
        pages_count = max([c.page for c in new_chunks])
        self.documents_metadata.append({
            "filename": doc_name,
            "pages": pages_count,
            "chunks_count": len(new_chunks)
        })
        
        # Re-index
        corpus = [c.text for c in self.chunks]
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words='english', sublinear_tf=True)
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        return {
            "status": "success",
            "document": doc_name,
            "pages": pages_count,
            "chunks": len(new_chunks)
        }

    def retrieve(self, query: str, top_k: int = 4, target_doc: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        # Entity/keyword boosting
        query_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9$%\-]+\b', query) if len(w) > 2]
        ranked_indices = np.argsort(scores)[::-1]
        
        results = []
        for idx in ranked_indices:
            chunk = self.chunks[idx]
            if target_doc and chunk.document != target_doc:
                continue

            base_score = float(scores[idx])
            # Keyword matching bonus
            chunk_lower = chunk.text.lower()
            keyword_matches = sum(1 for tok in query_tokens if tok in chunk_lower)
            boost = (keyword_matches / max(len(query_tokens), 1)) * 0.35
            final_score = min(base_score + boost, 1.0)
            
            if final_score > 0.05:
                results.append({
                    "chunk_id": chunk.chunk_id,
                    "document": chunk.document,
                    "page": chunk.page,
                    "text": chunk.text,
                    "confidence": round(final_score, 4)
                })
            
            if len(results) >= top_k:
                break
                
        return results

    def generate_answer(self, query: str, target_doc: Optional[str] = None) -> Dict[str, Any]:
        retrieved = self.retrieve(query, top_k=3, target_doc=target_doc)
        if not retrieved:
            return {
                "query": query,
                "answer": "I could not locate relevant clauses or policies in the uploaded insurance documents regarding this query.",
                "citations": [],
                "confidence": 0.0
            }

        top_chunk = retrieved[0]
        # Synthesize answer intelligently from highest confidence context
        primary_text = top_chunk["text"]
        
        # High quality extractive synthesis
        sentences = re.split(r'(?<=[.!?])\s+', primary_text)
        query_words = set(re.findall(r'\b[a-zA-Z0-9$%\-]+\b', query.lower()))
        
        best_sentences = []
        for s in sentences:
            s_words = set(re.findall(r'\b[a-zA-Z0-9$%\-]+\b', s.lower()))
            overlap = len(query_words.intersection(s_words))
            best_sentences.append((overlap, s))
            
        best_sentences.sort(key=lambda x: x[0], reverse=True)
        key_content = " ".join([s for _, s in best_sentences[:2]]) if best_sentences else primary_text[:250]
        
        # Construct professional insurance assistant answer
        answer = f"Based on {top_chunk['document']} (Page {top_chunk['page']}): {key_content.strip()}"
        
        citations = []
        for r in retrieved:
            citations.append({
                "document": r["document"],
                "page": r["page"],
                "confidence": r["confidence"],
                "snippet": r["text"][:220] + "..."
            })
            
        return {
            "query": query,
            "answer": answer,
            "citations": citations,
            "top_page": top_chunk["page"],
            "top_document": top_chunk["document"],
            "confidence": top_chunk["confidence"]
        }
