import json
import os
import sqlite3
from datetime import datetime

class DataLineage:
    def __init__(self, storage_path='data_lineage.json'):
        self.lineage_data = {}
        self.storage_path = storage_path
        self.use_sqlite = storage_path.endswith('.db')
        self.load_lineage()

    def track_data_usage(self, data_id, user_id, purpose):
        if data_id not in self.lineage_data:
            self.lineage_data[data_id] = []
        
        entry = {
            "user": user_id,
            "purpose": purpose,
            "timestamp": datetime.now().isoformat()
        }
        self.lineage_data[data_id].append(entry)
        self.save_lineage()

    def get_data_history(self, data_id):
        return self.lineage_data.get(data_id, [])

    def save_lineage(self):
        if self.use_sqlite:
            self._save_to_sqlite()
        else:
            self._save_to_json()

    def load_lineage(self):
        if self.use_sqlite:
            self._load_from_sqlite()
        else:
            self._load_from_json()

    def _save_to_json(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.lineage_data, f, indent=2)

    def _load_from_json(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                self.lineage_data = json.load(f)

    def _save_to_sqlite(self):
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS data_lineage
                          (data_id TEXT, user_id TEXT, purpose TEXT, timestamp TEXT)''')
        cursor.execute('DELETE FROM data_lineage')  # Clear existing data
        for data_id, entries in self.lineage_data.items():
            for entry in entries:
                cursor.execute('INSERT INTO data_lineage VALUES (?, ?, ?, ?)',
                               (data_id, entry['user'], entry['purpose'], entry['timestamp']))
        conn.commit()
        conn.close()

    def _load_from_sqlite(self):
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        cursor.execute('SELECT data_id, user_id, purpose, timestamp FROM data_lineage')
        rows = cursor.fetchall()
        self.lineage_data = {}
        for row in rows:
            data_id, user_id, purpose, timestamp = row
            if data_id not in self.lineage_data:
                self.lineage_data[data_id] = []
            self.lineage_data[data_id].append({
                "user": user_id,
                "purpose": purpose,
                "timestamp": timestamp
            })
        conn.close()

    def generate_report(self, data_id=None):
        if data_id:
            return self._generate_single_report(data_id)
        else:
            return self._generate_full_report()

    def _generate_single_report(self, data_id):
        history = self.get_data_history(data_id)
        report = f"Data Lineage Report for {data_id}:\n"
        for entry in history:
            report += f"- User: {entry['user']}, Purpose: {entry['purpose']}, Time: {entry['timestamp']}\n"
        return report

    def _generate_full_report(self):
        report = "Full Data Lineage Report:\n"
        for data_id, history in self.lineage_data.items():
            report += f"\nData ID: {data_id}\n"
            for entry in history:
                report += f"- User: {entry['user']}, Purpose: {entry['purpose']}, Time: {entry['timestamp']}\n"
        return report

# Usage example
if __name__ == "__main__":
    # For JSON storage
    data_lineage_json = DataLineage(storage_path='data_lineage.json')
    
    # For SQLite storage
    data_lineage_sqlite = DataLineage(storage_path='data_lineage.db')

    # Track data usage
    for data_lineage in [data_lineage_json, data_lineage_sqlite]:
        data_lineage.track_data_usage("data123", "user456", "query")
        data_lineage.track_data_usage("data123", "user789", "analysis")

        # Get data history
        print(data_lineage.get_data_history("data123"))

        # Generate reports
        print(data_lineage.generate_report("data123"))
        print(data_lineage.generate_report())