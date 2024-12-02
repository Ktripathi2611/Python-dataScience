import tensorflow as tf
import numpy as np
from urllib.parse import urlparse
from app.models.ml_models import PhishingDetector, SpamDetector
from app.utils.text_preprocessor import preprocess_text

class ThreatAnalyzer:
    def __init__(self):
        self.phishing_detector = PhishingDetector()
        self.spam_detector = SpamDetector()
        
    def analyze_url(self, url):
        """Analyze URL for potential phishing threats."""
        try:
            # Extract URL features
            parsed_url = urlparse(url)
            features = self._extract_url_features(parsed_url)
            
            # Get prediction
            threat_score = self.phishing_detector.predict(features)
            
            return {
                'url': url,
                'threat_score': float(threat_score),
                'is_suspicious': threat_score > 0.7,
                'analysis_details': self._get_url_analysis_details(parsed_url)
            }
        except Exception as e:
            return {'error': f'URL analysis failed: {str(e)}'}
    
    def scan_email(self, content):
        """Scan email content for spam and phishing indicators."""
        try:
            # Preprocess email content
            processed_content = preprocess_text(content)
            
            # Get predictions
            spam_score = self.spam_detector.predict(processed_content)
            phishing_score = self.phishing_detector.predict_text(processed_content)
            
            return {
                'spam_score': float(spam_score),
                'phishing_score': float(phishing_score),
                'is_suspicious': spam_score > 0.8 or phishing_score > 0.7,
                'analysis_details': self._get_email_analysis_details(content)
            }
        except Exception as e:
            return {'error': f'Email scan failed: {str(e)}'}
    
    def process_threat_report(self, threat_type, threat_data):
        """Process user-reported threats and update models."""
        try:
            if threat_type == 'phishing':
                self.phishing_detector.update_model(threat_data)
            elif threat_type == 'spam':
                self.spam_detector.update_model(threat_data)
                
            return {
                'status': 'success',
                'message': f'Threat report processed for type: {threat_type}'
            }
        except Exception as e:
            return {'error': f'Threat report processing failed: {str(e)}'}
    
    def _extract_url_features(self, parsed_url):
        """Extract relevant features from URL for analysis."""
        features = {
            'length': len(parsed_url.geturl()),
            'num_dots': parsed_url.netloc.count('.'),
            'has_suspicious_words': self._check_suspicious_words(parsed_url.geturl()),
            'is_ip_address': self._is_ip_address(parsed_url.netloc),
            'has_suspicious_tld': self._check_suspicious_tld(parsed_url.netloc)
        }
        return features
    
    def _get_url_analysis_details(self, parsed_url):
        """Generate detailed analysis report for URL."""
        return {
            'domain': parsed_url.netloc,
            'path': parsed_url.path,
            'query_params': parsed_url.query,
            'security_checks': {
                'ssl_verified': self._check_ssl(parsed_url),
                'domain_age': self._get_domain_age(parsed_url.netloc),
                'blacklist_status': self._check_blacklist(parsed_url.netloc)
            }
        }
    
    def _get_email_analysis_details(self, content):
        """Generate detailed analysis report for email content."""
        return {
            'content_length': len(content),
            'has_attachments': 'attachment' in content.lower(),
            'has_urgent_words': self._check_urgent_words(content),
            'links_analysis': self._analyze_email_links(content)
        }
