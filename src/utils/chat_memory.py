from collections import deque
import json
import os
import sqlite3

class ChatMemory:
    def __init__(self, max_history=10, storage_path='chat_memory.json'):
        self.max_history = max_history
        self.storage_path = storage_path
        self.use_sqlite = storage_path.endswith('.db')
        self.memory = {}
        self.load_memory()

    def add_interaction(self, user_id, query, response):
        if user_id not in self.memory:
            self.memory[user_id] = deque(maxlen=self.max_history)
        self.memory[user_id].append({"query": query, "response": response})
        self.save_memory()

    def get_history(self, user_id):
        return list(self.memory.get(user_id, []))

    def clear_history(self, user_id):
        if user_id in self.memory:
            del self.memory[user_id]
            self.save_memory()

    def save_memory(self):
        if self.use_sqlite:
            self._save_to_sqlite()
        else:
            self._save_to_json()

    def load_memory(self):
        if self.use_sqlite:
            self._load_from_sqlite()
        else:
            self._load_from_json()

    def _save_to_json(self):
        with open(self.storage_path, 'w') as f:
            json.dump({user: list(history) for user, history in self.memory.items()}, f)

    def _load_from_json(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                loaded_memory = json.load(f)
                self.memory = {user: deque(history, maxlen=self.max_history) for user, history in loaded_memory.items()}

    def _save_to_sqlite(self):
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_memory
                          (user_id TEXT, query TEXT, response TEXT)''')
        cursor.execute('DELETE FROM chat_memory')  # Clear existing data
        for user_id, history in self.memory.items():
            for interaction in history:
                cursor.execute('INSERT INTO chat_memory VALUES (?, ?, ?)',
                               (user_id, interaction['query'], interaction['response']))
        conn.commit()
        conn.close()

    def _load_from_sqlite(self):
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, query, response FROM chat_memory')
        rows = cursor.fetchall()
        for row in rows:
            user_id, query, response = row
            if user_id not in self.memory:
                self.memory[user_id] = deque(maxlen=self.max_history)
            self.memory[user_id].append({"query": query, "response": response})
        conn.close()

# Usage example
if __name__ == "__main__":
    # For JSON storage
    chat_memory_json = ChatMemory(storage_path='chat_memory.json')
    
    # For SQLite storage
    chat_memory_sqlite = ChatMemory(storage_path='chat_memory.db')

    # Add interactions
    for chat_memory in [chat_memory_json, chat_memory_sqlite]:
        chat_memory.add_interaction("user123", "Hello", "Hi there!")
        chat_memory.add_interaction("user123", "How are you?", "I'm doing well, thank you!")

        # Get history
        print(chat_memory.get_history("user123"))

        # Clear history
        chat_memory.clear_history("user123")
        print(chat_memory.get_history("user123"))  # Should be empty