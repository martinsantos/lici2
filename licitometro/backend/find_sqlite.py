import os

def find_sqlite_files(directory):
    sqlite_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'sqlite' in content.lower():
                        sqlite_files.append(filepath)
    return sqlite_files

directory = r'd:/D/ultima milla/2024/MKT 2024/licitometro/licitometro91/project/CascadeProjects/windsurf-project/licitometro'
sqlite_files = find_sqlite_files(directory)

print("Files containing SQLite references:")
for file in sqlite_files:
    print(file)
