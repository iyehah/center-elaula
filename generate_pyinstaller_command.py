import os

def generate_add_data_args(base_path):
    add_data_args = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            # Get the full path of the file
            full_file_path = os.path.join(root, file)
            # Get the relative path inside the base folder
            relative_path = os.path.relpath(root, base_path)
            # Construct the --add-data argument
            if relative_path == ".":
                add_data_args.append(f'--add-data "{full_file_path};."')
            else:
                add_data_args.append(f'--add-data "{full_file_path};{relative_path}"')
    return " ".join(add_data_args)

# Base path of your project
base_path = "."

# Generate the --add-data arguments
add_data_args = generate_add_data_args(base_path)

# Generate the full PyInstaller command
pyinstaller_command = f'pyinstaller --onefile --windowed {add_data_args} app.py'

# Print the command
print(pyinstaller_command)