import os
import subprocess
import sys
from pathlib import Path

from ahkunwrapped import Script


def run():
    script_path = os.path.join(Path(__file__).resolve().parent, 'main.py')
    try:
        script = subprocess.run([sys.executable, script_path] + sys.argv[1:], stdout=subprocess.PIPE, check=True, encoding='utf-8', text=True)
        print(script.stdout)
        restart_rw()
    except subprocess.CalledProcessError as e:
        exit(e.returncode)


def restart_rw():
    Script("""
        AutoExec() {
            WinClose, ahk_exe RimWorldWin64.exe
            WinWaitClose,
            Run, C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe
        }
    """)


if __name__ == '__main__':
    run()
