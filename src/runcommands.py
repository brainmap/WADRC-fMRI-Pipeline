"""This file contains commands that are used to run scripts and binaries
standalone or in the shell."""
import subprocess

## Runs an external (shell) command, and returns a tuple
# consisting of (stdout, stderr) from the external command.
def run(cmd):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return sp.communicate()
