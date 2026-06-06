import re

def clean_text(text):
    """Converts text to lowercase and removes extra whitespaces."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_sentences(text):
    """Splits text into sentences based on punctuation."""
    # Split by periods, exclamation marks, or question marks
    sentences = re.split(r'[.!?]', text)
    # Clean and filter out empty strings
    return [clean_text(s) for s in sentences if len(clean_text(s)) > 10]