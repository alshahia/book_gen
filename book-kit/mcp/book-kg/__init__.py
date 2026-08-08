"""Book knowledge graph package."""
from .indexer import index_book
from .query import contradicts, motifs_in_chapter, references, trace_path

__all__ = ["index_book", "trace_path", "motifs_in_chapter", "contradicts", "references"]
