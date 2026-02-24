import re

class FormatViolationError(Exception):
    """
    Exception raised when the LLM output does not conform to the strict OpenJudge XML/tag format.
    """
    pass

class OpenJudgeParser:
    """
    A strict parser for the OpenJudge engine.
    Extracts XML blocks (<state_memory>, <logical_extern>, <verdict>) 
    and importantly, the physical <tool_required> and <tool_payload>, along with the [ENFORCE:] tag.
    """
    
    def __init__(self):
        # We use regex to extract the specific blocks. DOTALL allows matching across newlines.
        self.block_pattern = re.compile(
            r'<(state_memory|logical_extern|verdict|tool_required|tool_payload)>(.*?)</\1>', 
            re.DOTALL
        )
        
        # Regex to catch the ENFORCE tag exactly
        self.enforce_pattern = re.compile(r'\[ENFORCE:\s*(PROCEED|PURGE|PIVOT|TERMINATE)\]')

    def parse(self, text: str) -> dict:
        """
        Parses the raw LLM output text.
        """
        result = {
            "state_memory": None,
            "logical_extern": None,
            "verdict": None,
            "tool_required": None,
            "tool_payload": None,
            "enforcement": None
        }

        # 1. Extract XML blocks
        blocks = self.block_pattern.findall(text)
        found_blocks = set()
        for tag, content in blocks:
            result[tag] = content.strip()
            found_blocks.add(tag)

        # We enforce that the core structural XML tags are present if this is an OpenJudge output.
        # If the LLM completely hallucinated without using `<openjudge_process>`, we throw an error.
        if "verdict" not in found_blocks and "state_memory" not in found_blocks:
             raise FormatViolationError(
                "Missing structural XML tags. The response must use <openjudge_process> and "
                "include <state_memory>, <logical_extern>, and <verdict> blocks."
            )

        # 2. Extract Enforcement Tag
        enforce_match = self.enforce_pattern.search(text)
        
        if not enforce_match:
            raise FormatViolationError(
                "Missing or invalid enforcement tag. Expected exactly one of: "
                "[ENFORCE: PROCEED], [ENFORCE: PURGE], [ENFORCE: PIVOT], or [ENFORCE: TERMINATE]."
            )
            
        result["enforcement"] = enforce_match.group(1).upper()
        
        return result
