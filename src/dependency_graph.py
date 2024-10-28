from interpreter import SimpleInterpreter, Method, bytecode_to_methodname
from dataclasses import dataclass   
from collections import deque
import jpamb_utils as utils
import json


def create_dependency_graph(methodId: str, inputs: list[str]) -> list[str]:
    method = methodId.load()
    # Convert all inputs to integers
    inputs = [[l.tolocal() for l in i.value] if isinstance(
        i, utils.IntListValue) or isinstance(i, utils.CharListValue) else i.tolocal() for i in inputs]
    interpreter = SimpleInterpreter(
        # heap=deque(),
        method_stack=deque(
            [Method(method["code"]["bytecode"], inputs, [], 0)])
    )

    # Step through the program and build the dependency graph
    # TODO: Handle other invokations than static
    limit = 1000
    dependencies = []
    while interpreter.step_count < limit and interpreter.done is None:
        next = interpreter.method_stack[-1].bytecode[interpreter.method_stack[-1].pc]
        if next["opr"] == "invoke" and next["access"] == "static":
            method_name = bytecode_to_methodname(next)
            dependencies.append(method_name)
    return dependencies

# TODO: Merge the dependency graph with a potentially already existing one
def run_tests(tests: list[tuple[str, list[str]]]):
    dependency_graph: dict[str, list[str]] = {}
    for (methodId, inputs) in tests:
        dependencies = create_dependency_graph(methodId, inputs)
        dependency_graph[methodId] = dependencies
    json_dependency_graph = json.dumps(dependency_graph)
    return json_dependency_graph
