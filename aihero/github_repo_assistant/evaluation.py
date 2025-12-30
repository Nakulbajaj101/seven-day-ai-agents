import asyncio
import concurrent.futures
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel
from pydantic_ai import Agent
from tqdm.auto import tqdm

from config import EVALUATION_CONFIG, EVALUATION_SYSTEM_PROMPT, EVALUATION_USER_PROMPT

# --- Models ---

class EvaluationCheck(BaseModel):
    check_name: str
    justification: str
    check_pass: bool

class EvaluationChecklist(BaseModel):
    checks: List[EvaluationCheck]
    summary: str

# --- Logic ---

def init_eval_agent() -> Agent:
    return Agent(
        model=EVALUATION_CONFIG.model_name, 
        name="eval_agent",
        instructions=EVALUATION_SYSTEM_PROMPT,
        output_type=EvaluationChecklist
    )

def load_log_data(log_file: Path) -> Dict[str, Any]:
    try:
        with open(log_file, 'r') as f_in:
            log_data = json.load(f_in)
            log_data['log_file'] = str(log_file.name)
            return log_data
    except FileNotFoundError:
        print(f"{log_file} is not found in the desired location")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {log_file}")
        return {}
    
def simplify_log_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    log_simplified = []

    for m in messages:
        parts = []
    
        for original_part in m.get('parts', []):
            part = original_part.copy()
            kind = part.get('part_kind')
    
            if kind == 'user-prompt':
                part.pop('timestamp', None)
            if kind == 'tool-call':
                part.pop('tool_call_id', None)
            if kind == 'tool-return':
                part.pop('tool_call_id', None)
                part.pop('metadata', None)
                part.pop('timestamp', None)
                # Replace actual search results with placeholder to save tokens
                part['content'] = 'RETURN_RESULTS_REDACTED'
            if kind == 'text':
                part.pop('id', None)
    
            parts.append(part)
    
        message = {
            'kind': m.get('kind'),
            'parts': parts
        }
    
        log_simplified.append(message)
    return log_simplified

async def evaluate_log_record(eval_agent: Agent, log_record: Dict[str, Any]) -> EvaluationChecklist:
    messages = log_record.get('messages', [])
    if not messages:
        raise ValueError("Log record has no messages")

    # Assuming standard structure: 
    instructions = ""
    if "system_prompt" in log_record and log_record["system_prompt"]:
        instructions = log_record["system_prompt"][0]
    
    # Extract question and answer
    try:
        question = "Unknown Question"
        if messages and 'parts' in messages[0] and messages[0]['parts']:
            question = messages[0]['parts'][0]['content']
            
        answer = "No Answer"
        if messages and 'parts' in messages[-1] and messages[-1]['parts']:
            answer = messages[-1]['parts'][0]['content']

    except Exception as e:
        print(f"Error parseing log content: {e}")
        question = "Error extracting question"
        answer = "Error extracting answer"

    log_simplified = simplify_log_messages(messages)
    log_str = json.dumps(log_simplified)

    user_prompt = EVALUATION_USER_PROMPT.format(
        instructions=instructions,
        question=question,
        answer=answer,
        log=log_str)

    result = await eval_agent.run(user_prompt)
    return result.output

def get_eval_data(log_directory: Path) -> List[Dict[str, Any]]:
    eval_set = []
    if not log_directory.exists():
        return eval_set
        
    for log_file in log_directory.glob('*.json'):
        log_record = load_log_data(log_file=log_file)
        if not log_record: 
            continue
            
        # Filter for AI generated logs only if that metadata exists
        if log_record.get('source') != 'ai-generated':
            continue
            
        eval_set.append(log_record)
    
    return eval_set

def process_record(log_record: Dict[str, Any]) -> Optional[tuple]:
    """
    Worker function to process a single record in a separate thread/loop.
    This ensures isolation and avoids 'anyio.WouldBlock' issues in a single busy loop.
    """
    try:
        # Create a fresh agent for this thread/task
        agent = init_eval_agent()
        
        # Run the async evaluation in a fresh event loop
        eval_result = asyncio.run(evaluate_log_record(eval_agent=agent, log_record=log_record))
        return (eval_result, log_record)
    except Exception as e:
        print(f"Failed to evaluate {log_record.get('log_file')}: {e}")
        return None

def run_evaluations(eval_data: List[Dict[str, Any]], concurrency: int = EVALUATION_CONFIG.concurrency_level) -> List[tuple]:
    """Function to run evaluations using ThreadPoolExecutor"""
    eval_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all tasks
        futures = {executor.submit(process_record, record): record for record in eval_data}
        
        # Process as they complete
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(eval_data), desc=f"Evaluating Logs (Threads: {concurrency})"):
            result = future.result()
            if result:
                eval_results.append(result)
            
    return eval_results

def build_evaluations_df(eval_results: List[tuple]) -> pd.DataFrame:
    rows = []
    for result, record in eval_results:
        row = {
            "log_file": record.get("log_file"),
            "source":  record.get("source"),
            "model": record.get("model")
        }
        if isinstance(result, EvaluationChecklist):
            checks = {c.check_name: c.check_pass for c in result.checks}
            row.update(checks)
        rows.append(row)
    
    if not rows:
        return pd.DataFrame()
        
    eval_df = pd.DataFrame(rows)
    return eval_df

def main():
    LOG_DIR = Path(EVALUATION_CONFIG.log_directory)
    if not LOG_DIR.exists():
        print(f"Directory {LOG_DIR} not found.")
        return

    # Extract evaluation ground truth data
    eval_set = get_eval_data(log_directory=LOG_DIR)
    print(f"Found {len(eval_set)} logs to evaluate.")
    
    if not eval_set:
        return

    # Run evaluations (Sync call now)
    eval_results = run_evaluations(
        eval_data=eval_set,
        concurrency=EVALUATION_CONFIG.concurrency_level
    )

    eval_df = build_evaluations_df(eval_results=eval_results)

    # Check the evaluation results
    print("\nEvaluation Results Summary:")
    print(eval_df.mean(numeric_only=True))
    
    # Save results
    output_file = EVALUATION_CONFIG.output_file
    eval_df.to_csv(output_file, index=False)
    print(f"\nDetailed results saved to {output_file}")

if __name__ == "__main__":
    if "OPENAI_API_KEY" not in os.environ:
        print("❌ Error: OPENAI_API_KEY environment variable is not set.")
        exit(1)
        
    main()
