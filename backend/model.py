import json
import os
from langdetect import detect
from sentence_transformers import SentenceTransformer, util
import torch

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
        self.pattern_embeddings = self.model.encode(self.patterns, convert_to_tensor=True)

    def detect_language(self, text):
        try:
            return detect(text)
        except:
            return "en"

    def get_response(self, query):
        # Detect language
        lang = self.detect_language(query)
        
        # Apply autocorrection if it is English to handle typos
        if lang == 'en':
            from textblob import TextBlob
            query = str(TextBlob(query).correct())
            print(f"Corrected query: {query}") # For debugging
        
        # Encode user query
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # Compute cosine similarity
        cosine_scores = util.cos_sim(query_embedding, self.pattern_embeddings)[0]
        
        # Find best match
        best_match_idx = torch.argmax(cosine_scores).item()
        best_score = cosine_scores[best_match_idx].item()
        
        # Threshold for relevance
        if best_score < 0.3:
            return {
                "response": "I'm sorry, I didn't understand that. Please ask something about crops, fertilizers, or government schemes.",
                "language": lang,
                "confidence": best_score,
                "intent": "unknown"
            }
        
        best_tag = self.tags[best_match_idx]
        responses = self.responses[best_tag]
        
        # Return response in detected language, fallback to English
        response_text = responses.get(lang, responses.get('en', "Response not available in this language."))
        
        return {
            "response": response_text,
            "language": lang,
            "confidence": best_score,
            "intent": best_tag
        }

# Global instance
chatbot = ChatbotModel()
