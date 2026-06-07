import pypdf
import io


class PDFExtractor:
    """Extracts text content from PDF files."""

    @staticmethod
    def extract_from_path(file_path):
        """Extract text from a PDF file on disk.

        Args:
            file_path: Absolute path to the PDF file.

        Returns:
            dict with keys: text (str), page_count (int), word_count (int)
        Raises:
            ValueError: if the file is not a valid PDF or is empty.
        """
        try:
            reader = pypdf.PdfReader(file_path)
            pages = []
            for page in reader.pages:
                page_text = page.extract_text() or ''
                pages.append(page_text)

            full_text = '\n\n'.join(pages)

            if not full_text.strip() or len(full_text.strip()) < len(reader.pages) * 50:
                print('[INFO] PDF text is sparse or missing. Attempting Gemini OCR fallback...')
                from utils.llm import GeminiLLM
                client = GeminiLLM._get_client()
                try:
                    gemini_file = client.files.upload(file=file_path)
                    prompt = "Extract all text from this document accurately. Do not summarize."
                    response = client.models.generate_content(
                        model='gemini-flash-latest',
                        contents=[gemini_file, prompt]
                    )
                    ocr_text = response.text
                    client.files.delete(name=gemini_file.name)
                    
                    if ocr_text and len(ocr_text.strip()) > len(full_text.strip()):
                        full_text = ocr_text
                        print('[INFO] Gemini OCR successful.')
                except Exception as e:
                    print(f'[WARN] Gemini OCR failed: {e}')

            if not full_text.strip():
                raise ValueError('PDF appears to be empty or image-only (no extractable text).')

            word_count = len(full_text.split())

            return {
                'text': full_text,
                'page_count': len(reader.pages),
                'word_count': word_count,
            }
        except pypdf.errors.PdfReadError as e:
            raise ValueError(f'Could not read PDF: {e}')
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f'PDF extraction failed: {e}')

    @staticmethod
    def extract_from_bytes(file_bytes):
        """Extract text from PDF bytes (in-memory).

        Args:
            file_bytes: Raw PDF bytes.

        Returns:
            dict with keys: text, page_count, word_count
        """
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pages = []
            for page in reader.pages:
                page_text = page.extract_text() or ''
                pages.append(page_text)

            full_text = '\n\n'.join(pages)

            if not full_text.strip() or len(full_text.strip()) < len(reader.pages) * 50:
                print('[INFO] PDF text is sparse or missing. Attempting Gemini OCR fallback...')
                import tempfile
                import os
                from utils.llm import GeminiLLM
                
                client = GeminiLLM._get_client()
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        tmp.write(file_bytes)
                        tmp_path = tmp.name
                        
                    gemini_file = client.files.upload(file=tmp_path)
                    prompt = "Extract all text from this document accurately. Do not summarize."
                    response = client.models.generate_content(
                        model='gemini-flash-latest',
                        contents=[gemini_file, prompt]
                    )
                    ocr_text = response.text
                    client.files.delete(name=gemini_file.name)
                    os.remove(tmp_path)
                    
                    if ocr_text and len(ocr_text.strip()) > len(full_text.strip()):
                        full_text = ocr_text
                        print('[INFO] Gemini OCR successful.')
                except Exception as e:
                    print(f'[WARN] Gemini OCR failed: {e}')

            if not full_text.strip():
                raise ValueError('PDF appears to be empty or image-only.')

            return {
                'text': full_text,
                'page_count': len(reader.pages),
                'word_count': len(full_text.split()),
            }
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f'PDF extraction failed: {e}')
