
from typing import List


def fixed_size_chunking(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """Split text into fixed-size chunks with overlap."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start += chunk_size - overlap

    return chunks



def recursive_chunking(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """Split text recursively while preserving natural boundaries."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    separators = ["\n\n", "\n", ". ", " ", ""]

    def split_recursively(value: str, separator_index: int) -> List[str]:
        if len(value) <= chunk_size:
            return [value] if value else []

        if separator_index >= len(separators):
            return [
                value[i:i + chunk_size]
                for i in range(0, len(value), chunk_size)
            ]

        separator = separators[separator_index]

        if not separator:
            return [
                value[i:i + chunk_size]
                for i in range(0, len(value), chunk_size)
            ]

        if separator not in value:
            return split_recursively(value, separator_index + 1)

        parts = value.split(separator)

        # Keep separators attached to their preceding text.
        pieces = [
            part + separator if i < len(parts) - 1 else part
            for i, part in enumerate(parts)
        ]

        result = []

        for piece in pieces:
            if not piece:
                continue

            if len(piece) > chunk_size:
                result.extend(
                    split_recursively(piece, separator_index + 1)
                )
            else:
                result.append(piece)

        return result

    segments = split_recursively(text, 0)

    chunks = []
    current = ""

    for segment in segments:
        candidate = current + segment

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current.strip())

        # Carry forward overlap without starting halfway through a word.
        if overlap > 0 and current:
            suffix = current[-overlap:]
            first_space = suffix.find(" ")

            if first_space != -1:
                suffix = suffix[first_space + 1:]
            else:
                suffix = ""

            while suffix and len(suffix) + len(segment) > chunk_size:
                suffix = suffix[1:]

            current = suffix + segment
        else:
            current = segment

        if len(current) > chunk_size:
            current = current[:chunk_size]

    if current.strip():
        chunks.append(current.strip())

    return chunks
