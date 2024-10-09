from __future__ import annotations
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from scipy import stats
from .monitoring_agent import MonitoringAgent

class BiasType:
    def __init__(self, name: str, threshold: float, interpretations: List[Tuple[Tuple[float, float], str]]):
        self.name = name
        self.threshold = threshold
        self.interpretations = interpretations

    def interpret(self, value: float) -> str:
        for (lower, upper), interpretation in self.interpretations:
            if lower <= value < upper:
                return interpretation
        return "Interpretation not available"

class BiasManagementMasterAgent:
    def __init__(self, threshold: float, storage_path: str = 'bias_metrics.db'):
        self.threshold = threshold
        self.storage_path = storage_path
        self.bias_metrics: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.bias_types: Dict[str, BiasType] = self._initialize_bias_types()
        self.load_metrics()
        self.monitoring_agent = MonitoringAgent(self)

    def _initialize_bias_types(self) -> Dict[str, BiasType]:
        return {
            "skill_bias": BiasType("skill_bias", 0.2, [
                ((0, 0.1), "Low skill bias"),
                ((0.1, 0.2), "Moderate skill bias"),
                ((0.2, 1), "High skill bias")
            ]),
            "gender_bias": BiasType("gender_bias", 0.15, [
                ((0, 0.05), "Low gender bias"),
                ((0.05, 0.15), "Moderate gender bias"),
                ((0.15, 1), "High gender bias")
            ]),
            "experience_bias": BiasType("experience_bias", 0.25, [
                ((0, 0.1), "Low experience bias"),
                ((0.1, 0.25), "Moderate experience bias"),
                ((0.25, 1), "High experience bias")
            ]),
            "cultural_bias": BiasType("cultural_bias", 0.2, [
                ((0, 0.1), "Low cultural bias"),
                ((0.1, 0.2), "Moderate cultural bias"),
                ((0.2, 1), "High cultural bias")
            ]),
            "workload_bias": BiasType("workload_bias", 0.3, [
                ((0, 0.15), "Low workload bias"),
                ((0.15, 0.3), "Moderate workload bias"),
                ((0.3, 1), "High workload bias")
            ])
        }

    def record_bias_metric(self, model_version: str, metric_name: str, value: float, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        if model_version not in self.bias_metrics:
            self.bias_metrics[model_version] = {}
        if metric_name not in self.bias_metrics[model_version]:
            self.bias_metrics[model_version][metric_name] = []
        
        entry = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        self.bias_metrics[model_version][metric_name].append(entry)
        self.save_metrics()

        if self.check_threshold(metric_name, value):
            return f"Alert: {metric_name} for {model_version} exceeded threshold. Value: {value}"
        return None

    def check_threshold(self, metric_name: str, value: float) -> bool:
        bias_type = self.bias_types.get(metric_name)
        if not bias_type:
            return False
        
        interpretation = bias_type.interpret(value)
        print(f"{metric_name} interpretation: {interpretation}")
        
        return value > bias_type.threshold

    def get_bias_metrics(self, model_version: str) -> Dict[str, List[Dict[str, Any]]]:
        return self.bias_metrics.get(model_version, {})

    def save_metrics(self) -> None:
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS bias_metrics
                          (model_version TEXT, metric_name TEXT, value REAL, timestamp TEXT, context TEXT)''')
        cursor.execute('DELETE FROM bias_metrics')  # Clear existing data
        for model_version, metrics in self.bias_metrics.items():
            for metric_name, entries in metrics.items():
                for entry in entries:
                    cursor.execute('INSERT INTO bias_metrics VALUES (?, ?, ?, ?, ?)',
                                   (model_version, metric_name, entry['value'], entry['timestamp'], json.dumps(entry['context'])))
        conn.commit()
        conn.close()

    def load_metrics(self) -> None:
        conn = sqlite3.connect(self.storage_path)
        cursor = conn.cursor()
        cursor.execute('SELECT model_version, metric_name, value, timestamp, context FROM bias_metrics')
        rows = cursor.fetchall()
        self.bias_metrics = {}
        for row in rows:
            model_version, metric_name, value, timestamp, context = row
            if model_version not in self.bias_metrics:
                self.bias_metrics[model_version] = {}
            if metric_name not in self.bias_metrics[model_version]:
                self.bias_metrics[model_version][metric_name] = []
            self.bias_metrics[model_version][metric_name].append({
                "value": value,
                "timestamp": timestamp,
                "context": json.loads(context)
            })
        conn.close()

    def analyze_trends(self, model_version: str, metric_name: str) -> str:
        metrics = self.get_bias_metrics(model_version)
        if metric_name not in metrics:
            return f"No data available for metric '{metric_name}' in model version {model_version}"
        
        values = [entry['value'] for entry in metrics[metric_name]]
        avg_value = np.mean(values)
        max_value = np.max(values)
        min_value = np.min(values)
        std_dev = np.std(values)
        
        t_statistic, p_value = stats.ttest_1samp(values, 0)
        
        interpretation = self.bias_types[metric_name].interpret(avg_value)
        
        return f"""Trend Analysis for '{metric_name}' in model version {model_version}:
Average: {avg_value:.4f} - {interpretation}
Standard Deviation: {std_dev:.4f}
Maximum: {max_value:.4f}
Minimum: {min_value:.4f}
Number of records: {len(values)}
T-statistic: {t_statistic:.4f}
P-value: {p_value:.4f}"""

    def calculate_overall_bias_score(self, task_allocation: Dict[str, Any]) -> float:
        bias_scores = []
        for bias_type, bias_value in task_allocation.get('bias_metrics', {}).items():
            if bias_type in self.bias_types:
                normalized_value = bias_value / self.bias_types[bias_type].threshold
                bias_scores.append(normalized_value)
        
        if not bias_scores:
            return 0.0
        
        return np.mean(bias_scores)

    def suggest_bias_mitigation(self, task_allocation: Dict[str, Any]) -> List[str]:
        suggestions = []
        for bias_type, bias_value in task_allocation.get('bias_metrics', {}).items():
            if bias_type in self.bias_types and bias_value > self.bias_types[bias_type].threshold:
                if bias_type == "skill_bias":
                    suggestions.append("Consider providing additional training or mentoring to balance skill levels.")
                elif bias_type == "gender_bias":
                    suggestions.append("Review task allocation process for potential gender biases and consider implementing blind allocation techniques.")
                elif bias_type == "experience_bias":
                    suggestions.append("Mix experienced team members with less experienced ones for knowledge transfer and balanced workload.")
                elif bias_type == "cultural_bias":
                    suggestions.append("Promote cultural awareness and diversity in team composition and task allocation.")
                elif bias_type == "workload_bias":
                    suggestions.append("Redistribute tasks to ensure a more balanced workload across team members.")
        
        return suggestions

    def bias_aware_task_allocation(self, task: Dict[str, Any], team_members: List[Dict[str, Any]]) -> Dict[str, Any]:
        best_allocation = None
        lowest_bias_score = float('inf')

        for member in team_members:
            allocation = {
                'task': task,
                'assigned_to': member['id'],
                'bias_metrics': {
                    'skill_bias': abs(task.get('required_skill_level', 0) - member.get('skill_level', 0)),
                    'experience_bias': abs(task.get('required_experience', 0) - member.get('experience', 0)),
                    'workload_bias': member.get('current_workload', 0) / 100  # Assuming workload is a percentage
                }
            }

            bias_score = self.calculate_overall_bias_score(allocation)
            if bias_score < lowest_bias_score:
                lowest_bias_score = bias_score
                best_allocation = allocation

        if best_allocation:
            best_allocation['bias_mitigation_suggestions'] = self.suggest_bias_mitigation(best_allocation)

        return best_allocation

    async def assign_task(self, task: str, *args, **kwargs) -> Any:
        if task == 'monitor_activity':
            return await self.monitoring_agent.process(*args, **kwargs)
        elif task == 'record_bias_metric':
            return self.record_bias_metric(*args, **kwargs)
        elif task == 'analyze_trends':
            return self.analyze_trends(*args, **kwargs)
        elif task == 'bias_aware_task_allocation':
            return self.bias_aware_task_allocation(*args, **kwargs)
        else:
            raise ValueError(f"Unknown task type: {task}")

# Usage example
if __name__ == "__main__":
    bias_management = BiasManagementMasterAgent(threshold=0.2, storage_path='bias_metrics.db')

    # Record some bias metrics
    bias_management.record_bias_metric("v1.0", "skill_bias", 0.15, {"project": "AI Integration"})
    bias_management.record_bias_metric("v1.0", "gender_bias", 0.22, {"team": "Backend Development"})
    bias_management.record_bias_metric("v1.0", "experience_bias", 0.18, {"sprint": "Sprint 5"})

    # Analyze trends
    print(bias_management.analyze_trends("v1.0", "skill_bias"))
    print(bias_management.analyze_trends("v1.0", "gender_bias"))

    # Example task allocation
    task = {
        "id": "TASK-001",
        "name": "Implement new API endpoint",
        "required_skill_level": 0.7,
        "required_experience": 3
    }

    team_members = [
        {"id": "EMP-001", "name": "Alice", "skill_level": 0.8, "experience": 5, "current_workload": 60},
        {"id": "EMP-002", "name": "Bob", "skill_level": 0.6, "experience": 2, "current_workload": 40},
        {"id": "EMP-003", "name": "Charlie", "skill_level": 0.9, "experience": 7, "current_workload": 80}
    ]

    allocation = bias_management.bias_aware_task_allocation(task, team_members)
    print("Bias-aware task allocation:")
    print(json.dumps(allocation, indent=2))