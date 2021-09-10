import subprocess

def execute_command(command):
    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    return str(output)
