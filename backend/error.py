from enum import Enum

class SyntaxErrorType(Enum):
    INVALID_STATEMENT = "Invalid statement"
    INVALID_INDENTATION = "Invalid indentation"
    MISSING_COLON = "Missing colon"
    MISSING_PARENTHESIS = "Missing parenthesis"
    INVALID_CLASS_DEFINITION = "Invalid class definition"
    INVALID_METHOD_DEFINITION = "Invalid method definition"
    INVALID_INHERITANCE = "Invalid inheritance"
    INVALID_ARGUMENT = "Invalid argument"
    INVALID_EXPRESSION = "Invalid expression"
    MISSING_SETUP = "Missing setup method"
    INVALID_FUNCTION_DEFINITION = "Invalid function definition"
    INCOMPLETE_STATEMENT = "Incomplete statement"
    INVALID_PARAMETER = "Invalid parameter"
    INVALID_PRINT_ARGUMENT = "Invalid print argument"
    UNDEFINED_VARIABLE = "Undefined variable"
    UNDEFINED_FUNCTION = "Undefined function"
    UNDEFINED_CLASS = "Undefined class"
    UNDEFINED_METHOD = "Undefined method"
    INVALID_PARAMETER_COUNT = "Invalid parameter count"
    INVALID_ASSIGNMENT = "Invalid assignment"
    INVALID_OPERATOR = "Invalid operator"
    INVALID_TYPE = "Invalid type"
    INVALID_ACCESS = "Invalid access" 
    INVALID_THIS = "Invalid use of 'this' keyword"
    INVALID_PARENT = "Invalid use of 'parent' keyword"
    INVALID_RETURN = "Invalid return statement"
    INVALID_LOOP = "Invalid loop statement"
    INVALID_CONDITION = "Invalid condition"
    INVALID_BREAK = "Invalid break statement"
    INVALID_CONTINUE = "Invalid continue statement"
    INVALID_FUNCTION_CALL = "Invalid function call"
    INVALID_METHOD_CALL = "Invalid method call"
    INVALID_OBJECT_CREATION = "Invalid object creation"
    DUPLICATE_DEFINITION = "Duplicate definition"

class SyntaxError:
    def __init__(self, error_type: SyntaxErrorType, line: int, message: str):
        self.error_type = error_type
        self.line = line
        self.message = message

    def to_dict(self):
        return {
            "type": self.error_type.value,
            "line": self.line,
            "message": self.message
        }