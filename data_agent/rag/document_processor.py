"""
Document processor for the RAG component.

This module handles loading, parsing, and preprocessing documents.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.config import config
from ..utils.logging import logger
from .chunking import chunk_text


class DocumentProcessor:
    """Document processor for loading and processing documents."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logger
    
    def process_file(
        self,
        file_path: Union[str, Path],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process a single file.
        
        Args:
            file_path: Path to the file
            metadata: Optional metadata to attach to the document
            
        Returns:
            List[Dict[str, Any]]: List of processed document chunks
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                return []
            
            # Get file type from extension
            file_type = file_path.suffix.lower()
            
            # Load and parse file
            if file_type in ['.txt', '.md', '.py', '.sql', '.yml', '.yaml', '.json']:
                return self._process_text_file(file_path, metadata)
            else:
                self.logger.warning(f"Unsupported file type: {file_type}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            return []
    
    def _process_text_file(
        self,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process a text file.
        
        Args:
            file_path: Path to the file
            metadata: Optional metadata to attach to the document
            
        Returns:
            List[Dict[str, Any]]: List of processed document chunks
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare base metadata
            base_metadata = {
                "source": str(file_path),
                "file_type": file_path.suffix.lower(),
                "file_name": file_path.name,
            }
            
            # Merge with provided metadata
            if metadata:
                base_metadata.update(metadata)
            
            # Chunk the content
            chunks = chunk_text(
                content,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            
            # Create document chunks with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = base_metadata.copy()
                chunk_metadata["chunk_index"] = i
                chunk_metadata["chunk_count"] = len(chunks)
                
                documents.append({
                    "text": chunk,
                    "metadata": chunk_metadata
                })
            
            self.logger.info(f"Processed {file_path} into {len(documents)} chunks")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error processing text file {file_path}: {str(e)}")
            return []
    
    def process_directory(
        self,
        directory_path: Union[str, Path],
        file_types: Optional[List[str]] = None,
        recursive: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process all supported files in a directory.
        
        Args:
            directory_path: Path to the directory
            file_types: List of file extensions to process
            recursive: Whether to process subdirectories
            metadata: Optional metadata to attach to documents
            
        Returns:
            List[Dict[str, Any]]: List of processed document chunks
        """
        try:
            directory_path = Path(directory_path)
            if not directory_path.exists() or not directory_path.is_dir():
                self.logger.error(f"Directory not found: {directory_path}")
                return []
            
            # Default supported file types
            if file_types is None:
                file_types = ['.txt', '.md', '.py', '.sql', '.yml', '.yaml', '.json']
            
            # Normalize file types
            file_types = [ft.lower() if ft.startswith('.') else f'.{ft.lower()}' for ft in file_types]
            
            # Find files
            all_documents = []
            
            if recursive:
                for root, _, files in os.walk(directory_path):
                    for file in files:
                        file_path = Path(root) / file
                        if file_path.suffix.lower() in file_types:
                            # Prepare file-specific metadata
                            file_metadata = metadata.copy() if metadata else {}
                            file_metadata["relative_path"] = str(file_path.relative_to(directory_path))
                            
                            # Process file
                            documents = self.process_file(file_path, file_metadata)
                            all_documents.extend(documents)
            else:
                for file_path in directory_path.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in file_types:
                        # Prepare file-specific metadata
                        file_metadata = metadata.copy() if metadata else {}
                        file_metadata["relative_path"] = file_path.name
                        
                        # Process file
                        documents = self.process_file(file_path, file_metadata)
                        all_documents.extend(documents)
            
            self.logger.info(f"Processed {len(all_documents)} document chunks from {directory_path}")
            return all_documents
            
        except Exception as e:
            self.logger.error(f"Error processing directory {directory_path}: {str(e)}")
            return []
