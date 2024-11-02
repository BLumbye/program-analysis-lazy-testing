from dataclasses import dataclass
import jpamb_utils as utils
import json


@dataclass
class JavaMethod:
    name: str
    bytecode: list
    params: list[utils.JvmType]
    returns: utils.JvmType
    is_test: bool = False


# @dataclass
# class JavaField:
#     name: str
#     type: utils.JvmType

@dataclass
class JavaClass:
    name: str
    methods: dict[str, JavaMethod]
    # fields: dict[str, JavaField]


def load_class(class_path: str) -> JavaClass:
    """
    Loads a decompiled Java class from a json file.
    """
    file = open(class_path, "rt")
    classJson = json.load(file)
    file.close()

    methods = {}
    for method in classJson["methods"]:
        methodName = method["name"]
        methodBytecode = method["code"]["bytecode"]
        is_test = any(annotation["type"] ==
                      "utils/Test" for annotation in method["annotations"])
        # Might not work for arrays
        params = []
        for param in method["params"]:
            params.append(param["type"]["base"])
        returns = method["returns"]["type"]["base"] if method["returns"]["type"] != None else None
        methods[methodName] = JavaMethod(
            methodName, methodBytecode, params, returns, is_test)

    return JavaClass(classJson["name"], methods)
