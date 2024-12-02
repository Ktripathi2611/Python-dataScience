import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib
import re

class SpamDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.spam_patterns = [
            r'\b(?:viagra|cialis|lottery|winner|inheritance|prince)\b',
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            r'(?i)urgent|important|action required',
            r'(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?'  # IP addresses and ports
        ]
    
    def preprocess_text(self, text):
        """Clean and normalize text data."""
        text = text.lower()
        text = re.sub(r'http\S+|www\S+', 'URL', text)
        text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', 'EMAIL', text)
        text = re.sub(r'\d+', 'NUMBER', text)
        return text
    
    def extract_features(self, text):
        """Extract additional spam-related features."""
        features = {
            'has_urls': len(re.findall(r'http\S+|www\S+', text)) > 0,
            'has_email': len(re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)) > 0,
            'caps_ratio': sum(1 for c in text if c.isupper()) / (len(text) + 1),
            'spam_pattern_count': sum(len(re.findall(pattern, text)) for pattern in self.spam_patterns)
        }
        return features
    
    def analyze_content(self, text):
        """Analyze content for spam characteristics."""
        preprocessed_text = self.preprocess_text(text)
        features = self.extract_features(text)
        
        # Calculate spam probability based on features
        spam_score = (
            features['spam_pattern_count'] * 0.4 +
            features['caps_ratio'] * 0.2 +
            (1 if features['has_urls'] else 0) * 0.2 +
            (1 if features['has_email'] else 0) * 0.2
        )
        
        # Analyze text characteristics
        analysis = {
            'spam_probability': min(spam_score, 1.0),
            'features': features,
            'detected_patterns': [
                pattern for pattern in self.spam_patterns 
                if re.search(pattern, text)
            ],
            'risk_level': self._calculate_risk_level(spam_score)
        }
        
        return analysis
    
    def _calculate_risk_level(self, spam_score):
        """Calculate risk level based on spam score."""
        if spam_score < 0.3:
            return {'level': 'low', 'color': 'green'}
        elif spam_score < 0.7:
            return {'level': 'medium', 'color': 'yellow'}
        else:
            return {'level': 'high', 'color': 'red'}
    
    def save_model(self, path):
        """Save the trained model."""
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'spam_patterns': self.spam_patterns
        }
        joblib.dump(model_data, path)
    
    def load_model(self, path):
        """Load a trained model."""
        model_data = joblib.load(path)
        self.vectorizer = model_data['vectorizer']
        self.classifier = model_data['classifier']
        self.spam_patterns = model_data['spam_patterns']
