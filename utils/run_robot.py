import subprocess
import os

# Chemin absolu ou relatif vers le dossier du robot
robot_path = r"C:\Users\Public\Documents\Robot\Robocorp"

os.chdir(robot_path)
subprocess.run([
    "rcc", "task", "run",
    "--robot", "robot.yaml",
    "--task", "yakaedi"
])