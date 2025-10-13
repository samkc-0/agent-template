from pathlib import Path
from google.genai import types
from .utils import outside_directory_error


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="write content to the file at the specified path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to write to, relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file",
            ),
        },
    ),
)


def write_file(working_directory: Path | str, file_path: str, content: str):
    wd = Path(working_directory).resolve(strict=False)
    path = (wd / Path(file_path)).resolve(strict=False)

    if not path.is_relative_to(wd):
        return outside_directory_error(file_path)

    try:
        if not path.exists():
            path.touch(exist_ok=True)

        with open(path, "w") as f:
            f.write(content)

    except Exception as e:
        return f"Error: {e}"

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
