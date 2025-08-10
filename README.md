\# 🖥️ System Monitor MCP Server



A multifunctional \*\*Model Context Protocol (MCP)\*\* server that provides:



\- \*\*System Monitoring\*\* — CPU, memory, disk statistics

\- \*\*Antivirus-like scan\*\* — detects suspicious running processes

\- \*\*Speed Math mini-game\*\* — play math puzzles while waiting

\- \*\*Usage tracking\*\* — see how many times the server has been accessed

\- \*\*Search simulator with game prompt\*\* — invites users to play while "loading"



---



\## 🚀 Features



\### 1. System Monitoring Tools

| Tool | Description |

|------|-------------|

| `get\_cpu\_usage` | Returns current CPU usage % |

| `get\_memory\_info` | Shows system memory stats (total, available, usage %) |

| `get\_disk\_space` | Provides total, used, free, and % disk space |



---



\### 2. Antivirus Scan

\*\*Tool:\*\* `antivirus\_scan`  

Scans running processes for suspicious names (`bitcoin`, `trojan`, `keylogger`, `malware`, etc.).  

If threats are found:

\- Safety Mode is activated

\- Risky tools are blocked until the server restarts



---



\### 3. Speed Math Mini-Game

\*\*Tool:\*\* `speed\_math\_game`  

Text-based challenge to solve math problems fast.



\*\*Usage:\*\*

1\. Start game:

speed\_math\_game(action="start")



→ Returns a math question and a `state` object.

2\. Answer:

speed\_math\_game(action="answer", answer=42, state={...})



Replace `42` with your solution and pass the exact `state` from the start call.



---



\### 4. Usage Tracking

| Tool | Description |

|------|-------------|

| `record\_access` | Increments the global access counter |

| `get\_usage\_count` | Returns total recorded accesses so far |



---



\### 5. Search Simulator with Game Prompt

\*\*Tool:\*\* `search\_simulator`  

Simulates a "loading" search and invites the user to play Speed Math in the meantime.



Example:

search\_simulator(query="example")



**Might return:**

**🔎 Searching for 'example'... This may take a moment.**

**💡 While you wait, type: speed\_math\_game(action='start') to play a quick Speed Math game!**



**---**



**## ⚠️ Safety Mode**

**Triggered by:**

**- A tool error/crash**

**- Antivirus finding suspicious processes**



**When Safety Mode is active:**

**- Risky tools are disabled until restart**

**- Responses include `"Safety Mode Enabled"`**



**---**



**## 🛠️ Installation \& Setup**



**1. \*\*Prerequisites:\*\* Python 3.10+ installed**

**2. \*\*Install UV\*\* (recommended):**

**pip install uv**



**3. \*\*Create and enter project folder:\*\***

**uv init system-monitor-mcp**

**cd system-monitor-mcp**

**4. \*\*Add dependencies:\*\***





**uv add fastmcp**

**uv add psutil**



**5. \*\*Place `main.py` in folder\*\* with the server code**



**---**



**## ▶️ Running Locally**



**With UV:**

**uv run python main.py**



**Without UV:**

**python main.py**





**If successful, the MCP server will start and wait for tool calls from an MCP client.**



**---**



**## ✅ Example Tool Calls**



**get\_cpu\_usage()**

**get\_memory\_info()**

**get\_disk\_space()**

**antivirus\_scan()**

**record\_access()**

**get\_usage\_count()**

**speed\_math\_game(action="start")**

**speed\_math\_game(action="answer", answer=7, state={...})**

**search\_simulator(query="testing")**

