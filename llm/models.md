# LLM Routing Strategy

---

## Group 1: The Heavy Reasoners (The "Supervisors")

Use these when the agent needs to write complex bash scripts, recover from Linux errors, or handle strict, nested JSON schemas.

---

### 1. llama-3.3-70b-versatile (Groq)

**Limits:**  
30 RPM | 12K TPM | 100K TPD  

**When to use:**  
Your primary Live Telegram C2 Agent. At 70B parameters, it is a genius-level coder and reasoning engine. Because it runs on Groq, it will reply to your Telegram messages instantly.

**Constraint:**  
The 12K TPM limit means it cannot read massive log files.

---

### 2. openai/gpt-oss-120b (Groq)

**Limits:**  
30 RPM | 8K TPM | 200K TPD  

**When to use:**  
The "Nuclear Option" for reasoning. If the 70B model fails a logic puzzle, route it here. A 120B parameter model is massively intelligent.

**Constraint:**  
The 8K TPM limit is extremely tight. Only send it highly truncated, essential context.

---

### 3. qwen/qwen3-32b (Groq)

**Limits:**  
60 RPM | 6K TPM | 500K TPD  

**When to use:**  
Qwen models are notoriously elite at coding and terminal commands. With a double-speed 60 RPM limit, this is a fantastic fallback if the Llama 70B model hits a rate limit during a fast back-and-forth chat.

---

# Group 2: The High-Volume Workhorses (The "Scrapers")

Use these for background loops, grading Reddit posts, and tasks that run 24/7.

---

### 4. gemma-3-27b (Google)

**Limits:**  
30 RPM | 15K TPM | 14,400 RPD  

**When to use:**  
Your primary background Reddit scraper. The 14,400 Requests Per Day limit makes this the most valuable free API on your list. A 27B model is incredibly smart for grading text.

**Constraint:**  
Google's REST latency is slower than Groq's, but for a background scraper, speed doesn't matter.

---

### 5. llama-3.1-8b-instant (Groq)

**Limits:**  
30 RPM | 6K TPM | 500K TPD  

**When to use:**  
Fast, simple, high-volume binary decisions (e.g., "Is this Reddit post spam? Yes/No").

---

# Group 3: The Massive Context Eaters (The "Readers")

Use these strictly when a Termux command outputs thousands of lines of text (like `cat /var/log/syslog`) that would instantly crash Groq's TPM limits.

---

### 6. gemini-2.5-flash (Google)

**Limits:**  
5 RPM | 250K TPM | 20 RPD  

**When to use:**  
When you need the agent to read an entire codebase or a massive log file. 250,000 tokens per minute is an astronomical limit.

**Constraint:**  
You only get 20 requests per day. Hoard these requests like gold. Do not use this model for simple `ls` commands.

---

### 7. gemini-3-flash (Google)

**Limits:**  
5 RPM | 250K TPM | 20 RPD  

**When to use:**  
The exact same use-case as above. If `gemini-2.5-flash` burns its 20 daily requests, your router should instantly failover to this model to unlock 20 more massive-context requests.

---

# Group 4: High-Burst / Specialized Models

Use these as shock absorbers when you need weird combinations of speed and token limits.

---

### 8. groq/compound (Groq)

**Limits:**  
30 RPM | 70K TPM | No TPD limit shown  

**When to use:**  
When you need a massive burst of tokens (up to 70,000 in a minute) but you want Groq's lightning-fast speed instead of Google's slower REST API.

---

### 9. meta-llama/llama-4-scout-17b-16e-instruct (Groq)

**Limits:**  
30 RPM | 30K TPM | 500K TPD  

**When to use:**  
A brilliant middle ground. 17B is smart enough for complex routing, and the 30K TPM gives you 2.5× the context breathing room of the standard Llama 70B model.

---

### 10. allam-2-7b (Groq)

**Limits:**  
30 RPM | 6K TPM | 500K TPD  

**When to use:**  
An ultra-lightweight fallback. If the primary 8B models are experiencing API outages or rate limits, this is a clean, standard 7B model to keep your basic scraping pipelines alive.