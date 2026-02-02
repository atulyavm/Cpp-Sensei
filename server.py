from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import uuid
import asyncio
import threading
from logic import SenseiLogic

app = FastAPI()
sensei = SenseiLogic() 

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExplanationRequest(BaseModel):
    line: str

@app.post("/explain")
async def explain_line(req: ExplanationRequest):
    explanation = sensei.explain_line(req.line)
    return {"explanation": explanation}

@app.websocket("/ws/run")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Receive the code first
    data = await websocket.receive_json()
    code = data.get('code')
    
    if not code:
        await websocket.send_text("Error: No code provided")
        await websocket.close()
        return

    # Setup files
    file_id = str(uuid.uuid4())
    src_file = f"temp_{file_id}.cpp"
    exe_file = f"temp_{file_id}.exe"
    
    try:
        with open(src_file, "w") as f:
            f.write(code)
            
        await websocket.send_text("Compiling...\n")
        
        comp = subprocess.run(['g++', src_file, '-o', exe_file], capture_output=True, text=True)
        
        if comp.returncode != 0:
            await websocket.send_text("Compilation Error:\n" + comp.stderr)
            await websocket.close()
            return
            
        await websocket.send_text("Running...\n")
        
        # Start Process
        process = subprocess.Popen(
            [exe_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0 # Unbuffered
        )
        
        # Helper to read stream and send to WS
        def stream_reader(pipe, prefix=""):
            try:
                while True:
                    # Read 1 character at a time to handle prompts without newlines (e.g. "Enter name: ")
                    chunk = pipe.read(1) 
                    if not chunk:
                        break
                    asyncio.run_coroutine_threadsafe(websocket.send_text(prefix + chunk), loop)
            except Exception:
                pass

        loop = asyncio.get_event_loop()
        
        # Start threads for stdout and stderr
        threading.Thread(target=stream_reader, args=(process.stdout,), daemon=True).start()
        threading.Thread(target=stream_reader, args=(process.stderr, "Error: "), daemon=True).start()
        
        # Main loop: Listen for input from Client
        try:
            while process.poll() is None:
                # Wait for input from user (browser) with a timeout
                try:
                    user_input = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                    if user_input:
                        process.stdin.write(user_input + "\n")
                        process.stdin.flush()
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    break
                    
        except Exception as e:
            pass
            
        await websocket.send_text("\n[Program Finished]")
        
    except Exception as e:
        await websocket.send_text(f"Server Error: {str(e)}")
    finally:
        await websocket.close()
        # Cleanup
        if os.path.exists(src_file):
            try: os.remove(src_file)
            except: pass
        if os.path.exists(exe_file):
            try: os.remove(exe_file)
            except: pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
