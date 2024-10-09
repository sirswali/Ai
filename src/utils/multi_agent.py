from typing import List, Any, Callable

class Agent:
    def __init__(self, name: str, task: Callable):
        self.name = name
        self.task = task
        self.result = None

    def process(self, *args, **kwargs):
        self.result = self.task(*args, **kwargs)
        return self.result

class MasterAgent:
    def __init__(self):
        self.sub_agents: List[Agent] = []
        self.result = None

    def add_agent(self, agent: Agent):
        self.sub_agents.append(agent)

    def assign_task(self, task_name: str, *args, **kwargs):
        for agent in self.sub_agents:
            if agent.name == task_name:
                self.result = agent.process(*args, **kwargs)
                return
        raise ValueError(f"No agent found for task: {task_name}")

    def display_result(self):
        if self.result is not None:
            print(f"Final Result from Master Agent: {self.result}")
        else:
            print("No result computed.")

# Example usage
def arithmetic_task(a: float, b: float, operator: str) -> float:
    if operator == '+':
        return a + b
    elif operator == '-':
        return a - b
    elif operator == '*':
        return a * b
    elif operator == '/':
        return a / b
    else:
        raise ValueError(f"Unknown operator: {operator}")

if __name__ == "__main__":
    master_agent = MasterAgent()
    arithmetic_agent = Agent("arithmetic", arithmetic_task)
    master_agent.add_agent(arithmetic_agent)

    master_agent.assign_task("arithmetic", 5, 3, '+')
    master_agent.display_result()

    master_agent.assign_task("arithmetic", 10, 2, '*')
    master_agent.display_result()