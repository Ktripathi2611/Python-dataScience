import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from typing import Dict, List, Optional, Union
import os
import json
import logging
from datetime import datetime

class ModelTrainer:
    def __init__(self, config_path: str = 'config/model_config.json'):
        self.config = self._load_config(config_path)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.tokenizers = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('training.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path: str) -> Dict:
        """Load model configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'phishing_detection': {
                    'base_model': 'bert-base-uncased',
                    'num_labels': 2,
                    'batch_size': 16,
                    'learning_rate': 2e-5,
                    'num_epochs': 3
                },
                'deepfake_detection': {
                    'base_model': 'microsoft/resnet-50',
                    'num_labels': 2,
                    'batch_size': 8,
                    'learning_rate': 1e-4,
                    'num_epochs': 5
                }
            }

    def load_pretrained_model(self, task: str):
        """Load pre-trained model for specific task."""
        config = self.config[task]
        self.logger.info(f"Loading pretrained model for {task}")
        
        try:
            self.tokenizers[task] = AutoTokenizer.from_pretrained(config['base_model'])
            self.models[task] = AutoModelForSequenceClassification.from_pretrained(
                config['base_model'],
                num_labels=config['num_labels']
            ).to(self.device)
            
            self.logger.info(f"Successfully loaded model for {task}")
        except Exception as e:
            self.logger.error(f"Error loading model for {task}: {str(e)}")
            raise

    def prepare_training_args(self, task: str, output_dir: str) -> TrainingArguments:
        """Prepare training arguments for the model."""
        config = self.config[task]
        return TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=config['num_epochs'],
            per_device_train_batch_size=config['batch_size'],
            per_device_eval_batch_size=config['batch_size'],
            learning_rate=config['learning_rate'],
            weight_decay=0.01,
            logging_dir=f'{output_dir}/logs',
            logging_steps=100,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="accuracy"
        )

    def train_phishing_detector(self, train_texts: List[str], train_labels: List[int],
                              eval_texts: Optional[List[str]] = None,
                              eval_labels: Optional[List[int]] = None):
        """Fine-tune model for phishing detection."""
        task = 'phishing_detection'
        self.load_pretrained_model(task)
        
        # Prepare datasets
        train_encodings = self.tokenizers[task](train_texts, truncation=True, padding=True)
        train_dataset = PhishingDataset(train_encodings, train_labels)
        
        eval_dataset = None
        if eval_texts and eval_labels:
            eval_encodings = self.tokenizers[task](eval_texts, truncation=True, padding=True)
            eval_dataset = PhishingDataset(eval_encodings, eval_labels)
        
        # Setup training arguments
        training_args = self.prepare_training_args(task, f'models/{task}')
        
        # Initialize trainer
        trainer = Trainer(
            model=self.models[task],
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=self.compute_metrics
        )
        
        # Train the model
        self.logger.info("Starting phishing detector training")
        trainer.train()
        
        # Save the model
        self.save_model(task)

    def train_deepfake_detector(self, train_images: List[torch.Tensor], train_labels: List[int],
                              eval_images: Optional[List[torch.Tensor]] = None,
                              eval_labels: Optional[List[int]] = None):
        """Fine-tune model for deepfake detection."""
        task = 'deepfake_detection'
        self.load_pretrained_model(task)
        
        # Prepare datasets
        train_dataset = DeepfakeDataset(train_images, train_labels)
        eval_dataset = None
        if eval_images and eval_labels:
            eval_dataset = DeepfakeDataset(eval_images, eval_labels)
        
        # Setup training arguments
        training_args = self.prepare_training_args(task, f'models/{task}')
        
        # Initialize trainer
        trainer = Trainer(
            model=self.models[task],
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=self.compute_metrics
        )
        
        # Train the model
        self.logger.info("Starting deepfake detector training")
        trainer.train()
        
        # Save the model
        self.save_model(task)

    def save_model(self, task: str):
        """Save the trained model and tokenizer."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_dir = f'models/{task}/{timestamp}'
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            self.models[task].save_pretrained(save_dir)
            self.tokenizers[task].save_pretrained(save_dir)
            
            # Save model configuration
            with open(f'{save_dir}/config.json', 'w') as f:
                json.dump(self.config[task], f, indent=2)
            
            self.logger.info(f"Model saved successfully at {save_dir}")
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise

    def load_model(self, task: str, model_path: str):
        """Load a saved model."""
        try:
            self.models[task] = AutoModelForSequenceClassification.from_pretrained(model_path).to(self.device)
            self.tokenizers[task] = AutoTokenizer.from_pretrained(model_path)
            
            # Load model configuration
            with open(f'{model_path}/config.json', 'r') as f:
                self.config[task] = json.load(f)
            
            self.logger.info(f"Model loaded successfully from {model_path}")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise

    @staticmethod
    def compute_metrics(pred):
        """Compute evaluation metrics."""
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        
        accuracy = (preds == labels).mean()
        return {
            'accuracy': accuracy
        }

class PhishingDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

class DeepfakeDataset(torch.utils.data.Dataset):
    def __init__(self, images, labels):
        self.images = images
        self.labels = labels

    def __getitem__(self, idx):
        return {
            'pixel_values': self.images[idx],
            'labels': torch.tensor(self.labels[idx])
        }

    def __len__(self):
        return len(self.labels)
