from pathlib import Path
import os
import sys
from google.genai import types

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


def _get_outside_directory_error(directory: str) -> str:
    return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'


def _get_not_is_dir_error(directory: str) -> str:
    return f'Error: "{directory}" is not a directory'


def _get_not_is_file_error(file_name: str) -> str:
    return f'Error: "{file_name}" is not a file'


def _get_file_info(f: Path) -> str:
    return f" - {f.name}: file_size={os.path.getsize(f)} bytes, is_dir={f.is_dir()}"


def _pretty_format_files_info(path: Path) -> str:
    return "\n".join(_get_file_info(f) for f in path.glob("*"))


def get_files_info(working_directory: Path | str, directory: str | None = None) -> str:
    wd = Path(working_directory).resolve(strict=False)
    if directory is None or directory == ".":
        directory = "."
    path = (wd / directory).resolve(strict=False)
    dirname = "current" if directory == "." else f"'{directory}'"
    out = f"Result for {dirname} directory:\n"
    # if directory is not even a directory
    if not path.is_relative_to(wd):
        out += "    " + _get_outside_directory_error(directory)
    elif not path.is_dir():
        out += "    " + _get_not_is_dir_error(directory)
    else:
        out += _pretty_format_files_info(path)
    return out


def _truncate(contents: str, file_path: str) -> str:
    return f'{contents}[...File "{file_path}" truncated at 10000 characters"]'


def get_file_content(working_directory: Path | str, file_path: str) -> str:
    wd = Path(working_directory).resolve(strict=False)
    path = (wd / file_path).resolve(strict=False)
    if not path.is_relative_to(wd):
        return _get_outside_directory_error(file_path)
    if not path.is_file():
        return _get_not_is_file_error(file_path)
    contents = path.read_text()
    if len(contents) > 1000:
        return _truncate(contents, file_path)
    return contents


def write_file(working_directory: Path | str, file_path: str, content: str):
    wd = Path(working_directory).resolve(strict=False)
    path = (wd / Path(file_path)).resolve(strict=False)
    if not path.is_relative_to(wd):
        return _get_outside_directory_error(file_path)
    try:
        if not path.exists():
            path.touch(exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
    except Exception as e:
        return f"Error: {e}"
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
