from dragonpy.core.gui import BaseTkinterGUI

class VectrexGUI(BaseTkinterGUI):
    """
    The complete Tkinter GUI window
    """
    def __init__(self, *args, **kwargs):
        super(VectrexGUI, self).__init__(*args, **kwargs)


#------------------------------------------------------------------------------


def test_run():
    import sys
    import os
    import subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
        "--verbosity", "5",
        "--machine", "Vectrex", "run",
        "--max_ops", "1",
        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()