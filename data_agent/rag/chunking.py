"""
Chunking module for text splitting.

This module provides various strategies for splitting text into chunks.
"""

import re
from typing import List, Optional


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separator: str = "\n",
) -> List[str]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: Input text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        separator: Separator to split on
        
    Returns:
        List[str]: List of text chunks
    """
    if not text:
        return []
    
    # Split text on separator
    splits = text.split(separator)
    
    # Handle case where separator isn't present
    if len(splits) == 1:
        return _chunk_text_by_chars(text, chunk_size, chunk_overlap)
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for split in splits:
        # Skip empty splits
        if not split:
            continue
        
        # Add separator back except for first item in chunk
        if current_chunk:
            split_with_sep = separator + split
        else:
            split_with_sep = split
        
        split_size = len(split_with_sep)
        
        # If adding this split would exceed chunk size, finalize current chunk
        if current_chunk and current_size + split_size > chunk_size:
            chunks.append(separator.join(current_chunk))
            
            # Use overlap: keep some of the last elements
            overlap_start = max(0, len(current_chunk) - _estimate_chunks_for_overlap(current_chunk, chunk_overlap, separator))
            current_chunk = current_chunk[overlap_start:]
            current_size = sum(len(separator) + len(s) for s in current_chunk) - len(separator)
        
        # Add current split to the chunk
        current_chunk.append(split)
        current_size += split_size
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(separator.join(current_chunk))
    
    return chunks


def _chunk_text_by_chars(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[str]:
    """
    Split text into chunks by characters.
    
    Args:
        text: Input text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    if not text:
        return []
    
    # If text is shorter than chunk size, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    # Calculate the stride (chunk size - overlap)
    stride = chunk_size - chunk_overlap
    
    # Ensure stride is positive
    if stride <= 0:
        stride = chunk_size // 2
    
    # Split text into chunks
    chunks = []
    for i in range(0, len(text), stride):
        # Ensure we don't exceed text length
        chunk_end = min(i + chunk_size, len(text))
        chunks.append(text[i:chunk_end])
        
        # If we've reached the end of the text, we're done
        if chunk_end == len(text):
            break
    
    return chunks


def _estimate_chunks_for_overlap(
    chunks: List[str],
    overlap_size: int,
    separator: str,
) -> int:
    """
    Estimate how many chunks to keep to meet the overlap size.
    
    Args:
        chunks: Current chunks
        overlap_size: Desired overlap size
        separator: Separator between chunks
        
    Returns:
        int: Number of chunks to keep
    """
    if not chunks:
        return 0
    
    # Count characters from the end
    total_size = 0
    for i in range(len(chunks) - 1, -1, -1):
        # Add separator length except for the first chunk we consider
        if i < len(chunks) - 1:
            total_size += len(separator)
        
        total_size += len(chunks[i])
        
        if total_size >= overlap_size:
            return len(chunks) - i
    
    # If we couldn't meet the overlap, keep all chunks
    return len(chunks)


def chunk_by_tokens(
    text: str,
    max_tokens: int = 500,
    overlap_tokens: int = 100,
) -> List[str]:
    """
    Split text into chunks by estimated token count.
    
    This is a simple approximation - actual token count depends on the tokenizer.
    
    Args:
        text: Input text to split
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Token overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    # Rough approximation: 1 token ~= 4 characters for English text
    return chunk_text(
        text,
        chunk_size=max_tokens * 4,
        chunk_overlap=overlap_tokens * 4,
    )


def chunk_markdown(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[str]:
    """
    Split markdown text into chunks, trying to preserve structure.
    
    Args:
        text: Markdown text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List[str]: List of markdown chunks
    """
    # Split on headers (## Header)
    header_pattern = r"(^|\n)(#{1,6}\s.*?)(\n|$)"
    splits = re.split(header_pattern, text)
    
    chunks = []
    current_chunk = ""
    
    for i in range(0, len(splits), 4):
        # Get the header and content (handling end of list)
        if i < len(splits):
            prefix = splits[i]
        else:
            prefix = ""
            
        if i + 1 < len(splits):
            header = splits[i + 1]
        else:
            header = ""
            
        if i + 2 < len(splits):
            content = splits[i + 2]
        else:
            content = ""
            
        if i + 3 < len(splits):
            suffix = splits[i + 3]
        else:
            suffix = ""
        
        # Combine the parts
        section = prefix + header + content + suffix
        
        # If adding this section exceeds chunk size, finalize current chunk
        if current_chunk and len(current_chunk) + len(section) > chunk_size:
            chunks.append(current_chunk)
            
            # Start a new chunk with overlap
            overlap_size = min(len(current_chunk), chunk_overlap)
            current_chunk = current_chunk[-overlap_size:] if overlap_size > 0 else ""
        
        current_chunk += section
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks
