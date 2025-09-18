from .get_files_info import get_files_info, get_file_content, write_file
from .run_python import run_python_file
from google.genai import types


callable_functions = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(function_call_part, verbose=False):
    if function_call_part.name not in callable_functions:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"unknown function: {function_call_part.name}"},
                )
            ],
        )

    if verbose:
        print(f"calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - calling function {function_call_part.name}")
    working_directory = "./calculator"
    args = [working_directory, *function_call_part.args]
    result = callable_functions[function_call_part.name](*args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": result},
            )
        ],
    )
