from pathlib import Path
import subprocess
from .utils import outside_directory_error
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
        return outside_directory_error(file_path)

    if not path.exists():
        return f'Error: File "{file_path}" not found.'

    capture = subprocess.run(
        ["python", file_path],
        cwd=wd,
        timeout=30,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = ""

    if capture.stdout:
        output += f"STDOUT: {capture.stdout.decode('utf-8')}\n"

    if capture.stderr:
        output += f"\nSTDERR: {capture.stderr.decode()}\n"

    if capture.returncode != 0:
        output += f"Process exited with code {capture.returncode}\n"

    return output
