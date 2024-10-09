import abc
from typing import List, Union, Dict, Any
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent(abc.ABC):
    @abc.abstractmethod
    def process(self) -> Any:
        pass

class MasterAgent:
    def __init__(self):
        self.sub_agents: List[Agent] = []
        self.results: List[Any] = []
        self.task_factory: Dict[str, type] = {
            'arithmetic': ArithmeticAgent
        }

    async def assign_task(self, task: str, operands: List[Any]) -> None:
        if task not in self.task_factory:
            raise ValueError(f"Unknown task type: {task}")
        
        agent_class = self.task_factory[task]
        agent = agent_class(*operands)
        self.sub_agents.append(agent)
        
        try:
            result = await asyncio.to_thread(agent.process)
            self.results.append(result)
            logger.info(f"Task completed. Result: {result}")
        except Exception as e:
            logger.error(f"Error processing task: {e}")

    def display_results(self) -> None:
        for i, result in enumerate(self.results, 1):
            print(f"Result {i}: {result}")

class ArithmeticAgent(Agent):
    def __init__(self, operand1: float, operand2: float, operator: str):
        self.operand1 = operand1
        self.operand2 = operand2
        self.operator = operator

    def process(self) -> float:
        operand_agent1 = OperandAgent(self.operand1)
        operand_agent2 = OperandAgent(self.operand2)
        operator_agent = OperatorAgent(self.operator)

        value1 = operand_agent1.retrieve_operand()
        value2 = operand_agent2.retrieve_operand()
        operation = operator_agent.retrieve_operator()

        if operation == '+':
            return value1 + value2
        elif operation == '-':
            return value1 - value2
        elif operation == '*':
            return value1 * value2
        elif operation == '/':
            if value2 == 0:
                raise ValueError("Division by zero")
            return value1 / value2
        else:
            raise ValueError(f"Unknown operator: {operation}")

class OperandAgent:
    def __init__(self, value: float):
        self.value = value

    def retrieve_operand(self) -> float:
        return self.value

class OperatorAgent:
    def __init__(self, operator: str):
        self.operator = operator

    def retrieve_operator(self) -> str:
        return self.operator

async def main():
    master_agent = MasterAgent()
    
    tasks = [
        master_agent.assign_task('arithmetic', [5, 3, '+']),
        master_agent.assign_task('arithmetic', [10, 2, '*']),
        master_agent.assign_task('arithmetic', [15, 3, '/']),
        master_agent.assign_task('arithmetic', [7, 2, '-'])
    ]
    
    await asyncio.gather(*tasks)
    master_agent.display_results()

if __name__ == "__main__":
    asyncio.run(main())