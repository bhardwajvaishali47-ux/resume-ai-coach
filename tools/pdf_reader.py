import re
import pdfplumber
from langchain_core.tools import tool


def clean_text(text: str) -> str:
    """
    Cleans extracted PDF text.
    Removes font encoding artifacts like (cid:127)
    that appear when PDF uses custom bullet symbols.
    """
    text = re.sub(r'\(cid:\d+\)', '•', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


@tool
def read_pdf(file_path: str) -> str:
    """
    Reads a PDF file and extracts all text content.
    Use this tool when you need to read the contents
    of a resume PDF file.
    Takes the full file path as input.
    Returns the extracted text as a string.
    """
    return extract_text_from_pdf(file_path)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Direct function version of the PDF reader.
    Use this when calling directly from other Python files
    without going through the LangChain tool interface.
    Takes the full file path as input.
    Returns the extracted text as a string.
    """
    extracted_text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"

    cleaned = clean_text(extracted_text)

    if len(cleaned) < 100:
        return "ERROR: Could not extract text from PDF. Please upload a text-based PDF from Word or Google Docs."

    return cleaned


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"Reading PDF: {pdf_path}")
        print("---")
        text = extract_text_from_pdf(pdf_path)
        print(text)
        print("---")
        print(f"Total characters extracted: {len(text)}")
    else:
        print("Please provide a PDF path")
        print("Usage: python tools/pdf_reader.py yourfile.pdf")