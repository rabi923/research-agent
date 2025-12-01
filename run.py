import os
import sys
from streamlit.web import cli as stcli

def main():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "research_agent", "ui", "app.py")
    
    sys.argv = ["streamlit", "run", app_path]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
