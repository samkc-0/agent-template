from pathlib import Path
from google.genai import types
from .utils import outside_directory_error, not_a_file_error, truncate


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Gets the content of the file at the specified path, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to read the content of, relative to the working directory",
            ),
        },
    ),
)


def get_file_content(working_directory: Path | str, file_path: str) -> str:
    wd = Path(working_directory).resolve(strict=False)
    path = (wd / file_path).resolve(strict=False)
    if not path.is_relative_to(wd):
        return outside_directory_error(file_path)
    if not path.is_file():
        return not_a_file_error(file_path)
    contents = path.read_text()
    if len(contents) > 1000:
        return truncate(contents, file_path)
    return contents

