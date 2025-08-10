from fastmcp import FastMCP
from fastmcp.transports.tcp import TCPTransport
import psutil
import random

# ========= GLOBAL STATES =========
safety_mode = False
usage_count = 0
SUSPICIOUS_NAMES = [
    'bitcoin', 'keylogger', 'malware', 'trojan',
    'hacker', 'virus', 'ransom'
]

# Create MCP server
mcp = FastMCP("System Monitor MCP", version="1.0")

# ========= HELPER FUNCTIONS =========
def activate_safety_mode(reason="Unknown error"):
    global safety_mode
    safety_mode = True
    return {"status": "Safety Mode Enabled", "reason": reason}

def record_access_internal():
    global usage_count
    usage_count += 1

# ========= TOOLS =========
@mcp.tool()
def record_access() -> dict:
    record_access_internal()
    return {"total_accesses": usage_count}

@mcp.tool()
def get_usage_count() -> dict:
    return {"total_accesses": usage_count}

@mcp.tool()
def get_cpu_usage() -> dict:
    record_access_internal()
    global safety_mode
    try:
        if safety_mode:
            return activate_safety_mode("get_cpu_usage blocked in safety mode")
        return {"cpu_percent": psutil.cpu_percent(interval=1)}
    except Exception as e:
        activate_safety_mode(f"CPU usage tool crashed: {str(e)}")
        return {"error": str(e), "note": "Safety Mode Enabled"}

@mcp.tool()
def get_memory_info() -> dict:
    record_access_internal()
    global safety_mode
    try:
        if safety_mode:
            return activate_safety_mode("get_memory_info blocked in safety mode")
        mem = psutil.virtual_memory()
        return {"total": mem.total, "available": mem.available, "percent": mem.percent}
    except Exception as e:
        activate_safety_mode(f"Memory info tool crashed: {str(e)}")
        return {"error": str(e), "note": "Safety Mode Enabled"}

@mcp.tool()
def get_disk_space() -> dict:
    record_access_internal()
    global safety_mode
    try:
        if safety_mode:
            return activate_safety_mode("get_disk_space blocked in safety mode")
        disk = psutil.disk_usage('/')
        return {"total": disk.total, "used": disk.used, "free": disk.free, "percent": disk.percent}
    except Exception as e:
        activate_safety_mode(f"Disk usage tool crashed: {str(e)}")
        return {"error": str(e), "note": "Safety Mode Enabled"}

@mcp.tool()
def antivirus_scan() -> dict:
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
                        threats.append({"pid": proc.info['pid'], "name": proc.info['name']})
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if threats:
            activate_safety_mode("Suspicious process detected")
            return {"suspicious_processes": threats, "note": "Safety Mode Enabled"}
        else:
            return {"suspicious_processes": None, "status": "No threats found"}
    except Exception as e:
        activate_safety_mode(f"Antivirus scan crashed: {str(e)}")
        return {"error": str(e), "note": "Safety Mode Enabled"}

@mcp.tool()
def speed_math_game(action: str = "start", answer: int = None, state: dict = None) -> dict:
    record_access_internal()
    if state is None:
        state = {}
    if action == "start":
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(['+', '-', '*'])
        question = f"{a} {op} {b}"
        correct = eval(question)
        return {"message": f"Solve: {question}", "state": {"question": question, "answer": correct}}
    elif action == "answer":
        if not state or "answer" not in state:
            return {"error": "No active question. Start with action='start'."}
        is_correct = (answer == state["answer"])
        response = "✅ Correct!" if is_correct else f"❌ Wrong! The answer was {state['answer']}."
        return {"result": response, "state": {}}
    else:
        return {"error": "Invalid action. Use 'start' or 'answer'."}

@mcp.tool()
def search_simulator(query: str) -> dict:
    record_access_internal()
    return {
        "message": (
            f"🔎 Searching for '{query}'... Please wait.\n"
            "💡 While you wait, type: speed_math_game(action='start') to play a quick Speed Math game!"
        )
    }

# ========= RUN SERVER ON TCP =========
if __name__ == "__main__":
    # Listen on all interfaces, port 8000
    transport = TCPTransport(host="0.0.0.0", port=8000)
    mcp.run(transport=transport)
