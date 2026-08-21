from __future__ import annotations

import re
from dataclasses import dataclass


def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


@dataclass
class Chunk:
    text: str
    chunk_index: int
    char_start: int
    char_end: int


def split_into_paragraphs(text: str) -> list[str]:
    # Normalize whitespace, then split on blank lines.
    text = text.replace("\r\n", "\n")
    paras = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paras if p.strip()]


def chunk_text(text: str, chunk_size_tokens: int, overlap_tokens: int) -> list[Chunk]:
    paragraphs = split_into_paragraphs(text)
    chunks: list[Chunk] = []

    current_paras: list[str] = []
    current_tokens = 0
    char_cursor = 0
    chunk_start_char = 0

    def flush():
        nonlocal current_paras, current_tokens, chunk_start_char
        if not current_paras:
            return
        chunk_body = "\n\n".join(current_paras)
        chunks.append(
            Chunk(
                text=chunk_body,
                chunk_index=len(chunks),
                char_start=chunk_start_char,
                char_end=chunk_start_char + len(chunk_body),
            )
        )

    for para in paragraphs:
        para_tokens = _approx_tokens(para)

        # Single paragraph bigger than the whole chunk budget: hard-split it.
        if para_tokens > chunk_size_tokens:
            if current_paras:
                flush()
                current_paras, current_tokens = [], 0
            words = para.split()
            window_words = chunk_size_tokens * 4  # ~4 chars/token, ~1 token/word-ish
            step = max(1, window_words - overlap_tokens * 4)
            for i in range(0, len(words), step):
                sub = " ".join(words[i : i + window_words])
                if not sub:
                    continue
                chunk_start_char = char_cursor
                current_paras = [sub]
                flush()
                current_paras, current_tokens = [], 0
            char_cursor += len(para)
            chunk_start_char = char_cursor
            continue

        if current_tokens + para_tokens > chunk_size_tokens and current_paras:
            flush()
            # carry overlap forward: keep trailing paragraphs worth ~overlap_tokens
            overlap_paras: list[str] = []
            running = 0
            for p in reversed(current_paras):
                running += _approx_tokens(p)
                overlap_paras.insert(0, p)
                if running >= overlap_tokens:
                    break
            current_paras = overlap_paras
            current_tokens = sum(_approx_tokens(p) for p in current_paras)
            chunk_start_char = char_cursor - sum(len(p) for p in overlap_paras)

        current_paras.append(para)
        current_tokens += para_tokens
        char_cursor += len(para) + 2  # account for the paragraph separator

    flush()
    return [c for c in chunks if c.text.strip()]
