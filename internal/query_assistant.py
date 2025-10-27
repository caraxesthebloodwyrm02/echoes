import sys
import os

# Exclude the core directory to avoid conflicts with standard library
project_root = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(project_root, 'core')
if core_dir in sys.path:
    sys.path.remove(core_dir)

from assistant_v2_core import EchoesAssistantV2

def main():
    assistant = EchoesAssistantV2()

    query = """Please provide a plan to initiate analysis of the following files:
- e:\Projects\Echoes\ATLAS\Project Directory Overview.png
- e:\Projects\Echoes\ATLAS\Project Progress_ Day 1 Summary.png
- e:\Projects\Echoes\ATLAS\Software Project Directory Structure.png
- e:\Projects\Echoes\ATLAS\Strategic Partnership Outline.png

And recommend a strategy to approach OpenAI through medium, with a note about my aim: initiating communication and making a strong first impression through pitch."""

    response = assistant.chat(query)
    print("EchoesAssistantV2 Response:")
    print("=" * 50)
    print(response)

if __name__ == "__main__":
    main()
