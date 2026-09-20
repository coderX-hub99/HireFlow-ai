import fitz


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []

    document = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    for page in document:
        page_text = page.get_text("text")
        if page_text:
            text_parts.append(page_text)

    document.close()

    return "\n".join(text_parts).strip()


def extract_text(uploaded_file) -> str:
    """
    Extract text from Streamlit UploadedFile.
    Supports PDF and TXT/MD files.
    """

    filename = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(data)

    if filename.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="ignore").strip()

    raise ValueError(
        f"Unsupported file type: {uploaded_file.name}"
    )


def clip_text(text: str, max_chars: int = 30000) -> str:
    text = text.strip()

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n\n[TEXT TRUNCATED]"