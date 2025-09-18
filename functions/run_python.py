from pathlib import Path
import subprocess
import os
from .get_files_info import _get_outside_directory_error
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a specified python script.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path of the script you want to run.",
            ),
        },
    ),
)


def run_python_file(working_directory: Path | str, file_path: str) -> str:
    wd = Path(working_directory).resolve(strict=False)
    path = (wd / file_path).resolve(strict=False)
    if not path.is_relative_to(wd):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not path.exists():
        return f'Error: File "{file_path}" not found.'
    if path.suffix != "py":
        return f'Error: "{file_path}" is not a Python file.'
    capture = subprocess.run(
        ["python", file_path],
        cwd=wd,
        timeout=30,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = f"STDOUT: {capture.stdout}\nSTDERR: {capture.stderr}\n"
    if capture.returncode != 0:
        output += f"Process exited with code {capture.returncode}\n"
    return output
