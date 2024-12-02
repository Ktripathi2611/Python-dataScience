import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

def preprocess_text(text):
    """
    Preprocess text for analysis.
    
    Args:
        text (str): Input text to preprocess
        
    Returns:
        str: Preprocessed text
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenization
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    # Join tokens back into text
    preprocessed_text = ' '.join(tokens)
    
    return preprocessed_text

def extract_urls(text):
    """
    Extract URLs from text.
    
    Args:
        text (str): Input text to extract URLs from
        
    Returns:
        list: List of extracted URLs
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

def extract_email_addresses(text):
    """
    Extract email addresses from text.
    
    Args:
        text (str): Input text to extract email addresses from
        
    Returns:
        list: List of extracted email addresses
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

def clean_html(text):
    """
    Remove HTML tags from text.
    
    Args:
        text (str): Input text containing HTML
        
    Returns:
        str: Clean text without HTML tags
    """
    html_pattern = re.compile('<.*?>')
    return re.sub(html_pattern, '', text)

def normalize_text(text):
    """
    Normalize text by removing extra whitespace and special characters.
    
    Args:
        text (str): Input text to normalize
        
    Returns:
        str: Normalized text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Replace special characters with space
    text = re.sub(r'[^\w\s]', ' ', text)
    
    return text.strip()
