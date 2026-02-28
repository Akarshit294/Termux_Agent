import aiohttp
import json
from pydantic import BaseModel, Field
from typing import Type, TypeVar, List, Optional, Literal
from utils.config import config
from utils.logger import get_logger
from services.shell_service import ShellService
from prompts.loader import get_prompt
from .llm_gateway import llm_gateway

log = get_logger(__name__, process_name="gemini_agent")

T = TypeVar("T", bound=BaseModel)


# ==========================================
# 1. NETWORK LAYER (Gateway Protected)
# ==========================================
@llm_gateway
async def raw_gemini_api_call(payload: dict, response_schema: Type[T] = None, caller: str = "telegram") -> T:
    """
    Pure network layer. The @llm_gateway handles retries here, 
    so a rate limit failure just pauses and retries this single call, not the whole loop.
    """
    log.info("Requesting Gemini structured output...")
    api_key = config.gemini_api_key.get_secret_value()
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent?key={api_key}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers={'Content-Type': 'application/json'}) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                log.error(f"Gemini API Error {resp.status}: {error_text}")
                raise Exception(f"HTTP {resp.status}")

            data = await resp.json()
            
    try:
        res_text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed_result = response_schema.model_validate_json(res_text)
        return parsed_result
    except Exception as e:
        log.error(f"Failed to parse Gemini response: {str(e)}")
        raise Exception(f"Parsing Error: {str(e)}")


# ==========================================
# 2. AGENT ORCHESTRATOR LOOP
# ==========================================
async def call_gemini(payload: dict, **kwargs) -> str:
    """
    The Thinking Loop (Supervisor Agent).
    Runs in the standard pipeline. Calls the gateway-protected network function.
    """
    user_prompt = payload.get("user_prompt", "")
    history = payload.get("history", [])
    caller = payload.get("caller", "telegram")
    
    system_prompt = get_prompt("termux_assistant.txt", pipeline=caller)
    
    # Use a fresh list to avoid mutating the SQLite history reference
    contents = list(history) 
    
    if user_prompt and (not contents or contents[-1].get("role") != "user"):
        contents.append({"role": "user", "parts": [{"text": user_prompt}]})
    
    # Manually define the strict, flat schema for the REST API to avoid $defs errors
    gemini_strict_schema = {
        "type": "OBJECT",
        "properties": {
            "thought": {"type": "STRING", "description": "The reasoning behind the current action."},
            "action": {"type": "STRING", "description": "Must be exactly 'run_command' or 'final_response'."},
            "command": {"type": "STRING", "description": "The shell command to execute (if applicable)."},
            "answer": {"type": "STRING", "description": "The message to send to the user (if applicable)."}
        },
        "required": ["thought", "action"]
    }
    
    gemini_payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": gemini_strict_schema
        }
    }
    
    for step in range(10):
        log.info(f"Step {step + 1}: Thinking...")
        
        try:
            # Pass the payload to the gateway-protected function
            decision_model: AgentDecision = await raw_gemini_api_call(
                payload=gemini_payload, 
                response_schema=AgentDecision, 
                caller=caller
            )
            
            # Use the flat action string instead of isinstance()
            if decision_model.action == "run_command":
                log.info(f"Action: Running Command -> {decision_model.command}")
                result = await ShellService.execute_command(decision_model.command)
                
                # CRITICAL: Truncate output to protect RAM and token limits!
                stdout_safe = result['stdout'][:2000] + ("\n...[TRUNCATED]" if len(result['stdout']) > 2000 else "")
                stderr_safe = result['stderr'][:1000] + ("\n...[TRUNCATED]" if len(result['stderr']) > 1000 else "")
                
                observation = (
                    f"Command: {decision_model.command}\n"
                    f"Exit Code: {result['exit_code']}\n"
                    f"STDOUT: {stdout_safe}\n"
                    f"STDERR: {stderr_safe}"
                )
                
                # Append the action and the observation to the payload history
                gemini_payload["contents"].append({
                    "role": "model", 
                    "parts": [{"text": decision_model.model_dump_json()}]
                })
                gemini_payload["contents"].append({
                    "role": "user", 
                    "parts": [{"text": f"OBSERVATION:\n{observation}"}]
                })
                
            elif decision_model.action == "final_response":
                return decision_model.answer
                
        except Exception as e:
            log.error(f"Error in Agent loop: {str(e)}")
            return f"⚠️ Agent Error: {str(e)}"
            
    return "⚠️ Agent Error: Maximum iteration limit reached. Goal not completed."