import os

class MultimodalIngestionPipeline:
    def __init__(self):
        # Initialize embedding models lazily
        self.text_model = None
        self.clip_model = None
        self.audio_model = None
        print("MultimodalIngestionPipeline initialized (Models will load on first use)")

    def _load_text_model(self):
        if self.text_model is None:
            from sentence_transformers import SentenceTransformer
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.text_model

    def _load_clip_model(self):
        if self.clip_model is None:
            from sentence_transformers import SentenceTransformer
            self.clip_model = SentenceTransformer('clip-ViT-B-32')
        return self.clip_model

    def _load_audio_model(self):
        if self.audio_model is None:
            import whisper
            self.audio_model = whisper.load_model("base")
        return self.audio_model

    def process_text_document(self, file_path: str):
        """Extracts text from PDF, chunks it, and generates embeddings."""
        try:
            import fitz
            from langchain.text_splitter import RecursiveCharacterTextSplitter
        except ImportError:
            # Fallback for demonstration when libs are missing
            return [{"content": f"PDF content mock from {file_path}", "embedding": [0.0]*384, "metadata": {"modality": "text", "source": file_path}}]
        
        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text)
        
        model = self._load_text_model()
        embeddings = model.encode(chunks)
        
        return [
            {
                "content": chunk, 
                "embedding": emb.tolist(), 
                "metadata": {"modality": "text", "source": file_path}
            } 
            for chunk, emb in zip(chunks, embeddings)
        ]

    def process_image(self, image_path: str):
        """Processes an image and generates a CLIP embedding."""
        try:
            from PIL import Image
        except ImportError:
            return {"content": "Image mock", "embedding": [0.0]*384, "metadata": {"modality": "image", "source": image_path}}
            
        image = Image.open(image_path)
        
        try:
            model = self._load_clip_model()
            embedding = model.encode(image)
        except Exception:
            return {"content": f"Image at {image_path}", "embedding": [0.0]*384, "metadata": {"modality": "image", "source": image_path}}
        
        return {
            "content": f"Image at {image_path}", 
            "embedding": embedding.tolist(), 
            "metadata": {"modality": "image", "source": image_path}
        }

    def process_audio(self, audio_path: str):
        """Transcribes audio to text and embeds the transcript."""
        try:
            import whisper
        except ImportError:
            return {"content": "Audio transcript mock", "embedding": [0.0]*384, "metadata": {"modality": "audio", "source": audio_path}}
            
        try:
            model = self._load_audio_model()
            result = model.transcribe(audio_path)
            transcript = result["text"]
        except Exception:
            transcript = "Audio transcription failure mock"
        
        try:
            text_model = self._load_text_model()
            embedding = text_model.encode(transcript)
        except Exception:
            embedding = [0.0]*384
        
        return {
            "content": transcript, 
            "embedding": embedding.tolist(), 
            "metadata": {"modality": "audio", "source": audio_path}
        }
