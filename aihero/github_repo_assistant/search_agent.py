from minsearch import Index
from pydantic_ai import Agent
from search_tools import SearchTool

SYSTEM_PROMPT_TEMPLATE = """
You are a helpful assistant for documentation  

Use the search tool to find relevant information from the document materials before answering questions.  

If you can find specific information through search, use it to provide accurate answers.
Before providing an answer please make certain checks:
- The response directly addresses the user's question  
- The answer is clear and correct  
- The response includes proper citations or sources when required  
- The response is complete and covers all key aspects of the request
- The response was not hallucinated and covers actual facts


Finally Always include references by citing the filename of the source material you used.  
When citing the reference, construct the link to the GitHub repository: "https://github.com/{repo_owner}/{repo_name}/blob/main/{{filename}}"
Format: [filename](https://github.com/{repo_owner}/{repo_name}/blob/main/filename)

If the search doesn't return relevant results, let the user know and provide general guidance.  
""".strip()

def init_agent(index: Index, repo_owner: str, repo_name: str) -> Agent:

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(repo_owner=repo_owner, repo_name=repo_name)

    st = SearchTool(
        index=index
    )

    agent = Agent(
        name = "search_docs",
        instructions=system_prompt,
        model = "gpt-4o-mini",
        tools=[st.search]
    )

    return agent
