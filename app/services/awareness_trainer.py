from datetime import datetime
from app.models.db_models import Tutorial, Quiz, SecurityTip, ResponseGuide
from app.utils.content_generator import generate_personalized_content

class AwarenessTrainer:
    def __init__(self):
        self.tutorials = Tutorial()
        self.quizzes = Quiz()
        self.security_tips = SecurityTip()
        self.response_guides = ResponseGuide()
    
    def get_security_tips(self, category='general'):
        """Get security tips based on category and user context."""
        try:
            # Get base tips for category
            tips = self.security_tips.get_by_category(category)
            
            # Personalize tips based on user context
            personalized_tips = self._personalize_tips(tips)
            
            return {
                'category': category,
                'tips': personalized_tips,
                'last_updated': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'error': f'Failed to retrieve security tips: {str(e)}'}
    
    def get_tutorial(self, topic):
        """Get tutorial content for specific security topic."""
        try:
            # Get tutorial content
            tutorial = self.tutorials.get_by_topic(topic)
            
            # Generate interactive elements
            interactive_content = self._generate_interactive_content(topic)
            
            return {
                'topic': topic,
                'content': tutorial['content'],
                'interactive_elements': interactive_content,
                'estimated_duration': tutorial['duration'],
                'difficulty_level': tutorial['difficulty']
            }
        except Exception as e:
            return {'error': f'Failed to retrieve tutorial: {str(e)}'}
    
    def evaluate_quiz(self, user_id, quiz_id, answers):
        """Evaluate user's quiz answers and provide feedback."""
        try:
            # Get quiz questions and correct answers
            quiz = self.quizzes.get_by_id(quiz_id)
            
            # Evaluate answers
            results = self._evaluate_answers(quiz, answers)
            
            # Update user progress
            self._update_user_progress(user_id, quiz_id, results)
            
            return {
                'score': results['score'],
                'correct_answers': results['correct_count'],
                'total_questions': len(quiz['questions']),
                'feedback': results['feedback'],
                'recommendations': self._generate_recommendations(results)
            }
        except Exception as e:
            return {'error': f'Failed to evaluate quiz: {str(e)}'}
    
    def get_response_guide(self, incident_type):
        """Get response guide for specific security incident type."""
        try:
            # Get base guide
            guide = self.response_guides.get_by_type(incident_type)
            
            # Enhance with current best practices
            enhanced_guide = self._enhance_guide(guide)
            
            return {
                'incident_type': incident_type,
                'steps': enhanced_guide['steps'],
                'resources': enhanced_guide['resources'],
                'emergency_contacts': enhanced_guide['contacts'],
                'preventive_measures': enhanced_guide['prevention']
            }
        except Exception as e:
            return {'error': f'Failed to retrieve response guide: {str(e)}'}
    
    def _personalize_tips(self, tips):
        """Personalize security tips based on user context and behavior."""
        personalized_tips = []
        for tip in tips:
            personalized_content = generate_personalized_content(tip['content'])
            personalized_tips.append({
                'id': tip['id'],
                'content': personalized_content,
                'priority': tip['priority'],
                'category': tip['category']
            })
        return personalized_tips
    
    def _generate_interactive_content(self, topic):
        """Generate interactive content for tutorials."""
        return {
            'quizzes': self._generate_mini_quizzes(topic),
            'exercises': self._generate_practical_exercises(topic),
            'simulations': self._generate_security_simulations(topic)
        }
    
    def _evaluate_answers(self, quiz, user_answers):
        """Evaluate quiz answers and generate feedback."""
        correct_count = 0
        feedback = []
        
        for q_id, answer in user_answers.items():
            is_correct = self._check_answer(quiz, q_id, answer)
            if is_correct:
                correct_count += 1
            feedback.append(self._generate_answer_feedback(quiz, q_id, is_correct))
        
        score = (correct_count / len(quiz['questions'])) * 100
        
        return {
            'score': score,
            'correct_count': correct_count,
            'feedback': feedback
        }
    
    def _enhance_guide(self, guide):
        """Enhance response guide with current best practices and resources."""
        return {
            'steps': guide['steps'],
            'resources': self._get_updated_resources(guide['type']),
            'contacts': self._get_emergency_contacts(guide['type']),
            'prevention': self._generate_preventive_measures(guide['type'])
        }
