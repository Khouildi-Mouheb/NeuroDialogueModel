# save_all_models.py
import os
import pickle
import json
import torch
from datetime import datetime
from transformers import pipeline, AutoModel, AutoTokenizer
from sentence_transformers import SentenceTransformer

class ModelSaver:
    def __init__(self, save_dir: str = "saved_models"):
        """
        Save all your models locally for offline use.
        
        Args:
            save_dir: Directory to save all models
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # Create subdirectories
        self.dirs = {
            'emotion': os.path.join(save_dir, 'bert_base_go_emotion'),
            'intent': os.path.join(save_dir, 'bart_large_mnli_intent'),
            'needs': os.path.join(save_dir, 'bart_large_mnli_needs'),
            'embedding': os.path.join(save_dir, 'all_minilm_l6_v2'),
            'metadata': os.path.join(save_dir, 'metadata')
        }
        
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def save_emotion_model(self):
        """Save bhadresh-savani/bert-base-go-emotion"""
        print("💾 Saving emotion model (bert-base-go-emotion)...")
        
        # Load model and tokenizer
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        
        model_name = "bhadresh-savani/bert-base-go-emotion"
        
        # Load
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Save locally
        model.save_pretrained(self.dirs['emotion'])
        tokenizer.save_pretrained(self.dirs['emotion'])
        
        # Save pipeline config
        pipeline_config = {
            "task": "text-classification",
            "model": model_name,
            "framework": "pt",
            "num_labels": model.config.num_labels
        }
        
        with open(os.path.join(self.dirs['emotion'], 'pipeline_config.json'), 'w') as f:
            json.dump(pipeline_config, f, indent=2)
        
        print(f"✅ Emotion model saved to: {self.dirs['emotion']}")
        return self.dirs['emotion']
    
    def save_intent_classifier(self):
        """Save facebook/bart-large-mnli for intent classification"""
        print("💾 Saving intent classifier (bart-large-mnli)...")
        
        # Create the pipeline first
        intent_pipeline = pipeline(
            "text-classification", 
            model="facebook/bart-large-mnli"
        )
        
        # Get the actual model and tokenizer from the pipeline
        model = intent_pipeline.model
        tokenizer = intent_pipeline.tokenizer
        
        # Save model
        model.save_pretrained(self.dirs['intent'])
        tokenizer.save_pretrained(self.dirs['intent'])
        
        # Save pipeline info
        pipeline_info = {
            "task": "text-classification",
            "model": "facebook/bart-large-mnli",
            "purpose": "intent_classification",
            "framework": "pt"
        }
        
        with open(os.path.join(self.dirs['intent'], 'pipeline_info.json'), 'w') as f:
            json.dump(pipeline_info, f, indent=2)
        
        print(f"✅ Intent classifier saved to: {self.dirs['intent']}")
        return self.dirs['intent']
    
    def save_needs_classifier(self):
        """Save facebook/bart-large-mnli for zero-shot classification"""
        print("💾 Saving needs classifier (bart-large-mnli zero-shot)...")
        
        # Create the pipeline
        needs_pipeline = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli"
        )
        
        # Get model and tokenizer
        model = needs_pipeline.model
        tokenizer = needs_pipeline.tokenizer
        
        # Save model
        model.save_pretrained(self.dirs['needs'])
        tokenizer.save_pretrained(self.dirs['needs'])
        
        # Save zero-shot specific config
        zs_config = {
            "task": "zero-shot-classification",
            "model": "facebook/bart-large-mnli",
            "purpose": "needs_classification",
            "framework": "pt",
            "multi_label": True
        }
        
        with open(os.path.join(self.dirs['needs'], 'zero_shot_config.json'), 'w') as f:
            json.dump(zs_config, f, indent=2)
        
        print(f"✅ Needs classifier saved to: {self.dirs['needs']}")
        return self.dirs['needs']
    
    def save_embedding_model(self):
        """Save sentence-transformers/all-MiniLM-L6-v2"""
        print("💾 Saving embedding model (all-MiniLM-L6-v2)...")
        
        # Load model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Save using sentence-transformers method
        model.save(self.dirs['embedding'])
        
        # Also save as transformers format for compatibility
        model.save_pretrained(self.dirs['embedding'])
        
        # Save model info
        model_info = {
            "model_name": "all-MiniLM-L6-v2",
            "embedding_dim": model.get_sentence_embedding_dimension(),
            "max_seq_length": model.max_seq_length,
            "framework": "sentence-transformers"
        }
        
        with open(os.path.join(self.dirs['embedding'], 'model_info.json'), 'w') as f:
            json.dump(model_info, f, indent=2)
        
        print(f"✅ Embedding model saved to: {self.dirs['embedding']}")
        return self.dirs['embedding']
    
    def save_metadata(self):
        """Save metadata about all models"""
        print("📄 Saving metadata...")
        
        metadata = {
            "version": "1.0.0",
            "saved_date": datetime.now().isoformat(),
            "models": {
                "emotion_model": {
                    "name": "bhadresh-savani/bert-base-go-emotion",
                    "type": "text-classification",
                    "path": self.dirs['emotion'],
                    "labels": 28  # go-emotion has 28 emotions
                },
                "intent_classifier": {
                    "name": "facebook/bart-large-mnli",
                    "type": "text-classification",
                    "path": self.dirs['intent'],
                    "purpose": "intent_detection"
                },
                "needs_classifier": {
                    "name": "facebook/bart-large-mnli",
                    "type": "zero-shot-classification", 
                    "path": self.dirs['needs'],
                    "purpose": "needs_detection"
                },
                "embedding_model": {
                    "name": "all-MiniLM-L6-v2",
                    "type": "sentence-embedding",
                    "path": self.dirs['embedding'],
                    "dimensions": 384
                }
            },
            "requirements": {
                "transformers": ">=4.30.0",
                "sentence-transformers": ">=2.2.2",
                "torch": ">=2.0.0",
                "python": ">=3.8"
            },
            "total_size_mb": self._calculate_total_size()
        }
        
        metadata_file = os.path.join(self.dirs['metadata'], 'models_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Metadata saved to: {metadata_file}")
        return metadata_file
    
    def _calculate_total_size(self):
        """Calculate total size of saved models in MB"""
        total_size = 0
        for dir_path in [self.dirs[k] for k in ['emotion', 'intent', 'needs', 'embedding']]:
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
        return round(total_size / (1024 * 1024), 2)  # MB
    
    def save_all(self):
        """Save all models in sequence"""
        print("=" * 60)
        print("🚀 STARTING MODEL SAVE PROCESS")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Save all models
        emotion_path = self.save_emotion_model()
        intent_path = self.save_intent_classifier()
        needs_path = self.save_needs_classifier()
        embedding_path = self.save_embedding_model()
        
        # Save metadata
        metadata_path = self.save_metadata()
        
        # Calculate time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("=" * 60)
        print("✅ ALL MODELS SAVED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📁 Save directory: {self.save_dir}")
        print(f"📊 Total size: {self._calculate_total_size()} MB")
        print(f"⏱️  Time taken: {duration:.2f} seconds")
        print(f"📍 Model paths:")
        print(f"   - Emotion: {emotion_path}")
        print(f"   - Intent: {intent_path}")
        print(f"   - Needs: {needs_path}")
        print(f"   - Embedding: {embedding_path}")
        print(f"   - Metadata: {metadata_path}")
        print("=" * 60)
        
        return {
            'emotion': emotion_path,
            'intent': intent_path,
            'needs': needs_path,
            'embedding': embedding_path,
            'metadata': metadata_path
        }

def main():
    """Main function to save all models"""
    
    # Initialize saver
    saver = ModelSaver(save_dir="my_saved_models")
    
    # Save all models
    try:
        paths = saver.save_all()
        
        # Print usage instructions
        print("\n📖 HOW TO USE SAVED MODELS:")
        print("1. Emotion model:")
        print('   from transformers import pipeline')
        print('   emotion_pipeline = pipeline("text-classification", model="my_saved_models/bert_base_go_emotion")')
        
        print("\n2. Intent classifier:")
        print('   intent_pipeline = pipeline("text-classification", model="my_saved_models/bart_large_mnli_intent")')
        
        print("\n3. Needs classifier:")
        print('   needs_pipeline = pipeline("zero-shot-classification", model="my_saved_models/bart_large_mnli_needs")')
        
        print("\n4. Embedding model:")
        print('   from sentence_transformers import SentenceTransformer')
        print('   embedder = SentenceTransformer("my_saved_models/all_minilm_l6_v2")')
        
    except Exception as e:
        print(f"❌ Error saving models: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()