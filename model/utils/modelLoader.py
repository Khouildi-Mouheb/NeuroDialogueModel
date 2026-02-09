"""
Model Loader Utility

Handles loading and caching of ML models
"""

import logging
from typing import Dict, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)


class ModelLoader:

    _model_cache: Dict[str, Any] = {}
    _tokenizer_cache: Dict[str, Any] = {}
    
    @classmethod
    def load_model(cls, model_name: str):
        """
        Load model (with caching)
        
        Args:
            model_name: HuggingFace model name
            
        Returns:
            Loaded model
        """
        if model_name not in cls._model_cache:
            logger.info(f"Loading model: {model_name}")
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            model.eval()
            cls._model_cache[model_name] = model
            logger.info(f"Model loaded: {model_name}")
        
        return cls._model_cache[model_name]
    
    @classmethod
    def load_tokenizer(cls, model_name: str):
        """
        Load tokenizer (with caching)
        
        Args:
            model_name: HuggingFace model name
            
        Returns:
            Loaded tokenizer
        """
        if model_name not in cls._tokenizer_cache:
            logger.info(f"Loading tokenizer: {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            cls._tokenizer_cache[model_name] = tokenizer
            logger.info(f"Tokenizer loaded: {model_name}")
        
        return cls._tokenizer_cache[model_name]
    
    @classmethod
    def clear_cache(cls):
        """Clear model cache (free memory)"""
        logger.info("Clearing model cache")
        cls._model_cache.clear()
        cls._tokenizer_cache.clear()