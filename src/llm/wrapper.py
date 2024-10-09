import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Dict, Any
import numpy as np

class LLMWrapper:
    def __init__(self):
        self.model_name = os.environ.get("LLM_MODEL_NAME", "EleutherAI/gpt-neo-1.3B")
        self.model_version = "1.0"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Loading LLM model: {self.model_name} on {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)

    def generate_response(self, prompt: str, context: str = "", max_length: int = 100) -> str:
        full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"
        inputs = self.tokenizer.encode(full_prompt, return_tensors="pt").to(self.device)
        
        attention_mask = torch.ones(inputs.shape, dtype=torch.long, device=self.device)
        outputs = self.model.generate(
            inputs,
            max_length=max_length,
            num_return_sequences=1,
            attention_mask=attention_mask,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("Answer:")[-1].strip()

    def analyze_sentiment(self, text: str) -> float:
        # This is a placeholder for sentiment analysis
        # In a real implementation, you would use a pre-trained sentiment analysis model
        # or a more sophisticated method
        positive_words = set(['good', 'great', 'excellent', 'positive', 'wonderful', 'fantastic'])
        negative_words = set(['bad', 'poor', 'negative', 'terrible', 'awful', 'horrible'])
        
        words = text.lower().split()
        sentiment_score = sum(1 for word in words if word in positive_words) - sum(1 for word in words if word in negative_words)
        return sentiment_score / len(words) if words else 0

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Generate embeddings for a list of texts
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        
        # Use the mean of the last hidden state as the embedding
        embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        return embeddings.tolist()

    def semantic_search(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.get_embeddings([query])[0]
        doc_embeddings = self.get_embeddings(documents)
        
        # Compute cosine similarity
        similarities = np.dot(doc_embeddings, query_embedding) / (np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding))
        
        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = [
            {"document": documents[i], "similarity": float(similarities[i])}
            for i in top_indices
        ]
        
        return results

    def summarize(self, text: str, max_length: int = 150) -> str:
        inputs = self.tokenizer.encode("Summarize: " + text, return_tensors="pt", max_length=1024, truncation=True).to(self.device)
        summary_ids = self.model.generate(inputs, max_length=max_length, num_return_sequences=1, length_penalty=2.0, min_length=30)
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

if __name__ == "__main__":
    # Example usage
    llm = LLMWrapper()
    response = llm.generate_response("What is the capital of France?")
    print("Response:", response)
    
    sentiment = llm.analyze_sentiment("This is a great day!")
    print("Sentiment:", sentiment)
    
    documents = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is a subset of artificial intelligence.",
        "Python is a popular programming language for data science."
    ]
    query = "artificial intelligence"
    search_results = llm.semantic_search(query, documents)
    print("Semantic Search Results:", search_results)
    
    summary = llm.summarize("Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. Leading AI textbooks define the field as the study of 'intelligent agents': any system that perceives its environment and takes actions that maximize its chance of achieving its goals. Some popular accounts use the term 'artificial intelligence' to describe machines that mimic 'cognitive' functions that humans associate with the human mind, such as 'learning' and 'problem solving', however this definition is rejected by major AI researchers.")
    print("Summary:", summary)