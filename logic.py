import re

class SenseiLogic:
    def __init__(self):
        self.rules = [
            (r'#include\s*<(.*)>', "🧰 TOOLBOX: You are bringing in the '{}' library. It gives your program extra powers like printing or math."),
            (r'using namespace std;', "📝 SHORTCUT: You're telling the computer to assume we're using the 'standard' names, so you don't have to type 'std::' every time."),
            (r'int\s+main\(\)', "🚀 START: This is the 'Main Entry'. When you run the program, the computer looks for this line first."),
            (r'int\s+(\w+)\s*=', "📦 VARIABLE: You've created a container named '{}' to hold whole numbers."),
            (r'float\s+(\w+)\s*=', "🥛 VARIABLE: You've created a container named '{}' to hold numbers with decimals (like 3.14)."),
            (r'char\s+(\w+)\s*=', "🔤 VARIABLE: You've created a container named '{}' to hold a single character (like 'A')."),
            (r'cin\s*>>\s*(\w+);', "👂 INPUT: The program is now listening! It will wait for the user to type something and save it in '{}'."),
            (r'cout\s*<<\s*(.*);', "📢 OUTPUT: You are sending '{}' to the screen for the user to see."),
            (r'if\s*\((.*)\)', "🛣️ DECISION: The computer is checking if ({}) is true. If it's not, it will skip the next block of code."),
            (r'while\s*\((.*)\)', "🔄 LOOP: As long as ({}) is true, the computer will repeat the instructions inside the curly brackets."),
            (r'return\s+0;', "🏁 FINISH: This tells the computer, 'I'm done, and everything went perfectly!'")
        ]

    def explain_line(self, line):
        line = line.strip()
        if not line: return "..."
        
        for pattern, explanation in self.rules:
            match = re.search(pattern, line)
            if match:
                return explanation.format(*match.groups())
        
        return "I'm watching! That looks like a custom line. Keep going!"