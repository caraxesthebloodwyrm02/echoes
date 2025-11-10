import ast

with open("api/config.py") as f:
    content = f.read()
    tree = ast.parse(content)
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    print("Classes:", sorted(classes))
