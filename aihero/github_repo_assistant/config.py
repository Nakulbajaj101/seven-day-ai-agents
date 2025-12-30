from pydantic import BaseModel

EVALUATION_USER_PROMPT = """
<INSTRUCTIONS>{instructions}</INSTRUCTIONS>
<QUESTION>{question}</QUESTION>
<ANSWER>{answer}</ANSWER>
<LOG>{log}</LOG>
""".strip()

EVALUATION_SYSTEM_PROMPT = """
Use this checklist to evaluate the quality of an AI agent's answer (<ANSWER>) to a user question (<QUESTION>).
We also include the entire log (<LOG>) for analysis.

For each item, check if the condition is met. 

Checklist:

- instructions_follow: The agent followed the user's instructions (in <INSTRUCTIONS>)
- instructions_avoid: The agent avoided doing things it was told not to do  
- answer_relevant: The response directly addresses the user's question  
- answer_clear: The answer is clear and correct  
- answer_citations: The response includes proper citations or sources when required  
- completeness: The response is complete and covers all key aspects of the request
- factual: The response was not hallucinated and covers actual facts
- tool_call_search: Is the search tool invoked? 

Output true/false for each check and provide a short explanation for your judgment.
Output true/false for each check and provide a short explanation for your judgment.
""".strip()

class EvaluationConfig(BaseModel):
    model_name: str = "gpt-5-nano"
    concurrency_level: int = 8
    log_directory: str = "evaluation_data"
    output_file: str = "evaluation_results.csv"

EVALUATION_CONFIG = EvaluationConfig()
