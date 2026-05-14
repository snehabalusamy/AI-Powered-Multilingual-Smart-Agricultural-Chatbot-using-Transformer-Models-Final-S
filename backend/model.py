import json
import os
import sys
import io
import logging
from langdetect import detect
from sentence_transformers import SentenceTransformer, util
import torch

# Fix Windows console encoding for Unicode output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ChatbotModel:
    def __init__(self, knowledge_base_path="data/knowledge_base.json"):
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        self.patterns = []
        self.responses = {}
        self.tags = []
        self.pattern_embeddings = None
        self._prepare_data()

    def load_knowledge_base(self, path):
        # Adjust path to be relative to where the script is run or absolute
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            # Fallback for running from backend dir
            abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', path))
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _prepare_data(self):
        for intent in self.knowledge_base['intents']:
            for pattern in intent['patterns']:
                self.patterns.append(pattern)
                self.tags.append(intent['tag'])
            self.responses[intent['tag']] = intent['responses']
        
        # Compute embeddings for all patterns
        logger.info(f"[ChatbotModel] Encoding {len(self.patterns)} patterns across {len(self.responses)} intents...")
        self.pattern_embeddings = self.model.encode(self.patterns, convert_to_tensor=True)
        logger.info(f"[ChatbotModel] Ready! Pattern embeddings shape: {self.pattern_embeddings.shape}")

    # Supported languages in our knowledge base
    SUPPORTED_LANGS = {'en', 'ta', 'hi', 'te', 'kn'}

    def detect_language(self, text):
        try:
            lang = detect(text)
            # langdetect sometimes returns incorrect codes for short text
            lang_map = {
                'mr': 'hi',  # Marathi often confused with Hindi
            }
            lang = lang_map.get(lang, lang)
            # If detected language is not supported, default to English
            # This handles transliterated text (e.g. "payir vagaigal" detected as Lithuanian)
            if lang not in self.SUPPORTED_LANGS:
                return "en"
            return lang
        except:
            return "en"

    def get_response(self, query):
        # Detect language
        lang = self.detect_language(query)
        
        # Safe debug logging (handles Unicode on Windows)
        try:
            logger.info(f"\n[Query] '{query}' | Detected language: {lang}")
        except Exception:
            logger.info(f"\n[Query] (non-ascii text) | Detected language: {lang}")
        
        # Encode user query
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # Compute cosine similarity
        cosine_scores = util.cos_sim(query_embedding, self.pattern_embeddings)[0]
        
        # Get top 3 matches for debugging
        top_k = min(3, len(cosine_scores))
        top_scores, top_indices = torch.topk(cosine_scores, top_k)
        
        try:
            logger.info("[Top matches]:")
            for i in range(top_k):
                idx = top_indices[i].item()
                score = top_scores[i].item()
                logger.info(f"  {i+1}. [{self.tags[idx]}] '{self.patterns[idx]}' (score: {score:.4f})")
        except Exception:
            # If logging fails due to encoding, just log the scores
            for i in range(top_k):
                idx = top_indices[i].item()
                score = top_scores[i].item()
                logger.info(f"  {i+1}. [{self.tags[idx]}] (score: {score:.4f})")
        
        # Find best match
        best_match_idx = top_indices[0].item()
        best_score = top_scores[0].item()
        
        # Use a stricter threshold for relevance
        if best_score < 0.4:
            logger.info(f"[Result] Below threshold ({best_score:.4f} < 0.4) -> fallback response")
            
            # Provide a language-appropriate fallback
            fallback_responses = {
                "en": "I'm sorry, I didn't understand that. Please ask me about crops, fertilizers, pest control, irrigation, or government schemes.",
                "ta": "\u0bae\u0ba9\u0bcd\u0ba9\u0bbf\u0b95\u0bcd\u0b95\u0bb5\u0bc1\u0bae\u0bcd, \u0baa\u0bc1\u0bb0\u0bbf\u0baf\u0bb5\u0bbf\u0bb2\u0bcd\u0bb2\u0bc8. \u0baa\u0baf\u0bbf\u0bb0\u0bcd\u0b95\u0bb3\u0bcd, \u0b89\u0bb0\u0b99\u0bcd\u0b95\u0bb3\u0bcd, \u0baa\u0bc2\u0b9a\u0bcd\u0b9a\u0bbf \u0b95\u0b9f\u0bcd\u0b9f\u0bc1\u0baa\u0bcd\u0baa\u0bbe\u0b9f\u0bc1, \u0ba8\u0bc0\u0bb0\u0bcd \u0baa\u0bbe\u0b9a\u0ba9\u0bae\u0bcd \u0b85\u0bb2\u0bcd\u0bb2\u0ba4\u0bc1 \u0b85\u0bb0\u0b9a\u0bc1 \u0ba4\u0bbf\u0b9f\u0bcd\u0b9f\u0b99\u0bcd\u0b95\u0bb3\u0bcd \u0baa\u0bb1\u0bcd\u0bb1\u0bbf \u0b95\u0bc7\u0bb3\u0bc1\u0b99\u0bcd\u0b95\u0bb3\u0bcd.",
                "hi": "\u0915\u094d\u0937\u092e\u093e \u0915\u0930\u0947\u0902, \u092e\u0941\u091d\u0947 \u0938\u092e\u091d \u0928\u0939\u0940\u0902 \u0906\u092f\u093e\u0964 \u0915\u0943\u092a\u092f\u093e \u092b\u0938\u0932\u094b\u0902, \u0909\u0930\u094d\u0935\u0930\u0915\u094b\u0902, \u0915\u0940\u091f \u0928\u093f\u092f\u0902\u0924\u094d\u0930\u0923, \u0938\u093f\u0902\u091a\u093e\u0908, \u092f\u093e \u0938\u0930\u0915\u093e\u0930\u0940 \u092f\u094b\u091c\u0928\u093e\u0913\u0902 \u0915\u0947 \u092c\u093e\u0930\u0947 \u092e\u0947\u0902 \u092a\u0942\u091b\u0947\u0902\u0964",
                "te": "\u0c15\u0c4d\u0c37\u0c2e\u0c3f\u0c02\u0c1a\u0c02\u0c21\u0c3f, \u0c28\u0c3e\u0c15\u0c41 \u0c05\u0c30\u0c4d\u0c25\u0c02 \u0c15\u0c3e\u0c32\u0c47\u0c26\u0c41. \u0c26\u0c2f\u0c1a\u0c47\u0c38\u0c3f \u0c2a\u0c02\u0c1f\u0c32\u0c41, \u0c0e\u0c30\u0c41\u0c35\u0c41\u0c32\u0c41, \u0c2a\u0c41\u0c30\u0c41\u0c17\u0c41\u0c32 \u0c28\u0c3f\u0c2f\u0c02\u0c24\u0c4d\u0c30\u0c23 \u0c32\u0c47\u0c26\u0c3e \u0c2a\u0c4d\u0c30\u0c2d\u0c41\u0c24\u0c4d\u0c35 \u0c2a\u0c25\u0c15\u0c3e\u0c32 \u0c17\u0c41\u0c30\u0c3f\u0c02\u0c1a\u0c3f \u0c05\u0c21\u0c17\u0c02\u0c21\u0c3f.",
                "kn": "\u0c95\u0ccd\u0cb7\u0cae\u0cbf\u0cb8\u0cbf, \u0ca8\u0ca8\u0c97\u0cc6 \u0c85\u0cb0\u0ccd\u0ca5\u0cb5\u0cbe\u0c97\u0cb2\u0cbf\u0cb2\u0ccd\u0cb2. \u0ca6\u0caf\u0cb5\u0cbf\u0c9f\u0ccd\u0c9f\u0cc1 \u0cac\u0cc6\u0cb3\u0cc6\u0c97\u0cb3\u0cc1, \u0c97\u0cca\u0cac\u0ccd\u0cac\u0cb0, \u0c95\u0cc0\u0c9f \u0ca8\u0cbf\u0caf\u0c82\u0ca4\u0ccd\u0cb0\u0ca3, \u0c85\u0ca5\u0cb5\u0cbe \u0cb8\u0cb0\u0ccd\u0c95\u0cbe\u0cb0\u0cbf \u0caf\u0ccb\u0c9c\u0ca8\u0cc6\u0c97\u0cb3 \u0cac\u0c97\u0ccd\u0c97\u0cc6 \u0c95\u0cc7\u0cb3\u0cbf."
            }
            
            return {
                "response": fallback_responses.get(lang, fallback_responses["en"]),
                "language": lang,
                "confidence": round(best_score, 4),
                "intent": "unknown"
            }
        
        best_tag = self.tags[best_match_idx]
        responses = self.responses[best_tag]
        
        # Return response in detected language, fallback to English
        response_text = responses.get(lang, responses.get('en', "Response not available in this language."))
        
        logger.info(f"[Result] Intent: {best_tag} | Score: {best_score:.4f} | Response lang: {lang}")
        
        return {
            "response": response_text,
            "language": lang,
            "confidence": round(best_score, 4),
            "intent": best_tag
        }

# Global instance
chatbot = ChatbotModel()
