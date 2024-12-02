from flask import Flask, request, jsonify
from typing import Dict, Any
import torch
import numpy as np
from PIL import Image
import io
import logging
from .model_manager import ModelManager

class ModelServer:
    def __init__(self, model_manager: ModelManager):
        self.app = Flask(__name__)
        self.model_manager = model_manager
        self.setup_routes()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('model_server.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_routes(self):
        """Setup API endpoints."""
        # Phishing detection endpoint
        @self.app.route('/api/detect/phishing', methods=['POST'])
        def detect_phishing():
            try:
                data = request.get_json()
                if not data or 'text' not in data:
                    return jsonify({'error': 'No text provided'}), 400
                
                result = self.model_manager.predict_phishing(data['text'])
                return jsonify(result)
            except Exception as e:
                self.logger.error(f"Error in phishing detection: {str(e)}")
                return jsonify({'error': str(e)}), 500

        # Deepfake detection endpoint
        @self.app.route('/api/detect/deepfake', methods=['POST'])
        def detect_deepfake():
            try:
                if 'image' not in request.files:
                    return jsonify({'error': 'No image provided'}), 400
                
                image_file = request.files['image']
                image = Image.open(io.BytesIO(image_file.read()))
                
                result = self.model_manager.predict_deepfake(image)
                return jsonify(result)
            except Exception as e:
                self.logger.error(f"Error in deepfake detection: {str(e)}")
                return jsonify({'error': str(e)}), 500

        # Model health check endpoint
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            try:
                status = self.model_manager.check_models_status()
                return jsonify(status)
            except Exception as e:
                self.logger.error(f"Error in health check: {str(e)}")
                return jsonify({'error': str(e)}), 500

        # Model metrics endpoint
        @self.app.route('/api/metrics', methods=['GET'])
        def get_metrics():
            try:
                metrics = self.model_manager.get_model_metrics()
                return jsonify(metrics)
            except Exception as e:
                self.logger.error(f"Error getting metrics: {str(e)}")
                return jsonify({'error': str(e)}), 500

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the model server."""
        self.logger.info(f"Starting model server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """Preprocess text input for model inference."""
        try:
            # Tokenize and prepare input
            tokenizer = self.model_manager.get_tokenizer('phishing_detection')
            inputs = tokenizer(
                text,
                truncation=True,
                padding=True,
                return_tensors='pt'
            )
            return inputs
        except Exception as e:
            self.logger.error(f"Error preprocessing text: {str(e)}")
            raise

    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image input for model inference."""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize and normalize image
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
        except Exception as e:
            self.logger.error(f"Error preprocessing image: {str(e)}")
            raise

    def format_response(self, predictions: torch.Tensor, task: str) -> Dict[str, Any]:
        """Format model predictions for API response."""
        try:
            probabilities = torch.nn.functional.softmax(predictions, dim=1)
            confidence, prediction = torch.max(probabilities, dim=1)
            
            response = {
                'prediction': prediction.item(),
                'confidence': confidence.item(),
                'probabilities': probabilities[0].tolist(),
                'task': task,
                'timestamp': str(torch.datetime.now())
            }
            
            if task == 'phishing_detection':
                response['label'] = 'phishing' if prediction.item() == 1 else 'legitimate'
            elif task == 'deepfake_detection':
                response['label'] = 'fake' if prediction.item() == 1 else 'real'
            
            return response
        except Exception as e:
            self.logger.error(f"Error formatting response: {str(e)}")
            raise
