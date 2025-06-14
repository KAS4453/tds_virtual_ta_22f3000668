import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle
import os
import logging
from typing import List, Tuple
from app import app
from models import ScrapedContent

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize vector store with a lightweight sentence transformer model.
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        self.index = None
        self.documents = []
        self.index_file = 'vector_index.faiss'
        self.docs_file = 'documents.pkl'
        
    def load_or_create_index(self):
        """
        Load existing index or create new one from database content.
        """
        if os.path.exists(self.index_file) and os.path.exists(self.docs_file):
            try:
                self.index = faiss.read_index(self.index_file)
                with open(self.docs_file, 'rb') as f:
                    self.documents = pickle.load(f)
                logger.info("Loaded existing vector index")
                return
            except Exception as e:
                logger.error(f"Error loading index: {e}")
        
        # Create new index
        self.create_index()
    
    def create_index(self):
        """
        Create vector index from scraped content in database.
        """
        with app.app_context():
            contents = ScrapedContent.query.all()
            
            if not contents:
                logger.warning("No scraped content found in database")
                # Create empty index
                self.index = faiss.IndexFlatIP(self.dimension)
                self.documents = []
                return
            
            # Prepare documents
            texts = []
            self.documents = []
            
            for content in contents:
                # Combine title and content for better search
                text = f"{content.title}\n{content.content}"
                texts.append(text)
                
                self.documents.append({
                    'id': content.id,
                    'url': content.url,
                    'title': content.title,
                    'content': content.content,
                    'content_type': content.content_type,
                    'text': text
                })
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} documents")
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            embeddings = np.array(embeddings).astype('float32')
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)
            self.index.add(embeddings)
            
            # Save index and documents
            faiss.write_index(self.index, self.index_file)
            with open(self.docs_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            logger.info(f"Created vector index with {len(texts)} documents")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        """
        Search for similar documents using vector similarity.
        """
        if self.index is None or len(self.documents) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        query_embedding = np.array(query_embedding).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid index
                results.append((self.documents[idx], float(score)))
        
        return results
    
    def add_document(self, content: ScrapedContent):
        """
        Add a new document to the index.
        """
        if self.index is None:
            self.load_or_create_index()
        
        text = f"{content.title}\n{content.content}"
        embedding = self.model.encode([text], convert_to_tensor=False)
        embedding = np.array(embedding).astype('float32')
        faiss.normalize_L2(embedding)
        
        self.index.add(embedding)
        
        self.documents.append({
            'id': content.id,
            'url': content.url,
            'title': content.title,
            'content': content.content,
            'content_type': content.content_type,
            'text': text
        })
        
        # Save updated index
        faiss.write_index(self.index, self.index_file)
        with open(self.docs_file, 'wb') as f:
            pickle.dump(self.documents, f)


# Global vector store instance
vector_store = VectorStore()
