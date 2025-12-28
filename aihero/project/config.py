prompt_template = """
Split the provided document into logical sections
that make sense for a Q&A system.

Each section should be self-contained and cover
a specific topic or concept.

<DOCUMENT>
{document}
</DOCUMENT>

Use this format:

## Section Name

Section content with all relevant details

---

## Another Section Name

Another section content

---
""".strip()


evaluation_user_prompt = """
<INSTRUCTIONS>{instructions}</INSTRUCTIONS>
<QUESTION>{question}</QUESTION>
<ANSWER>{answer}</ANSWER>
<LOG>{log}</LOG>
""".strip()


# First we need the evaluation system prompt to build an eval agent with pydantic
# We will need the answer provided by agent, question of the user, log for further analysis
evaluation_system_prompt = """
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
""".strip()
