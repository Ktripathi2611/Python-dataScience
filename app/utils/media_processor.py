import cv2
import numpy as np
from PIL import Image
import torch
import librosa

def extract_frames(video_path, max_frames=30):
    """
    Extract frames from video file.
    
    Args:
        video_path (str): Path to video file
        max_frames (int): Maximum number of frames to extract
        
    Returns:
        list: List of extracted frames as PIL Images
    """
    try:
        cap = cv2.VideoCapture(video_path)
        frames = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame interval to get evenly spaced frames
        interval = max(1, total_frames // max_frames)
        
        for i in range(0, total_frames, interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)
            
            if len(frames) >= max_frames:
                break
        
        cap.release()
        return frames
    except Exception as e:
        print(f"Error extracting frames: {str(e)}")
        return []

def process_audio(audio_path):
    """
    Process audio file for analysis.
    
    Args:
        audio_path (str): Path to audio file
        
    Returns:
        dict: Processed audio features
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_path)
        
        # Extract features
        features = {
            'mfcc': librosa.feature.mfcc(y=y, sr=sr),
            'spectral_centroids': librosa.feature.spectral_centroid(y=y, sr=sr),
            'spectral_rolloff': librosa.feature.spectral_rolloff(y=y, sr=sr),
            'zero_crossing_rate': librosa.feature.zero_crossing_rate(y),
            'tempo': librosa.beat.tempo(y=y, sr=sr)
        }
        
        # Convert features to numpy arrays
        processed_features = {}
        for key, value in features.items():
            if isinstance(value, np.ndarray):
                processed_features[key] = value.mean(axis=1) if value.ndim > 1 else value
            else:
                processed_features[key] = np.array(value)
        
        return processed_features
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return {}

def resize_image(image, target_size=(224, 224)):
    """
    Resize image to target size.
    
    Args:
        image (PIL.Image): Input image
        target_size (tuple): Target size (width, height)
        
    Returns:
        PIL.Image: Resized image
    """
    return image.resize(target_size, Image.Resampling.LANCZOS)

def normalize_image(image_tensor):
    """
    Normalize image tensor.
    
    Args:
        image_tensor (torch.Tensor): Input image tensor
        
    Returns:
        torch.Tensor: Normalized image tensor
    """
    mean = torch.tensor([0.485, 0.456, 0.406])
    std = torch.tensor([0.229, 0.224, 0.225])
    
    return (image_tensor - mean[:, None, None]) / std[:, None, None]

def extract_image_metadata(image):
    """
    Extract metadata from image.
    
    Args:
        image (PIL.Image): Input image
        
    Returns:
        dict: Image metadata
    """
    return {
        'format': image.format,
        'mode': image.mode,
        'size': image.size,
        'info': image.info
    }

def detect_face_landmarks(image):
    """
    Detect facial landmarks in image.
    
    Args:
        image (numpy.ndarray): Input image in BGR format
        
    Returns:
        list: Detected facial landmarks
    """
    try:
        # Initialize face detector and landmark predictor
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        landmarks = []
        for (x, y, w, h) in faces:
            # Get face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Add basic facial features
            landmarks.append({
                'face_position': (x, y, w, h),
                'center': (x + w//2, y + h//2),
                'confidence': 1.0  # placeholder for actual confidence score
            })
        
        return landmarks
    except Exception as e:
        print(f"Error detecting facial landmarks: {str(e)}")
        return []
