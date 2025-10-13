from google.genai import types
from .get_files_info import get_files_info, schema_get_files_info
from .get_file_content import get_file_content, schema_get_file_content
from .write_file import write_file, schema_write_file
from .run_python import run_python_file, schema_run_python_file

available_schema = types.Tool(
    function_declarations=[
        schema_run_python_file,
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
    ]
)


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
        args = ", ".join(function_call_part.args)
        print(f"calling function: {function_call_part.name}({args})")
    else:
        print(f" - calling function {function_call_part.name}")
    working_directory = "./calculator"
    kwargs = {"working_directory": working_directory, **function_call_part.args}
    result = callable_functions[function_call_part.name](**kwargs)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": result},
            )
        ],
    )
