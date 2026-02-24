import os
import chromadb
from chromadb.config import Settings

class VectorMemory:
    """
    A persistent Vector Database for OpenJudge using ChromaDB.
    Replaces infinitely expanding text ledgers with semantic RAG retrieval.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorMemory, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Store the DB in the project root
        db_path = os.path.join(os.path.dirname(__file__), "openjudge_memory_db")
        self.client = chromadb.PersistentClient(path=db_path, settings=Settings(allow_reset=True))
        
        # Get or create the main memory collection
        self.collection = self.client.get_or_create_collection(name="openjudge_ledger")

    def store(self, action_id: str, document: str, metadata: dict = None):
        """
        Embeds and stores a factual event or code snippet into long-term memory.
        """
        try:
            self.collection.add(
                documents=[document],
                metadatas=[metadata or {"type": "general"}],
                ids=[action_id]
            )
            return True
        except Exception as e:
            return str(e)

    def query(self, search_text: str, n_results: int = 5):
        """
        Retrieves the most semantically relevant memories based on the search text.
        """
        try:
            results = self.collection.query(
                query_texts=[search_text],
                n_results=n_results
            )
            
            if not results["documents"] or not results["documents"][0]:
                return "No relevant memories found."
                
            formatted = []
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                formatted.append(f"[{meta.get('type', 'Unknown')}] {doc}")
                
            return "\n\n".join(formatted)
        except Exception as e:
            return f"Query failed: {str(e)}"

# Singleton Instance
memory_db = VectorMemory()
