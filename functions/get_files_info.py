from pathlib import Path
from google.genai import types
from .utils import (
    INDENT,
    outside_directory_error,
    not_a_directory_error,
    pretty_format_files_info,
)

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)


def get_files_info(working_directory: Path | str, directory: str | None = None) -> str:
    wd = Path(working_directory).resolve(strict=False)
    directory = directory or "."
    path = (wd / directory).resolve(strict=False)
    printable_dirname = "current" if directory == "." else f"'{directory}'"
    message = f"Result for {printable_dirname} directory:\n"
    if not path.is_relative_to(wd):
        return message + INDENT + outside_directory_error(directory)
    elif not path.is_dir():
        return message + INDENT + not_a_directory_error(directory)
    else:
        return message + pretty_format_files_info(path)
