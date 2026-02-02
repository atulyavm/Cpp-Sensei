import threading
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os
from logic import SenseiLogic  # Importing the brain

class SenseiIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensei: The Learning IDE")
        self.root.geometry("1000x700")
        self.logic = SenseiLogic()

        # --- Top Toolbar ---
        self.toolbar = tk.Frame(root, bg="#eeeeee", height=40)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.run_btn = tk.Button(self.toolbar, text="▶ Run Code", command=self.run_code, 
                                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.run_btn.pack(side=tk.LEFT, padx=10, pady=5)

        # --- Main Body (Middle) ---
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left: Code Editor
        self.editor = scrolledtext.ScrolledText(self.paned_window, width=50, font=("Courier New", 12), undo=True)
        self.paned_window.add(self.editor)
        self.editor.bind("<KeyRelease>", self.update_explanation)

        # Right: Sensei Explanation Panel
        self.tutor_frame = tk.Frame(self.paned_window, bg="white")
        self.paned_window.add(self.tutor_frame)
        
        self.tutor_label = tk.Label(self.tutor_frame, text="SENSEI EXPLAINS", font=("Arial", 10, "bold"), bg="white")
        self.tutor_label.pack(pady=5)
        
        self.tutor_panel = tk.Text(self.tutor_frame, wrap=tk.WORD, font=("Arial", 12), bg="#f9f9f9", padx=10, pady=10)
        self.tutor_panel.pack(fill=tk.BOTH, expand=True)

        # --- Bottom: Console ---
        self.console = tk.Text(root, height=10, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.console.pack(side=tk.BOTTOM, fill=tk.X)
        self.console.insert(tk.END, "Console Output will appear here...\n")

    def update_explanation(self, event):
        # Get the current line content
        idx = self.editor.index(tk.INSERT).split('.')[0]
        line_content = self.editor.get(f"{idx}.0", f"{idx}.end")
        
        # Get explanation
        explanation = self.logic.explain_line(line_content)
        
        self.tutor_panel.delete('1.0', tk.END)
        self.tutor_panel.insert(tk.END, f"Line {idx}:\n\n{explanation}")
    

    def run_code(self):
        # UI updates must happen in the main thread
        self.console.delete('1.0', tk.END)
        self.console.insert(tk.END, "Compiling...\n")
        
        # Get code from editor (Tkinter is not thread-safe, so get text here)
        code_content = self.editor.get("1.0", tk.END)
        
        # Start a new thread for blocking operations (IO/Process)
        threading.Thread(target=self.execute_process, args=(code_content,), daemon=True).start()

    def execute_process(self, code_content):
        # Write the code to the file
        try:
            with open("temp.cpp", "w") as f:
                f.write(code_content)
        except Exception as e:
             self.root.after(0, lambda: self.console.insert(tk.END, f"❌ Error saving file: {str(e)}\n"))
             return

        # Check if the executable exists and try to remove it (cleanup)
        if os.path.exists("temp.exe"):
            try:
                os.remove("temp.exe")
            except PermissionError:
                self.root.after(0, lambda: self.console.insert(tk.END, "❌ Error: The program is still running. Please close it before running again!\n"))
                return 

        # Compile
        comp = subprocess.run(['g++', 'temp.cpp', '-o', 'temp.exe'], capture_output=True, text=True)
        
        if comp.returncode != 0:
            raw_error = comp.stderr
            friendly_msg = "Sensei: I found a small mistake!\n\n"
            
            if "expected ';'" in raw_error:
                friendly_msg += "💡 Tip: You forgot a semicolon (;) at the end of a line. In C++, that's like a period at the end of a sentence."
            elif "was not declared in this scope" in raw_error:
                friendly_msg += "💡 Tip: You're using a name that the computer doesn't recognize. Did you forget to create the variable first?"
            else:
                friendly_msg += "Technical Error Details:\n" + raw_error
                
            self.root.after(0, lambda: self.console.insert(tk.END, friendly_msg))
        else:
            self.root.after(0, lambda: self.console.insert(tk.END, "Compilation successful! Running program...\n"))
            
            # Run the compiled executable
            try:
                run = subprocess.run(['temp.exe'], capture_output=True, text=True, timeout=5) # Added timeout for safety
                output = run.stdout
                errors = run.stderr
                
                self.root.after(0, lambda: self.console.insert(tk.END, output))
                if errors:
                    self.root.after(0, lambda: self.console.insert(tk.END, "\nRuntime Errors:\n" + errors))
            except subprocess.TimeoutExpired:
                 self.root.after(0, lambda: self.console.insert(tk.END, "\n❌ Error: Program took too long to run (Infinite loop?)."))
            except Exception as e:
                 self.root.after(0, lambda: self.console.insert(tk.END, f"\n❌ Execution Error: {str(e)}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = SenseiIDE(root)
    root.mainloop()