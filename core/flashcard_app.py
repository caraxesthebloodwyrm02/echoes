# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Flashcard App for Python Development and Data Processing Techniques

Based on NotebookLM briefing content.
"""

import random
from typing import Dict

# Flashcard data from the briefing
FLASHCARDS = [
    {
        "question": "What is the primary method for parsing command-line arguments in Python?",
        "answer": "Using the sys.argv list, which contains all arguments passed to the script.",
        "category": "CLI Implementation",
    },
    {
        "question": "How do you check for a specific flag like '--break' in command-line arguments?",
        "answer": "Use a list comprehension to iterate through sys.argv and find an argument containing the substring.",
        "category": "CLI Implementation",
    },
    {
        "question": "What libraries are used for advanced breakpoint implementation with interactive features?",
        "answer": "sys, pexpect, and curses for process control, terminal interaction, and screen initialization.",
        "category": "CLI Implementation",
    },
    {
        "question": "What is JSON and what data types does it store?",
        "answer": "JSON (JavaScript Object Notation) is a lightweight, easy-to-read data format for data interchange. It stores strings, numbers, booleans, and complex structures like dictionaries, arrays, and objects.",
        "category": "JSON Handling",
    },
    {
        "question": "How do you convert a Python dictionary to a JSON string?",
        "answer": "Use the json.dumps() method from the built-in json library.",
        "category": "JSON Handling",
    },
    {
        "question": "How do you reconstruct a Python object from a JSON string?",
        "answer": "Use the json.loads() method to deserialize the JSON string back into a Python object.",
        "category": "JSON Handling",
    },
    {
        "question": "What are the six steps in the high-level Python data analysis workflow?",
        "answer": "1. Define Data Types, 2. Define Input Datasets, 3. Convert to DataFrames, 4. Explore and Clean Datasets, 5. Perform Data Manipulation, 6. Generate Visualizations.",
        "category": "Data Analysis",
    },
    {
        "question": "Which libraries are mentioned for data manipulation and analysis?",
        "answer": "pandas (for DataFrames), numpy, scikit-learn, and matplotlib/seaborn (for visualizations).",
        "category": "Data Analysis",
    },
    {
        "question": "What is the purpose of exploring and cleaning datasets?",
        "answer": "To inspect data for issues, handle missing values through imputation (mean, median), and address outliers.",
        "category": "Data Analysis",
    },
    {
        "question": "What are the key custom commands available in the PowerShell environment for Python venv management?",
        "answer": "pyenv (activate environment), pyenv-create (create/recreate), pyenv-list (show available), pyenv-remove (delete environment).",
        "category": "Dev Environment",
    },
    {
        "question": "What is the default Python interpreter path setting in VS Code?",
        "answer": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
        "category": "Dev Environment",
    },
    {
        "question": "Which linting tools are enabled in the VS Code configuration?",
        "answer": "python.linting.flake8Enabled and python.linting.ruffEnabled are true, while pylintEnabled is false.",
        "category": "Dev Environment",
    },
    {
        "question": "What is the line length setting for the Black code formatter?",
        "answer": "--line-length 88",
        "category": "Dev Environment",
    },
    {
        "question": "What terminal profile is set as default on Windows?",
        "answer": "PowerShell (project)",
        "category": "Dev Environment",
    },
    {
        "question": "How is the .env file made available in VS Code?",
        "answer": "Through the setting python.envFile set to ${workspaceFolder}/.env",
        "category": "Dev Environment",
    },
]


class FlashcardApp:
    """Interactive flashcard application"""

    def __init__(self):
        self.flashcards = FLASHCARDS.copy()
        self.current_card = None
        self.show_answer = False
        self.score = {"correct": 0, "total": 0}

    def get_random_card(self) -> Dict:
        """Get a random flashcard"""
        return random.choice(self.flashcards)

    def show_card(self):
        """Display current card"""
        if not self.current_card:
            self.current_card = self.get_random_card()

        print(f"\nCategory: {self.current_card['category']}")
        print(f"Question: {self.current_card['question']}")

        if self.show_answer:
            print(f"Answer: {self.current_card['answer']}")
            print("\nCommands: (c)orrect, (w)rong, (n)ext question, (q)uit")
        else:
            print("\nCommands: (s)how answer, (n)ext question, (q)uit")

    def run(self):
        """Main application loop"""
        print("Welcome to Python Development Flashcards!")
        print(
            "Press 's' to show answer, 'c' for correct, 'w' for wrong, 'n' for next, 'q' to quit"
        )

        while True:
            self.show_card()

            try:
                command = input("\n> ").strip().lower()
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

            if command == "q":
                print(f"\nFinal Score: {self.score['correct']}/{self.score['total']}")
                break
            elif command == "s" and not self.show_answer:
                self.show_answer = True
            elif command == "c" and self.show_answer:
                self.score["correct"] += 1
                self.score["total"] += 1
                self.current_card = None
                self.show_answer = False
            elif command == "w" and self.show_answer:
                self.score["total"] += 1
                self.current_card = None
                self.show_answer = False
            elif command == "n":
                self.current_card = None
                self.show_answer = False
            else:
                print("Invalid command. Try again.")


def main():
    """Run the flashcard app"""
    app = FlashcardApp()
    app.run()


if __name__ == "__main__":
    main()
