import torch
import numpy as np
from PIL import Image
import cv2
from app.models.ml_models import ImageDeepFakeDetector, VideoDeepFakeDetector, AudioDeepFakeDetector
from app.utils.media_processor import extract_frames, process_audio

class DeepFakeDetector:
    def __init__(self):
        self.image_detector = ImageDeepFakeDetector()
        self.video_detector = VideoDeepFakeDetector()
        self.audio_detector = AudioDeepFakeDetector()
        
    def analyze_media(self, file_path):
        """Analyze image for potential deep fake manipulation."""
        try:
            # Load and preprocess image
            image = Image.open(file_path)
            processed_image = self._preprocess_image(image)
            
            # Get prediction
            fake_probability = self.image_detector.predict(processed_image)
            
            # Analyze specific regions
            region_analysis = self._analyze_image_regions(processed_image)
            
            return {
                'is_fake': fake_probability > 0.7,
                'fake_probability': float(fake_probability),
                'confidence_score': self._calculate_confidence(fake_probability),
                'region_analysis': region_analysis,
                'metadata': self._extract_image_metadata(image)
            }
        except Exception as e:
            return {'error': f'Media analysis failed: {str(e)}'}
    
    def analyze_video(self, file_path):
        """Analyze video for deep fake manipulation."""
        try:
            # Extract frames from video
            frames = extract_frames(file_path)
            
            # Analyze each frame
            frame_results = []
            for frame in frames:
                processed_frame = self._preprocess_image(frame)
                result = self.video_detector.predict_frame(processed_frame)
                frame_results.append(result)
            
            # Aggregate results
            overall_score = np.mean([r['fake_probability'] for r in frame_results])
            
            return {
                'is_fake': overall_score > 0.7,
                'fake_probability': float(overall_score),
                'frame_analysis': self._summarize_frame_analysis(frame_results),
                'temporal_consistency': self._check_temporal_consistency(frame_results),
                'metadata': self._extract_video_metadata(file_path)
            }
        except Exception as e:
            return {'error': f'Video analysis failed: {str(e)}'}
    
    def analyze_audio(self, file_path):
        """Analyze audio for synthetic voice detection."""
        try:
            # Process audio file
            audio_features = process_audio(file_path)
            
            # Get prediction
            fake_probability = self.audio_detector.predict(audio_features)
            
            return {
                'is_synthetic': fake_probability > 0.7,
                'synthetic_probability': float(fake_probability),
                'voice_analysis': self._analyze_voice_characteristics(audio_features),
                'metadata': self._extract_audio_metadata(file_path)
            }
        except Exception as e:
            return {'error': f'Audio analysis failed: {str(e)}'}
    
    def _preprocess_image(self, image):
        """Preprocess image for model input."""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size
        image = image.resize((224, 224))
        
        # Convert to tensor and normalize
        image_tensor = torch.from_numpy(np.array(image))
        image_tensor = image_tensor.permute(2, 0, 1).float() / 255.0
        
        return image_tensor
    
    def _analyze_image_regions(self, image_tensor):
        """Analyze specific regions of the image for manipulation."""
        regions = {
            'face': self._analyze_facial_features(image_tensor),
            'background': self._analyze_background(image_tensor),
            'artifacts': self._detect_artifacts(image_tensor)
        }
        return regions
    
    def _calculate_confidence(self, probability):
        """Calculate confidence score based on probability."""
        # Implement confidence calculation logic
        return min(1.0, probability * 1.2)  # Simple scaling example
