from fastmcp import FastMCP
import psutil
import random
import os
from typing import Dict, Any

# ========= GLOBAL STATES =========
safety_mode = False
usage_count = 0
SUSPICIOUS_NAMES = [
    'bitcoin', 'keylogger', 'malware', 'trojan',
    'hacker', 'virus', 'ransom'
]

# Create MCP server
mcp = FastMCP("System Monitor MCP")

# ========= HELPER FUNCTIONS =========
def activate_safety_mode(reason="Unknown error"):
    global safety_mode
    safety_mode = True
    return {"status": "Safety Mode Enabled", "reason": reason}

def record_access_internal():
    global usage_count
    usage_count += 1

# ========= CORE FUNCTIONS (without @mcp.tool decorator for direct calls) =========
def _record_access() -> dict:
    """Records access and returns total access count"""
    record_access_internal()
    return {"total_accesses": usage_count}

def _get_usage_count() -> dict:
    """Returns total recorded accesses so far"""
    return {"total_accesses": usage_count}

def _get_cpu_usage() -> dict:
    """Returns current CPU usage percentage"""
    record_access_internal()
    global safety_mode
    try:
        if safety_mode:
            return activate_safety_mode("get_cpu_usage blocked in safety mode")
        return {"cpu_percent": psutil.cpu_percent(interval=1)}
    except Exception as e:
        activate_safety_mode(f"CPU usage tool crashed: {str(e)}")
        return {"error": str(e), "note": "Safety Mode Enabled"}

def _get_memory_info() -> dict:
    """Shows system memory stats (total, available, usage %)"""
    record_access_internal()
    global safety_mode
    try:
        if safety_mode:
            return activate_safety_mode("get_memory_info blocked in safety mode")
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available, 
            "percent": mem.percent
        }
    except Exception as e:
        activate_safety_mode(f"Memory info tool crashed: {str(e)}")
        return {"error": str(e), "note": "Safety Mode Enabled"}

def _get_disk_space() -> dict:
    """Provides total, used, free, and % disk space"""
    record_access_internal()
    global safety_mode
    try:
        if safety_mode:
            return activate_safety_mode("get_disk_space blocked in safety mode")
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.used / disk.total * 100
        }
    except Exception as e:
        activate_safety_mode(f"Disk usage tool crashed: {str(e)}")
        return {"error": str(e), "note": "Safety Mode Enabled"}

def _antivirus_scan() -> dict:
    """Scans running processes for suspicious names"""
    record_access_internal()
    global safety_mode
    try:
        if safety_mode:
            return activate_safety_mode("antivirus_scan blocked in safety mode")
        
        threats = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'].lower()
                for sig in SUSPICIOUS_NAMES:
                    if sig in pname:
                        threats.append({
                            "pid": proc.info['pid'], 
                            "name": proc.info['name']
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if threats:
            activate_safety_mode("Suspicious process detected")
            return {
                "suspicious_processes": threats, 
                "note": "Safety Mode Enabled"
            }
        else:
            return {
                "suspicious_processes": None, 
                "status": "No threats found"
            }
    except Exception as e:
        activate_safety_mode(f"Antivirus scan crashed: {str(e)}")
        return {"error": str(e), "note": "Safety Mode Enabled"}

def _speed_math_game(action: str = "start", answer: int = None, state: dict = None) -> dict:
    """Text-based challenge to solve math problems fast"""
    record_access_internal()
    if state is None:
        state = {}
    
    if action == "start":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(['+', '-', '*'])
        question = f"{a} {op} {b}"
        correct = eval(question)
        return {
            "message": f"Solve: {question}", 
            "state": {"question": question, "answer": correct}
        }
    elif action == "answer":
        if not state or "answer" not in state:
            return {"error": "No active question. Start with action='start'."}
        
        is_correct = (answer == state["answer"])
        response = "✅ Correct!" if is_correct else f"❌ Wrong! The answer was {state['answer']}."
        return {"result": response, "state": {}}
    else:
        return {"error": "Invalid action. Use 'start' or 'answer'."}

def _search_simulator(query: str) -> dict:
    """Simulates a loading search and invites user to play Speed Math"""
    record_access_internal()
    return {
        "message": (
            f"🔎 Searching for '{query}'... Please wait.\n"
            "💡 While you wait, type: speed_math_game(action='start') to play a quick Speed Math game!"
        )
    }

# ========= MCP TOOLS (for MCP protocol) =========
@mcp.tool()
def record_access() -> dict:
    return _record_access()

@mcp.tool()
def get_usage_count() -> dict:
    return _get_usage_count()

@mcp.tool()
def get_cpu_usage() -> dict:
    return _get_cpu_usage()

@mcp.tool()
def get_memory_info() -> dict:
    return _get_memory_info()

@mcp.tool()
def get_disk_space() -> dict:
    return _get_disk_space()

@mcp.tool()
def antivirus_scan() -> dict:
    return _antivirus_scan()

@mcp.tool()
def speed_math_game(action: str = "start", answer: int = None, state: dict = None) -> dict:
    return _speed_math_game(action, answer, state)

@mcp.tool()
def search_simulator(query: str) -> dict:
    return _search_simulator(query)

# ========= WEB SERVER FOR RENDER =========
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Create FastAPI app for web deployment
app = FastAPI(title="System Monitor MCP Server")

@app.get("/")
async def root():
    return {
        "server": "System Monitor MCP Server",
        "status": "running",
        "tools": [
            "get_cpu_usage", "get_memory_info", "get_disk_space", 
            "antivirus_scan", "speed_math_game", "search_simulator",
            "record_access", "get_usage_count"
        ],
        "safety_mode": safety_mode,
        "total_accesses": usage_count
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "safety_mode": safety_mode}

# Tool endpoints using the core functions
@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, params: Dict[str, Any] = None):
    if params is None:
        params = {}
    
    try:
        if tool_name == "get_cpu_usage":
            return _get_cpu_usage()
        elif tool_name == "get_memory_info":
            return _get_memory_info()
        elif tool_name == "get_disk_space":
            return _get_disk_space()
        elif tool_name == "antivirus_scan":
            return _antivirus_scan()
        elif tool_name == "speed_math_game":
            return _speed_math_game(**params)
        elif tool_name == "search_simulator":
            return _search_simulator(params.get("query", ""))
        elif tool_name == "record_access":
            return _record_access()
        elif tool_name == "get_usage_count":
            return _get_usage_count()
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Use PORT environment variable from Render
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting System Monitor MCP Server on port {port}")
    print("Available at: /")
    print("Health check: /health")
    print("Tools: /tools/{tool_name}")
    
    # Run FastAPI server with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
