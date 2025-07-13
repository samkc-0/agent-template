from functions.get_files_info import get_file_content, get_files_info, write_file
from functions.run_python import run_python_file


def get_test_output(func):
    def wrapped(*args, **kwargs):
        out = func(*args, **kwargs)
        print(out)
        return out

    return wrapped


get_files_info = get_test_output(get_files_info)
get_file_content = get_test_output(get_file_content)
write_file = get_test_output(write_file)
run_python_file = get_test_output(run_python_file)

if __name__ == "__main__":
    """
    get_files_info("calculator", ".")
    get_files_info("calculator", "pkg")
    get_files_info("calculator", "/bin")
    get_files_info("calculator", "..")

    get_file_content("calculator", "lorem.txt")
    get_file_content("calculator", "main.py")
    get_file_content("calculator", "pkg/calculator.py")
    get_file_content("calculator", "/bin/cat")
    write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
    write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
    write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
    """

    run_python_file("calculator", "main.py")
    run_python_file("calculator", "tests.py")
    run_python_file("calculator", "../main.py")
    run_python_file("calculator", "nonexistent.py")
