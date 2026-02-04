import re
from typing import Optional, Tuple, List

class SenseiLogic:
    def __init__(self):
        # Each rule: (pattern, short_summary, detailed_explanation, docs_url)
        self.rules = [
            (r'#include\s*<(.*)>',
             "🧰 HEADER INCLUDE: #include <{}> tells the preprocessor to copy the header's declarations into your source so the compiler can use them.",
             "DETAILED: The #include directive is handled by the preprocessor before compilation: it literally inserts the contents of the named header into your translation unit. "
             "Headers typically declare types, functions, templates and objects that other translation units can use. For example, <iostream> declares stream classes such as std::istream and std::ostream "
             "and provides predefined objects like std::cin and std::cout; the header itself is not a class — it exposes declarations that the compiler and linker use.",
             "https://en.cppreference.com/w/cpp/header/iostream"),

            (r'using namespace std;',
             "📝 NAMESPACE DIRECTIVE: using namespace std; brings symbols from the std namespace into the current scope so you can write 'cout' instead of 'std::cout'.",
             "DETAILED: Namespaces group related declarations to avoid name collisions (e.g., std::vector vs mylib::vector). 'using namespace std;' imports all names from std into the current scope, which is convenient but can cause "
             "ambiguous name conflicts in larger projects. Prefer using explicit qualification (std::) or selective using-declarations (e.g., using std::cout) for clarity and to avoid collisions.",
             "https://en.cppreference.com/w/cpp/language/namespace"),

            (r'int\s+main\(\)',
             "🚀 PROGRAM ENTRY: int main() is the function where program execution starts; its return value is the process exit code.",
             "DETAILED: The runtime calls main as the program's entry point. The return value is an integer exit status returned to the operating system (0 commonly means success). main can also accept arguments "
             "(int argc, char** argv) to access command-line parameters. In standard C++, falling off the end of main returns 0 implicitly.",
             "https://en.cppreference.com/w/cpp/language/main_function"),

            (r'int\s+(\w+)\s*=',
             "📦 INTEGER VARIABLE: Declares an int named '{}' to hold whole numbers.",
             "DETAILED: 'int' is a built-in signed integer type used to store whole numbers. Its size is implementation-defined (commonly 32 bits on desktop platforms). The '=' indicates the variable is being initialized. "
             "Integers use two's complement on most systems and have defined ranges determined by the implementation (see <limits>).",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'float\s+(\w+)\s*=',
             "🥛 FLOATING-POINT VARIABLE: Declares a float named '{}' to hold a decimal (approximate) number.",
             "DETAILED: 'float' is a single-precision floating-point type (typically IEEE 754 single precision). It stores approximate real numbers with limited precision (about 6–9 decimal digits). "
             "For greater precision, use 'double' or long double. Floating-point arithmetic introduces rounding and precision considerations.",
             "https://en.cppreference.com/w/cpp/language/types#Fundamental_types"),

            (r'char\s+(\w+)\s*=',
             "🔤 CHARACTER / BYTE: Declares a char named '{}' which typically holds a single byte used for characters or small integer values.",
             "DETAILED: 'char' is an integer type that usually occupies one byte. It's commonly used for characters (ASCII or UTF-8 code units) but behaves as an integer type for arithmetic. "
             "Its signedness is implementation-defined (signed or unsigned char). For text, consider std::string (which manages sequences of char).",
             "https://en.cppreference.com/w/cpp/language/types"),

            (r'cin\s*>>\s*(\w+);',
             "👂 INPUT EXTRACTION: cin >> {}; reads formatted input from standard input into the variable '{}'.",
             "DETAILED: The extraction operator (>>) reads characters from std::cin, parses them according to the target type, converts them and stores the result into the variable. "
             "Stream state flags (goodbit, failbit, badbit, eofbit) indicate success or failure of extraction; you should check the stream state to handle input errors robustly.",
             "https://en.cppreference.com/w/cpp/io/cin"),

            (r'cout\s*<<\s*(.*);',
             "📢 OUTPUT INSERTION: cout << '{}' sends the value/expression to standard output using the stream insertion operator (<<).",
             "DETAILED: The insertion operator (<<) serializes the provided value to std::cout by calling the appropriate operator<< overload. "
             "You can chain insertions (std::cout << a << b). Note that std::endl inserts a newline and flushes the stream; '\\n' is just a newline character without forcing an immediate flush.",
             "https://en.cppreference.com/w/cpp/io/cout"),

            (r'if\s*\((.*)\)',
             "🛣️ CONDITIONAL BRANCH: if ({}) evaluates the expression and executes the following block only if it is true.",
             "DETAILED: The condition inside if(...) is contextually converted to bool. C++ supports logical operators (&&, ||, !) and short-circuit evaluation. Non-boolean values convert to bool according to rules (e.g., 0 -> false). "
             "Use parentheses to clarify complex expressions and consider explicit boolean expressions to avoid accidental conversions.",
             "https://en.cppreference.com/w/cpp/language/if"),

            (r'while\s*\((.*)\)',
             "🔄 WHILE LOOP: while ({}) repeats the loop body as long as the condition remains true.",
             "DETAILED: The condition is evaluated before each iteration. Ensure loop control variables or state change within the loop, or you risk an infinite loop. For index-based loops, a for-loop is often more concise and less error-prone.",
             "https://en.cppreference.com/w/cpp/language/while"),

            (r'return\s+0;',
             "🏁 RETURN FROM MAIN: return 0; indicates successful program termination to the OS.",
             "DETAILED: Returning 0 conventionally signals success; non-zero values indicate different error conditions. In main specifically, reaching the closing brace implicitly returns 0 if no return is present.",
             "https://en.cppreference.com/w/cpp/language/return"),
        ]

    def explain_line(self, line: str) -> str:
        """
        Return the short explanation for the given source code line (keeps existing behavior).
        """
        line = line.strip()
        if not line:
            return "..."
        for pattern, summary, _, _ in self.rules:
            match = re.search(pattern, line)
            if match:
                return summary.format(*match.groups())
        return "I'm watching! That looks like a custom line. Keep going!"

    def explain_more(self, line: str) -> Optional[Tuple[str, str]]:
        """
        Return a tuple (detailed_explanation, docs_url) for the matched line.
        If no detailed explanation is available, return None.
        """
        line = line.strip()
        if not line:
            return None
        for pattern, _, detail, url in self.rules:
            match = re.search(pattern, line)
            if match:
                return (detail.format(*match.groups()), url)
        return None

    def get_options(self, line: str) -> List[str]:
        """
        Return a list of available options for the line's explanation (e.g., ['more']).
        """
        if self.explain_more(line) is not None:
            return ['more']
        return []
