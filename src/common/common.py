import os

# constants that can be used
CONST_ZERO = '@0'
CONST_ASSERTION_DISABLED = '$assertionsDisabled'

# if you load an anonymous variable name using push, then use the 
# instruction line index (self.current_method().pc - 1) as the variable name
# if you load a variable from a class the method name is None
def constant_name(variable_name, class_name, method_name = None):
    parts = [class_name, method_name, variable_name]
    parts = filter((lambda x: x != None), parts)
    parts = map(str, parts)
    return ":".join(parts)

def abs_method_name(class_name, method_name):
    parts = [class_name, method_name]
    parts = filter((lambda x: x != None), parts)
    parts = map(str, parts)
    return ":".join(parts)

def all_file_paths(dir: str):
    paths = []
    parent = dir.split(os.sep)[-1]
    for root, _, filenames in os.walk(dir):
        root_parts = root.split(os.sep)
        packages = root_parts[root_parts.index(parent) + 1:]
        for name in filenames:
            paths.append((
                str.join("/", [*packages, os.path.splitext(name)[0]]), 
                os.path.join(root, name)
            ))
    
    return paths
