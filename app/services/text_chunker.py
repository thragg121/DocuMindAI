from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextChunk:
    index: int
    content: str
    character_count: int


class TextChunkingError(Exception):
    """Raised when document text cannot be split into chunks."""


class TextChunker:
    DEFAULT_CHUNK_SIZE = 1200
    DEFAULT_CHUNK_OVERLAP = 200

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero.")

        if chunk_overlap < 0:
            raise ValueError("Chunk overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size.")

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[TextChunk]:
        normalized_text = self._normalize_text(text)

        if not normalized_text:
            raise TextChunkingError("Cannot split an empty document.")

        raw_chunks = self._split_into_raw_chunks(normalized_text)

        if not raw_chunks:
            raise TextChunkingError("No text chunks were created.")

        return [
            TextChunk(
                index=index,
                content=content,
                character_count=len(content),
            )
            for index, content in enumerate(raw_chunks)
        ]

    def _split_into_raw_chunks(self, text: str) -> list[str]:
        chunks: list[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            target_end = min(
                start + self._chunk_size,
                text_length,
            )

            end = self._find_best_split_position(
                text=text,
                start=start,
                target_end=target_end,
            )

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            next_start = end - self._chunk_overlap

            if next_start <= start:
                next_start = end

            start = next_start

        return chunks

    def _find_best_split_position(
        self,
        text: str,
        start: int,
        target_end: int,
    ) -> int:
        if target_end >= len(text):
            return len(text)

        minimum_split_position = start + int(self._chunk_size * 0.6)

        separators = (
            "\n\n",
            "\n",
            ". ",
            "! ",
            "? ",
            "; ",
            ", ",
            " ",
        )

        for separator in separators:
            split_position = text.rfind(
                separator,
                minimum_split_position,
                target_end,
            )

            if split_position == -1:
                continue

            return split_position + len(separator)

        return target_end

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized_lines = [
            line.strip() for line in text.replace("\x00", "").splitlines()
        ]

        paragraphs: list[str] = []
        current_paragraph: list[str] = []

        for line in normalized_lines:
            if line:
                current_paragraph.append(line)
                continue

            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []

        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        return "\n\n".join(paragraphs).strip()
