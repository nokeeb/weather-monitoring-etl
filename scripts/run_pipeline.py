from pathlib import Path
import os
import sys
PROJECT_ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(PROJECT_ROOT))

from src import pipeline

def main():
    exit_code=pipeline.main()
    print('Done!')
    return exit_code

if __name__=='__main__':
    main()