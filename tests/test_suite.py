import unittest
from test_main import TestMain, TestSlackHandlers
from test_task_allocator import TestTaskAllocator
from test_knowledge_base import TestKnowledgeBase
from test_llm_wrapper import TestLLMWrapper

def create_test_suite():
    test_suite = unittest.TestSuite()
    
    # Add tests from TestMain
    test_suite.addTest(unittest.makeSuite(TestMain))
    test_suite.addTest(unittest.makeSuite(TestSlackHandlers))
    
    # Add tests from TestTaskAllocator
    test_suite.addTest(unittest.makeSuite(TestTaskAllocator))
    
    # Add tests from TestKnowledgeBase
    test_suite.addTest(unittest.makeSuite(TestKnowledgeBase))
    
    # Add tests from TestLLMWrapper
    test_suite.addTest(unittest.makeSuite(TestLLMWrapper))
    
    return test_suite

if __name__ == '__main__':
    suite = create_test_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)