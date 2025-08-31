import os

def print_dbt_structure(path, indent=0, max_depth=3):
    if indent > max_depth:
        return
    for entry in sorted(os.listdir(path)):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            print('    ' * indent + entry + '/')
            print_dbt_structure(full_path, indent + 1, max_depth)
        elif entry.endswith(('.sql', '.yml','.py','.txt','md')):
            print('    ' * indent + entry)

# Change this to your dbt project path
print_dbt_structure(r"C:\PythonProject\RealEstate\dbt\real_estate_dbt")