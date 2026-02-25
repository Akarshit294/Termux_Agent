import asyncio
import time
from functools import wraps
from logger import get_logger


log = get_logger(__name__)
llm_queue = asyncio.PriorityQueue()


ROUTING_RULES = {
    "telegram": {"priority": 1, "max_retries": 10, "description": "High-Priority Chat"},
    "default":  {"priority": 2, "max_retries": 5, "description": "Unknown Caller"}
}


async def llm_worker():
    """
    The Single Background Worker.
    Pulls tasks from the queue based on priority and executes them safely.
    """
    log.info("LLM Gateway Worker started.")
    
    while True:
        # 1. Grab the highest priority item from the queue
        priority, _, func, payload, caller, max_retries, future = await llm_queue.get()
        
        log.info(f"[{caller}] Worker picked up request (Priority {priority}).")
        
        # 2. The Exponential Backoff Loop
        success = False
        for attempt in range(max_retries):
            try:
                # Execute the pure network function
                result = await func(payload)
                future.set_result(result)  # Hand the result back to the IOU
                success = True
                break  # Exit the retry loop on success
                
            except Exception as e:
                wait_time = 5 * (2 ** attempt)
                log.warning(f"[{caller}] Network failure: {e}. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                await asyncio.sleep(wait_time)
        
        # 3. Exhaustion Handler
        if not success:
            error_msg = f"Gateway Error: {caller} failed to reach LLM after {max_retries} attempts."
            log.error(f"[{caller}] {error_msg}")
            # Send a graceful text error back to the pipeline instead of crashing the script
            future.set_result(f"⚠️ {error_msg}")
            
        # 4. Tell the queue this task is officially done
        llm_queue.task_done()
        

def llm_gateway(func):
    """
    The Decorator. Intercepts the call, creates an IOU (Future), 
    puts it in the queue, and waits for the worker to process it.
    """
    @wraps(func)
    async def wrapper(payload: dict, caller: str = "default", *args, **kwargs):
        rules = ROUTING_RULES.get(caller, ROUTING_RULES["default"])
        priority = rules["priority"]
        max_retries = rules["max_retries"]
        desc = rules["description"]
        
        # Create the IOU (Future)
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        
        # Tie-breaker prevents Python from crashing if priorities are identical
        tie_breaker = time.monotonic() 
        
        # Package the task and put it in the queue
        task_package = (priority, tie_breaker, func, payload, caller, max_retries, future)
        await llm_queue.put(task_package)
        
        log.info(f"[{caller}] {desc} queued at Priority {priority}.")
        
        # Freeze this specific pipeline and wait for the worker to fill out the IOU
        return await future
        
    return wrapper