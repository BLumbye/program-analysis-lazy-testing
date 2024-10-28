# Tests should be run if one of these cases are true:
# 1. The code for the test itself is changed
# 2. Any of the dependencies of the test are changed
# 3. The test is new - not present in existing dependency graph

import jsondiff as jd
from jsondiff import diff
import json
import dependency_graph


def compare_bytecode(dependency_graph, bc1, bc2):
    # Construct the diff
    methods1 = sorted(bc1["methods"], key=lambda x: x["name"])
    methods2 = sorted(bc2["methods"], key=lambda x: x["name"])
    methods_diff = diff(methods1, methods2)

    if methods_diff == {}:
        return

    print(methods_diff)

    # Analyze the diff to find the impacted methods
    changed_methods = [] 
    changed_tests = []
    added_tests = []
    
    for method_diff in methods_diff:
        if method_diff == jd.insert:
            for (index, new_method) in methods_diff[method_diff]:
                # Check if the method is a test
                if any(annotation.type == "utils/Test" for annotation in new_method["annotations"]):
                    added_tests.append(new_method["name"])
        elif isinstance(method_diff, int):
            index = method_diff

            # Check if a normal method was changed to be a test
            if "annotations" in methods_diff[index] and any(annotation["type"] == "utils/Test" for annotation in methods2[index]["annotations"]):
                added_tests.append(methods2[index]["name"])

            # Check if there are changes in the bytecode
            if not ("code" in methods_diff[index] and "bytecode" in methods_diff[index]["code"]):
                continue

            # Check if the method is a test
            if any(annotation["type"] == "utils/Test" for annotation in methods2[index]["annotations"]):
                changed_tests.append(methods2[index]["name"])
            else:
                changed_methods.append(methods2[index]["name"])
    
    # Check whether any of the changed methods are in dependency graphs

            


if __name__ == "__main__":
    bc1 = json.loads(open("codebases/constant_becomes_equal/previous/decompiled/Simple.json", "r").read())
    bc2 = json.loads(open("codebases/constant_becomes_equal/next/decompiled/Simple.json", "r").read())
    dependencies = dependency_graph.run_tests([""])

    compare_bytecode({}, bc1, bc2)