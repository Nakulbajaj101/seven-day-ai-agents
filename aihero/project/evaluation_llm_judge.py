import asyncio
import json
from pathlib import Path
from typing import List

import pandas as pd
from config import evaluation_system_prompt, evaluation_user_prompt
from pydantic import BaseModel
from pydantic_ai import Agent
from tqdm.auto import tqdm


class EvaluationCheck(BaseModel):
    check_name: str
    justification: str
    check_pass: bool

class EvaluationChecklist(BaseModel):
    checks: list[EvaluationCheck]
    summary: str

def load_log_data(log_file: str):
    try:
        with open(log_file, 'r') as f_in:
            log_data = json.load(f_in)
            log_data['log_file'] = log_file
            return log_data
    except FileNotFoundError:
        print(f"{log_file} is not found in the desired location")
    
def simplify_log_messages(messages):
    log_simplified = []

    for m in messages:
        parts = []
    
        for original_part in m['parts']:
            part = original_part.copy()
            kind = part['part_kind']
    
            if kind == 'user-prompt':
                del part['timestamp']
            if kind == 'tool-call':
                del part['tool_call_id']
            if kind == 'tool-return':
                del part['tool_call_id']
                del part['metadata']
                del part['timestamp']
                # Replace actual search results with placeholder to save tokens
                part['content'] = 'RETURN_RESULTS_REDACTED'
            if kind == 'text':
                del part['id']
    
            parts.append(part)
    
        message = {
            'kind': m['kind'],
            'parts': parts
        }
    
        log_simplified.append(message)
    return log_simplified

async def evaluate_log_record(eval_agent, log_record):
    messages = log_record['messages']

    instructions = log_record["system_prompt"][0]
    question = messages[0]['parts'][0]['content']
    answer = messages[-1]['parts'][0]['content']

    log_simplified = simplify_log_messages(messages)
    log = json.dumps(log_simplified)

    user_prompt = evaluation_user_prompt.format(
        instructions=instructions,
        question=question,
        answer=answer,
        log=log)

    result = await eval_agent.run(user_prompt, output_type=EvaluationChecklist)
    return result.output 

def eval_data(log_directory: Path) -> List:

    eval_set = []

    for log_file in log_directory.glob('*.json'):
        log_record = load_log_data(log_file=log_file)
        if log_record['source'] != 'ai-generated':
            continue
        eval_set.append(log_record)
    
    return eval_set

async def run_evaluations(eval_data: List, eval_agent) -> List:
    """Function to run evaluations"""
    eval_results = []
    for eval_record in tqdm(eval_data):
        eval_result = await evaluate_log_record(eval_agent=eval_agent,
                                        log_record=eval_record)
        eval_results.append((eval_result, eval_record))
    
    return eval_results

def build_evaluations_df(eval_results: List) -> pd.DataFrame:
    rows = []
    for data in eval_results:
        row = {"log_file": data[1]["log_file"],
            "source":  data[1]["source"],
            "model": data[1]["model"]}
        checks = {c.check_name: c.check_pass for c in data[0].checks}
        row.update(checks)
        rows.append(row)
    
    eval_df = pd.DataFrame(rows)
    return eval_df


if __name__ == "__main__":
    #Create the eval agent
    evaluation_agent = Agent(
        model="gpt-5-nano",#Using a different model to avoid bias and ensure better results
        name="eval_agent",
        instructions=evaluation_system_prompt,
        output_type=EvaluationChecklist
        )
    LOG_DIR = Path('../course/logs')

    # Extract evaluation ground truth data
    eval_set = eval_data(log_directory=LOG_DIR)
    eval_results = asyncio.run(run_evaluations(
        eval_data=eval_set,
        eval_agent=evaluation_agent
    ))

    eval_df = build_evaluations_df(eval_results=eval_results)

    # Check the evaluation results
    print(eval_df.mean(numeric_only=True))
