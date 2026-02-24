import unittest
from parser import OpenJudgeParser, FormatViolationError
from tools import execute_bash, execute_python

class TestOpenJudgeParser(unittest.TestCase):
    def setUp(self):
        self.parser = OpenJudgeParser()

    def test_valid_parsing(self):
        valid_xml = """
        <openjudge_process>
        <state_memory>This is the test memory</state_memory>
        <logical_extern>Logic here</logical_extern>
        <verdict>Test verdict</verdict>
        <tool_required>bash</tool_required>
        <tool_payload>echo "hello world"</tool_payload>
        </openjudge_process>
        [ENFORCE: PIVOT]
        """
        result = self.parser.parse(valid_xml)
        self.assertEqual(result["state_memory"], "This is the test memory")
        self.assertEqual(result["verdict"], "Test verdict")
        self.assertEqual(result["tool_required"], "bash")
        self.assertEqual(result["tool_payload"], "echo \"hello world\"")
        self.assertEqual(result["enforcement"], "PIVOT")

    def missing_tags_throw_error(self):
        invalid_xml = """
        I am an LLM hallucinating text.
        [ENFORCE: PROCEED]
        """
        with self.assertRaises(FormatViolationError):
            self.parser.parse(invalid_xml)

    def missing_enforce_throws_error(self):
        invalid_xml = """
        <openjudge_process>
        <state_memory>Memory</state_memory>
        <logical_extern>Logic</logical_extern>
        <verdict>Verdict</verdict>
        </openjudge_process>
        """
        with self.assertRaises(FormatViolationError):
            self.parser.parse(invalid_xml)


class TestOpenJudgeTools(unittest.TestCase):
    def test_execute_bash(self):
        result = execute_bash('echo OpenJudge Test')
        self.assertEqual(result, "OpenJudge Test")

    def test_execute_python(self):
        code = "print('Python Tool Working')"
        result = execute_python(code)
        self.assertEqual(result, "Python Tool Working")

if __name__ == '__main__':
    unittest.main()
