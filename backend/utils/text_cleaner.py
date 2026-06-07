import re


class TextCleaner:
    """Cleans and normalizes extracted text for processing."""

    @staticmethod
    def clean(text):
        """Clean raw extracted text.

        Steps:
        1. Normalize unicode whitespace
        2. Remove control characters (except newlines/tabs)
        3. Collapse excessive blank lines (max 2 consecutive)
        4. Collapse multiple spaces into one
        5. Strip leading/trailing whitespace from each line

        Args:
            text: Raw text string.

        Returns:
            Cleaned text string.
        """
        if not text:
            return ''

        # Replace Windows line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Remove control characters except \n and \t
        text = re.sub(r'[^\S\n\t ]+', ' ', text)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        # Strip each line
        lines = [line.strip() for line in text.split('\n')]

        # Remove trailing spaces
        text = '\n'.join(lines)

        # Collapse 3+ consecutive blank lines into 2
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Collapse multiple spaces
        text = re.sub(r'[ \t]{2,}', ' ', text)

        return text.strip()

    @staticmethod
    def clean_txt_file(raw_bytes, encoding='utf-8'):
        """Decode and clean a plain text file.

        Args:
            raw_bytes: Raw bytes from the uploaded file.
            encoding:  Encoding to try first (default utf-8).

        Returns:
            dict with keys: text (str), word_count (int)
        Raises:
            ValueError: if file cannot be decoded.
        """
        # Try UTF-8 first, fallback to latin-1
        for enc in [encoding, 'latin-1', 'cp1252']:
            try:
                text = raw_bytes.decode(enc)
                text = TextCleaner.clean(text)
                if not text.strip():
                    raise ValueError('Text file appears to be empty.')
                return {
                    'text': text,
                    'word_count': len(text.split()),
                }
            except (UnicodeDecodeError, ValueError) as e:
                if enc == 'cp1252':
                    raise ValueError(f'Could not decode text file: {e}')
                continue
