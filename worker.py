from docling.document_converter import DocumentConverter

def convert_to_markdown(source: str, use_gpu: bool) -> str | None:
    try:
        converter = DocumentConverter()
        return converter.convert(source).document.export_to_markdown()
    except Exception as e:
        return f"[ERROR] {source}: {e}"
