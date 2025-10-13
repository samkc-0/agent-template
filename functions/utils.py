import os
from pathlib import Path


INDENT = "    "


def outside_directory_error(directory: str) -> str:
    return f'Error: "{directory}" is outside the permitted working directory'


def not_a_directory_error(directory: str) -> str:
    return f'Error: "{directory}" is not a directory'


def not_a_file_error(file_name: str) -> str:
    return f'Error: "{file_name}" is not a file'


def show_file_info(f: Path) -> str:
    return f" - {f.name}: file_size={os.path.getsize(f)} bytes, is_dir={f.is_dir()}"


def pretty_format_files_info(path: Path) -> str:
    return "\n".join(show_file_info(f) for f in path.glob("*"))


def truncate(contents: str, file_path: str) -> str:
    return f'{contents}[...File "{file_path}" truncated at 10000 characters"]'
