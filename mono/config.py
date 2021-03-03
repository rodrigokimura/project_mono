'''
File: FILENAME:config.py
Author: Rodrigo Eiti Kimura
Description: Initial configuration
'''
import subprocess

commands = [
    ['python', 'manage.py', 'migrate'],
    ['python', 'manage.py', 'loaddata', 'finance/fixtures/icon.json']
]

for command in commands:
    print(f"[INFO] Running command: {' '.join(command)}")
    Output = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    stdout,stderr = Output.communicate()
    
    if stdout is not None: print(f"[OUTPUT] {stdout.decode()}")
    if stderr is not None: print(f"[ERROR] {stderr.decode()}")
