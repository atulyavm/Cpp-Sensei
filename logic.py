import re
from typing import Optional, Tuple, List

class SenseiLogic:
    def __init__(self):
        # Each rule: (pattern, short_summary, detailed_explanation, docs_url)
        self.rules = [
            # --- PREPROCESSOR & SETUP ---
            (r'#include\s*<(.*)>',
             "HEADER INCLUDE: #include <{}> tells the preprocessor to pull in external tools (like input/output) so you can use them in your code.",
             "DETAILED: The #include directive is handled by the preprocessor before compilation. It copies the entire content of the header file into your code. <iostream> is the most common, providing 'std::cin' and 'std::cout'. Headers declare the 'blueprints' (functions and classes) that the compiler needs to verify your code is valid.",
             "https://en.cppreference.com/w/cpp/header"),

            (r'using\s+namespace\s+std;',
             "NAMESPACE DIRECTIVE: This lets you use standard tools like 'cout' directly instead of writing 'std::cout' every time.",
             "DETAILED: Namespaces are like folders for code. The standard library lives in the 'std' namespace. While 'using namespace std;' saves time, it can cause 'naming collisions' in large projects (where two different things have the same name). Professional code often prefers 'std::cout' for clarity.",
             "https://en.cppreference.com/w/cpp/language/namespace"),

            (r'int\s+main\s*\(',
             "PROGRAM ENTRY: This is the 'Front Door' of your program. The computer starts executing your code from here.",
             "DETAILED: 'int main()' is a mandatory function. The 'int' means it returns an integer to the Operating System when it finishes. If it returns 0, the OS knows the program ran successfully. Execution always starts at the first line inside the curly braces { }.",
             "https://en.cppreference.com/w/cpp/language/main_function"),

            # --- DATA TYPES & VARIABLES ---
            (r'(int|float|double|char|bool)\s+(\w+)\s*=',
             "VARIABLE DECLARATION: You're creating a '{}' variable named '{}' and giving it an initial value.",
             "DETAILED: C++ is 'statically typed,' meaning you must tell the compiler what kind of data a variable holds. 'int' is for whole numbers, 'float/double' for decimals, 'char' for single characters, and 'bool' for true/false. This helps the computer reserve the right amount of memory (e.g., usually 4 bytes for an int).",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'string\s+(\w+)\s*=',
             "STRING VARIABLE: You're creating a text variable named '{}'.",
             "DETAILED: Unlike 'char', which is one letter, 'std::string' is an object that handles a sequence of characters. It automatically manages memory for you, growing or shrinking as the text changes. You need <string> included at the top to use it.",
             "https://en.cppreference.com/w/cpp/string/basic_string"),

            # --- CONTROL FLOW ---
            (r'if\s*\((.*)\)',
             "IF STATEMENT: If the condition ({}) is true, the code inside the following {{ }} will run.",
             "DETAILED: The expression inside the parentheses is evaluated as a boolean. In C++, any non-zero number is 'true' and zero is 'false'. Use '==' for comparison; a common beginner mistake is using a single '=', which assigns a value instead of comparing it.",
             "https://en.cppreference.com/w/cpp/language/if"),

            (r'for\s*\((.*);(.*);(.*)\)',
             "FOR LOOP: This loop will repeat code based on three rules: initialization, condition, and increment.",
             "DETAILED: A 'for' loop is ideal when you know exactly how many times to repeat. 1. The first part runs once. 2. The second part is checked before every loop. 3. The third part runs after every loop (usually to increment a counter).",
             "https://en.cppreference.com/w/cpp/language/for"),

            (r'while\s*\((.*)\)',
             "WHILE LOOP: This repeats the code as long as ({}) stays true.",
             "DETAILED: The 'while' loop is a 'pre-test' loop. It checks the condition first. If the condition is false at the very start, the code inside the loop will never run even once. Watch out for 'infinite loops' where the condition never becomes false!",
             "https://en.cppreference.com/w/cpp/language/while"),

            (r'do\s*\{',
             "DO-WHILE LOOP: This loop will execute the code block at least once before checking the condition.",
             "DETAILED: Unlike a standard while loop, the 'do-while' checks the condition at the end of the block. This is perfect for menus or user input where you need to ask the user a question at least once.",
             "https://en.cppreference.com/w/cpp/language/do"),

            (r'switch\s*\((.*)\)',
             "SWITCH CASE: This is a cleaner way to write multiple 'if-else' checks for a single variable.",
             "DETAILED: The 'switch' evaluates an expression and jumps to the matching 'case' label. It's often faster than many 'if' statements. Crucially, you usually need a 'break;' statement at the end of each case, or the code will 'fall through' to the next case.",
             "https://en.cppreference.com/w/cpp/language/switch"),

            # --- I/O & TERMINATION ---
            (r'cout\s*<<\s*(.*);',
             "OUTPUT: This sends '{}' to be printed on the screen.",
             "DETAILED: 'std::cout' stands for 'character output'. The '<<' operator is called the 'insertion operator.' You can chain them together, for example: cout << 'Age: ' << age << endl;",
             "https://en.cppreference.com/w/cpp/io/cout"),

            (r'cin\s*>>\s*(\w+);',
             "INPUT: This pauses the program to wait for the user to type something and saves it in '{}'.",
             "DETAILED: 'std::cin' (character input) uses the '>>' (extraction) operator. It reads from the keyboard. Note that cin stops reading at the first space it hits; to read a whole line of text, you should use 'getline()'.",
             "https://en.cppreference.com/w/cpp/io/cin"),

            (r'return\s+(.*);',
             "RETURN: This ends the current function and sends the value '{}' back to whoever called it.",
             "DETAILED: In 'main()', returning 0 signals that the program finished without errors. In other functions, 'return' is how you pass the result of a calculation back to the rest of the program.",
             "https://en.cppreference.com/w/cpp/language/return"),
        ]
    
    # ... (rest of your explain_line and explain_more methods)
    def explain_line(self, line: str) -> str:
        """Returns the short, beginner-friendly summary."""
        line = line.strip()
        if not line or line in ["{", "}"]:
            return "..."
            
        for pattern, summary, _, _ in self.rules:
            match = re.search(pattern, line)
            if match:
                # Format the summary with the captured groups from the regex
                return summary.format(*match.groups())
        
        return "I'm watching! That looks like a custom line. Keep going!"

    def explain_more(self, line: str) -> Optional[Tuple[str, str]]:
        """Returns the technical details and a documentation link."""
        line = line.strip()
        if not line:
            return None
            
        for pattern, _, detail, url in self.rules:
            match = re.search(pattern, line)
            if match:
                return (detail.format(*match.groups()), url)
        
        return None

    def get_options(self, line: str) -> List[str]:
        """Checks if a 'Detailed' view is available for this line."""
        if self.explain_more(line) is not None:
            return ['more']
        return []
