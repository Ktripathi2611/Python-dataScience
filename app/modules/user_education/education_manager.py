from typing import Dict, List, Optional
import json
import datetime

class EducationManager:
    def __init__(self):
        self.training_modules = {
            'spam_awareness': {
                'title': 'Spam and Phishing Awareness',
                'topics': [
                    'Identifying suspicious emails',
                    'Common phishing tactics',
                    'Safe browsing practices',
                    'Password security'
                ]
            },
            'network_security': {
                'title': 'Network Security Basics',
                'topics': [
                    'Understanding network threats',
                    'Secure connection practices',
                    'VPN usage',
                    'Public WiFi safety'
                ]
            },
            'deepfake_awareness': {
                'title': 'Deepfake Detection',
                'topics': [
                    'Understanding deepfakes',
                    'Visual indicators',
                    'Audio manipulation signs',
                    'Verification techniques'
                ]
            },
            'incident_response': {
                'title': 'Security Incident Response',
                'topics': [
                    'Recognizing security incidents',
                    'Immediate response steps',
                    'Reporting procedures',
                    'Recovery practices'
                ]
            }
        }
        
        self.user_progress = {}
        self.recommendations = {}
    
    def get_training_module(self, module_id: str) -> Optional[Dict]:
        """Get details of a specific training module."""
        return self.training_modules.get(module_id)
    
    def get_all_modules(self) -> Dict:
        """Get all available training modules."""
        return self.training_modules
    
    def track_user_progress(self, user_id: str, module_id: str, progress: float):
        """Track user's progress in a specific module."""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        self.user_progress[user_id][module_id] = {
            'progress': progress,
            'last_updated': datetime.datetime.now().isoformat()
        }
    
    def get_user_progress(self, user_id: str) -> Dict:
        """Get user's progress across all modules."""
        return self.user_progress.get(user_id, {})
    
    def generate_recommendations(self, user_id: str, threat_history: List[Dict]) -> List[str]:
        """Generate personalized training recommendations based on threat history."""
        recommendations = []
        
        # Analyze threat history
        threat_types = [threat['type'] for threat in threat_history]
        
        # Count threat occurrences
        threat_counts = {}
        for threat in threat_types:
            threat_counts[threat] = threat_counts.get(threat, 0) + 1
        
        # Generate recommendations based on threat patterns
        if 'spam' in threat_counts or 'phishing' in threat_counts:
            recommendations.append('spam_awareness')
        
        if 'network_attack' in threat_counts or 'unauthorized_access' in threat_counts:
            recommendations.append('network_security')
        
        if 'deepfake' in threat_counts:
            recommendations.append('deepfake_awareness')
        
        if len(threat_history) > 5:
            recommendations.append('incident_response')
        
        self.recommendations[user_id] = {
            'recommendations': recommendations,
            'generated_at': datetime.datetime.now().isoformat()
        }
        
        return recommendations
    
    def get_module_content(self, module_id: str, topic_index: int) -> Optional[Dict]:
        """Get specific content for a module topic."""
        module = self.training_modules.get(module_id)
        if not module or topic_index >= len(module['topics']):
            return None
        
        topic = module['topics'][topic_index]
        return {
            'module_id': module_id,
            'topic': topic,
            'content': self._get_topic_content(module_id, topic)
        }
    
    def _get_topic_content(self, module_id: str, topic: str) -> Dict:
        """Get detailed content for a specific topic."""
        # This would typically fetch content from a database or content management system
        # For now, returning placeholder content
        return {
            'title': topic,
            'description': f"Detailed information about {topic}",
            'key_points': [
                'Important point 1',
                'Important point 2',
                'Important point 3'
            ],
            'examples': [
                'Example 1',
                'Example 2'
            ],
            'quiz': [
                {
                    'question': f"Sample question about {topic}?",
                    'options': ['Option 1', 'Option 2', 'Option 3', 'Option 4'],
                    'correct_answer': 0
                }
            ]
        }
    
    def get_user_recommendations(self, user_id: str) -> List[str]:
        """Get stored recommendations for a user."""
        return self.recommendations.get(user_id, {}).get('recommendations', [])
    
    def mark_topic_completed(self, user_id: str, module_id: str, topic_index: int):
        """Mark a specific topic as completed for a user."""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        if module_id not in self.user_progress[user_id]:
            self.user_progress[user_id][module_id] = {
                'progress': 0.0,
                'completed_topics': []
            }
        
        module = self.training_modules.get(module_id)
        if module and topic_index < len(module['topics']):
            if 'completed_topics' not in self.user_progress[user_id][module_id]:
                self.user_progress[user_id][module_id]['completed_topics'] = []
            
            completed_topics = self.user_progress[user_id][module_id]['completed_topics']
            if topic_index not in completed_topics:
                completed_topics.append(topic_index)
                # Update progress percentage
                progress = len(completed_topics) / len(module['topics']) * 100
                self.user_progress[user_id][module_id]['progress'] = progress
    
    def get_completion_certificate(self, user_id: str, module_id: str) -> Optional[Dict]:
        """Generate a completion certificate for a completed module."""
        user_module_progress = self.user_progress.get(user_id, {}).get(module_id, {})
        if user_module_progress.get('progress', 0) == 100:
            return {
                'user_id': user_id,
                'module_id': module_id,
                'module_name': self.training_modules[module_id]['title'],
                'completion_date': datetime.datetime.now().isoformat(),
                'certificate_id': f"{user_id}-{module_id}-{datetime.datetime.now().strftime('%Y%m%d')}"
            }
        return None
