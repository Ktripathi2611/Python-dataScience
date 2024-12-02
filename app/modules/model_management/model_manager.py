import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import Dict, List, Optional, Union, Any
import os
import json
import logging
from datetime import datetime
from PIL import Image
import numpy as np
from collections import deque

class ModelManager:
    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        self.models = {}
        self.tokenizers = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.metrics_history = {
            'phishing_detection': deque(maxlen=1000),
            'deepfake_detection': deque(maxlen=1000)
        }
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('model_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_model(self, task: str, model_path: str):
        """Load a model for a specific task."""
        try:
            self.logger.info(f"Loading model for {task} from {model_path}")
            
            # Load model and tokenizer
            self.models[task] = AutoModelForSequenceClassification.from_pretrained(
                model_path
            ).to(self.device)
            self.models[task].eval()
            
            self.tokenizers[task] = AutoTokenizer.from_pretrained(model_path)
            
            self.logger.info(f"Successfully loaded model for {task}")
        except Exception as e:
            self.logger.error(f"Error loading model for {task}: {str(e)}")
            raise

    def get_latest_model_path(self, task: str) -> Optional[str]:
        """Get the path to the latest model version for a task."""
        task_dir = os.path.join(self.models_dir, task)
        if not os.path.exists(task_dir):
            return None
        
        versions = [d for d in os.listdir(task_dir) if os.path.isdir(os.path.join(task_dir, d))]
        if not versions:
            return None
        
        latest_version = sorted(versions)[-1]
        return os.path.join(task_dir, latest_version)

    def predict_phishing(self, text: str) -> Dict[str, Any]:
        """Make phishing detection prediction."""
        task = 'phishing_detection'
        try:
            # Ensure model is loaded
            if task not in self.models:
                model_path = self.get_latest_model_path(task)
                if not model_path:
                    raise ValueError(f"No model found for {task}")
                self.load_model(task, model_path)
            
            # Preprocess input
            inputs = self.tokenizers[task](
                text,
                truncation=True,
                padding=True,
                return_tensors='pt'
            ).to(self.device)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.models[task](**inputs)
            
            # Process results
            result = self._format_prediction(outputs, task)
            
            # Store metrics
            self._store_prediction_metrics(task, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Error in phishing prediction: {str(e)}")
            raise

    def predict_deepfake(self, image: Image.Image) -> Dict[str, Any]:
        """Make deepfake detection prediction."""
        task = 'deepfake_detection'
        try:
            # Ensure model is loaded
            if task not in self.models:
                model_path = self.get_latest_model_path(task)
                if not model_path:
                    raise ValueError(f"No model found for {task}")
                self.load_model(task, model_path)
            
            # Preprocess image
            image_tensor = self._preprocess_image(image)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.models[task](image_tensor.to(self.device))
            
            # Process results
            result = self._format_prediction(outputs, task)
            
            # Store metrics
            self._store_prediction_metrics(task, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Error in deepfake prediction: {str(e)}")
            raise

    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for model input."""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize and normalize
        image = image.resize((224, 224))
        image_array = np.array(image)
        image_tensor = torch.from_numpy(image_array).float()
        image_tensor = image_tensor.permute(2, 0, 1)  # Convert to CxHxW format
        
        # Normalize
        image_tensor = image_tensor / 255.0
        mean = torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1)
        image_tensor = (image_tensor - mean) / std
        
        return image_tensor.unsqueeze(0)  # Add batch dimension

    def _format_prediction(self, outputs: Any, task: str) -> Dict[str, Any]:
        """Format model outputs into standardized prediction result."""
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
        confidence, prediction = torch.max(probabilities, dim=1)
        
        result = {
            'prediction': prediction.item(),
            'confidence': confidence.item(),
            'probabilities': probabilities[0].tolist(),
            'task': task,
            'timestamp': datetime.now().isoformat()
        }
        
        if task == 'phishing_detection':
            result['label'] = 'phishing' if prediction.item() == 1 else 'legitimate'
        elif task == 'deepfake_detection':
            result['label'] = 'fake' if prediction.item() == 1 else 'real'
        
        return result

    def _store_prediction_metrics(self, task: str, result: Dict[str, Any]):
        """Store prediction metrics for monitoring."""
        self.metrics_history[task].append({
            'timestamp': result['timestamp'],
            'confidence': result['confidence'],
            'prediction': result['prediction']
        })

    def get_model_metrics(self) -> Dict[str, Any]:
        """Get metrics for all models."""
        metrics = {}
        for task in self.metrics_history:
            if self.metrics_history[task]:
                predictions = list(self.metrics_history[task])
                confidences = [p['confidence'] for p in predictions]
                metrics[task] = {
                    'total_predictions': len(predictions),
                    'average_confidence': sum(confidences) / len(confidences),
                    'predictions_by_class': self._count_predictions_by_class(task)
                }
        return metrics

    def _count_predictions_by_class(self, task: str) -> Dict[str, int]:
        """Count predictions by class for a specific task."""
        counts = {'0': 0, '1': 0}
        for pred in self.metrics_history[task]:
            counts[str(pred['prediction'])] += 1
        return counts

    def check_models_status(self) -> Dict[str, Any]:
        """Check the status of all loaded models."""
        status = {}
        for task in ['phishing_detection', 'deepfake_detection']:
            if task in self.models:
                model_path = self.get_latest_model_path(task)
                status[task] = {
                    'loaded': True,
                    'device': str(self.device),
                    'model_path': model_path,
                    'last_prediction': self._get_last_prediction_time(task)
                }
            else:
                status[task] = {'loaded': False}
        return status

    def _get_last_prediction_time(self, task: str) -> Optional[str]:
        """Get the timestamp of the last prediction for a task."""
        if self.metrics_history[task]:
            return self.metrics_history[task][-1]['timestamp']
        return None

    def get_tokenizer(self, task: str) -> Optional[AutoTokenizer]:
        """Get the tokenizer for a specific task."""
        return self.tokenizers.get(task)
