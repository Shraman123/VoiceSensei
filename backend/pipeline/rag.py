"""
RAG Pipeline — FAISS + LangChain + sentence-transformers
Zero cost: embeddings run locally, no OpenAI key needed.
Model: all-MiniLM-L6-v2 (~90 MB, fast, accurate for exam Q&A)
"""
import os
import tempfile
from typing import Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader


_EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_embeddings: Optional[HuggingFaceEmbeddings] = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=_EMBED_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


class RAGPipeline:
    def __init__(self):
        self._vectorstore: Optional[FAISS] = None
        self.is_loaded: bool = False

    def load_pdf_bytes(self, pdf_bytes: bytes, filename: str = "upload.pdf") -> dict:
        """Ingest a PDF from raw bytes into the FAISS vectorstore."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        try:
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()
        finally:
            os.unlink(tmp_path)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=80,
            separators=["\n\n", "\n", ".", " "],
        )
        chunks = splitter.split_documents(pages)

        embeddings = _get_embeddings()

        if self._vectorstore is None:
            self._vectorstore = FAISS.from_documents(chunks, embeddings)
        else:
            new_store = FAISS.from_documents(chunks, embeddings)
            self._vectorstore.merge_from(new_store)

        self.is_loaded = True
        return {"chunks": len(chunks), "pages": len(pages)}

    def retrieve(self, query: str, k: int = 4) -> str:
        """Return top-k relevant chunks joined as a single string."""
        if not self.is_loaded or self._vectorstore is None:
            return ""
        docs = self._vectorstore.similarity_search(query, k=k)
        return "\n\n".join(d.page_content for d in docs)
