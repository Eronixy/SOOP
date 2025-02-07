from typing import List, Dict
from error import SyntaxError, SyntaxErrorType

class SyntaxAnalyzer:
    def __init__(self, tokens: List[Dict]):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        self.scope_level = 0
        self.in_class = False
        self.in_method = False
        self.has_setup = False
        self.current_class = None
        self.defined_classes = {}
        self.in_loop = False

    def current_token(self) -> Dict:
        while self.current < len(self.tokens) and self.tokens[self.current]["type"] == "NEWLINE":
            self.current += 1
        return self.tokens[self.current] if self.current < len(self.tokens) else None

    def peek_next(self) -> Dict:
        next_pos = self.current + 1
        while next_pos < len(self.tokens) and self.tokens[next_pos]["type"] == "NEWLINE":
            next_pos += 1
        return self.tokens[next_pos] if next_pos < len(self.tokens) else None

    def advance(self):
        self.current += 1
        while self.current < len(self.tokens) and self.tokens[self.current]["type"] == "NEWLINE":
            self.current += 1

    def expect(self, token_type: str) -> bool:
        if self.current_token()["type"] == token_type:
            self.advance()
            return True
        return False

    def add_error(self, error_type: SyntaxErrorType, message: str):
        line = self.current_token()["line"] if self.current_token() else 0
        self.errors.append(SyntaxError(error_type, line, message).to_dict())

    def analyze(self) -> List[Dict]:
        while self.current_token() and self.current_token()["type"] != "EOF":
            self.parse_statement()
        return self.errors
    
    def parse_statement(self):
        token = self.current_token()
        
        if not token:
            return
            
        if token["type"] == "DEFINE":
            self.parse_function_definition()
            
        elif token["type"] == "CLASS":
            self.parse_class_definition()

        elif token["type"] == "FOR":
            self.parse_for_loop()

        elif token["type"] == "WHILE":
            self.parse_while_statement()

        elif token["type"] in ["BREAK", "CONTINUE"]:
            self.parse_break_continue()
            
        elif token["type"] == "IF":
            self.parse_control_flow()
            
        elif token["type"] == "PRINT":
            self.parse_print_statement()
            
        elif token["type"] == "THIS":
            self.parse_this_access()
            
        elif token["type"] == "IDENTIFIER":
            identifiers = self.parse_identifier_list()
            
            next_token = self.current_token()
            if not next_token:
                self.add_error(SyntaxErrorType.INCOMPLETE_STATEMENT, 
                            "Unexpected end of statement")
                return
                
            if next_token["type"] == "ASSIGN":
                self.parse_multiple_assignment(identifiers)
            elif next_token["type"] == "DOT":
                if len(identifiers) > 1:
                    self.add_error(SyntaxErrorType.INVALID_METHOD_CALL,
                                "Method call cannot be performed on multiple identifiers")
                else:
                    self.parse_method_call(identifiers[0])
                
        elif token["type"] in ["INDENT", "DEDENT"]:
            self.handle_indentation()
            
        elif token["type"] == "NEWLINE":
            self.advance()
            
        else:
            self.advance()


    def parse_function_definition(self):
        self.advance() 
        
        if not self.expect("IDENTIFIER"):
            self.add_error(SyntaxErrorType.INVALID_FUNCTION_DEFINITION, "Expected function name")
            return

        if not self.expect("LPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected '('")
            return

        while self.current_token() and self.current_token()["type"] != "RPAREN":
            if not self.expect("IDENTIFIER"):
                self.add_error(SyntaxErrorType.INVALID_PARAMETER, "Expected parameter name")
                return
            if self.current_token() and self.current_token()["type"] == "COMMA":
                self.advance()

        if not self.expect("RPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")
            return

        if not self.expect("COLON"):
            self.add_error(SyntaxErrorType.MISSING_COLON, "Expected ':'")
            return

        if not self.expect("INDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected indented block")
            return

        while self.current_token() and self.current_token()["type"] != "DEDENT":
            self.parse_statement()

        if not self.expect("DEDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected dedent")

    def parse_assignment(self, identifier: str):
        current = self.current_token()
        if not current:
            return
            
        if current["type"] in ["ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", "MULTIPLY_ASSIGN", "DIVIDE_ASSIGN"]:
            self.advance()
            
            if self.current_token() and self.current_token()["type"] == "NEW":
                self.parse_object_creation()
                return
                
            self.parse_expression()
            
        elif current["type"] == "DOT":
            self.parse_method_call(identifier)
        else:
            self.add_error(
                SyntaxErrorType.INVALID_ASSIGNMENT,
                f"Expected assignment operator, got: {current['type']}"
            )
    
    def parse_object_creation(self):
        self.advance() 
        
        if not self.expect("IDENTIFIER"):
            self.add_error(SyntaxErrorType.INVALID_OBJECT_CREATION, "Expected class name")
            return
            
        class_name = self.tokens[self.current - 1]["value"]
        if class_name not in self.defined_classes:
            self.add_error(
                SyntaxErrorType.INVALID_OBJECT_CREATION,
                f"Cannot instantiate undefined class '{class_name}'"
            )
            return
            
        if not self.expect("LPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected '('")
            return
            
        arg_count = 0
        while self.current_token() and self.current_token()["type"] != "RPAREN":
            current = self.current_token()
            if current["type"] in ["STRING_LITERAL", "INTEGER_LITERAL", "FLOAT_LITERAL", "IDENTIFIER"]:
                self.advance()
                arg_count += 1
                if self.current_token() and self.current_token()["type"] == "COMMA":
                    self.advance()
            else:
                self.add_error(
                    SyntaxErrorType.INVALID_ARGUMENT,
                    f"Invalid constructor argument type: {current['type']}"
                )
                return

        if not self.expect("RPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")
            return
        
    def parse_class_definition(self):
        self.advance()
        
        if not self.expect("IDENTIFIER"):
            self.add_error(SyntaxErrorType.INVALID_CLASS_DEFINITION, "Expected class name")
            return

        class_name = self.tokens[self.current - 1]["value"]
        self.current_class = class_name
        self.in_class = True
        self.has_setup = False
        
        class_info = {
            "name": class_name,
            "parent": None,
            "methods": [],
            "attributes": set()
        }

        if self.current_token()["type"] == "INHERITS":
            self.advance()
            if not self.expect("IDENTIFIER"):
                self.add_error(SyntaxErrorType.INVALID_INHERITANCE, "Expected parent class name")
                return
            class_info["parent"] = self.tokens[self.current - 1]["value"]

        self.defined_classes[class_name] = class_info

        if self.current_token()["type"] == "INHERITS":
            self.advance()
            if not self.expect("IDENTIFIER"):
                self.add_error(SyntaxErrorType.INVALID_INHERITANCE, "Expected parent class name")
                return

        if not self.expect("COLON"):
            self.add_error(SyntaxErrorType.MISSING_COLON, "Expected ':'")
            return

        if not self.expect("INDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected indented block")
            return

        while self.current_token() and self.current_token()["type"] != "DEDENT":
            if self.current_token()["type"] in ["SETUP", "ACTION"]:
                self.parse_method_definition()
            else:
                self.advance()

        if not self.has_setup:
            self.add_error(
                SyntaxErrorType.INVALID_CLASS_DEFINITION,
                f"Class '{class_name}' missing required setup method"
            )

        if not self.expect("DEDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected dedent")
        
        self.in_class = False
        self.current_class = None

    def parse_method_definition(self):
        method_type = self.current_token()["type"] 
        self.advance()
        
        if method_type == "ACTION":
            if not self.expect("IDENTIFIER"):
                self.add_error(SyntaxErrorType.INVALID_METHOD_DEFINITION, "Expected method name")
                return
        elif method_type == "SETUP":
            self.has_setup = True
        
        if not self.expect("LPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected '('")
            return
            
        while self.current_token() and self.current_token()["type"] != "RPAREN":
            if not self.expect("IDENTIFIER"):
                self.add_error(SyntaxErrorType.INVALID_PARAMETER_COUNT, "Expected parameter name")
                return
            if self.current_token()["type"] == "COMMA":
                self.advance()
                
        if not self.expect("RPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")
            return
            
        if not self.expect("COLON"):
            self.add_error(SyntaxErrorType.MISSING_COLON, "Expected ':'")
            return
            
        if not self.expect("INDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected indented block")
            return
            
        while self.current_token() and self.current_token()["type"] != "DEDENT":
            if self.current_token()["type"] == "THIS":
                self.parse_this_assignment()
            elif self.current_token()["type"] == "PRINT":
                self.parse_print_statement()
            else:
                self.advance()
                
        if not self.expect("DEDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected dedent")

    def handle_indentation(self):
        if self.current_token()["type"] == "INDENT":
            self.scope_level += 1
        elif self.current_token()["type"] == "DEDENT":
            self.scope_level -= 1
        self.advance()


    def parse_control_flow(self):
        control_type = self.current_token()["type"]
        self.advance()

        if control_type == "WHILE":
            if not self.expect("LPAREN"):
                self.add_error(
                    SyntaxErrorType.MISSING_PARENTHESIS,
                    f"Expected '(' after {control_type.lower()}"
                )
                return

            while self.current_token() and self.current_token()["type"] != "RPAREN":
                self.advance()

            if not self.expect("RPAREN"):
                self.add_error(
                    SyntaxErrorType.MISSING_PARENTHESIS,
                    f"Expected ')' in {control_type.lower()} statement"
                )
                return
        else:
            self.parse_condition()

        if not self.expect("COLON"):
            self.add_error(
                SyntaxErrorType.MISSING_COLON,
                f"Expected ':' after {control_type.lower()} condition"
            )
            return

    def parse_print_statement(self):
        self.advance()
        
        if not self.expect("LPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected '(' after print")
            return
            
        first_arg = True
        while self.current_token() and self.current_token()["type"] != "RPAREN":
            if not first_arg:
                if not self.expect("COMMA"):
                    self.add_error(SyntaxErrorType.INVALID_PRINT_ARGUMENT, "Expected ',' between print arguments")
                    return
                    

            if not self.parse_print_argument():
                return
                
            first_arg = False
        
        if not self.expect("RPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")
            return

    def parse_print_argument(self):
        current = self.current_token()
        if not current:
            self.add_error(SyntaxErrorType.INVALID_PRINT_ARGUMENT, "Unexpected end of print statement")
            return False
            
        if not self.parse_print_value():
            return False
            
        while self.current_token() and self.current_token()["type"] == "PLUS":
            self.advance() 
            if not self.parse_print_value():
                return False
                
        return True

    def parse_print_value(self):
        current = self.current_token()
        if not current:
            self.add_error(SyntaxErrorType.INVALID_PRINT_ARGUMENT, "Unexpected end of print statement")
            return False
            
        if current["type"] in ["STRING_LITERAL", "INTEGER_LITERAL", "FLOAT_LITERAL"]:
            self.advance()
        elif current["type"] == "IDENTIFIER":
            self.advance()
            if self.current_token() and self.current_token()["type"] == "DOT":
                self.advance()
                if not self.expect("IDENTIFIER"):
                    self.add_error(SyntaxErrorType.INVALID_PRINT_ARGUMENT, "Expected identifier after '.'")
                    return False
        elif current["type"] == "THIS":
            self.advance()
            if not self.expect("DOT"):
                self.add_error(SyntaxErrorType.INVALID_THIS, "Expected '.' after 'this'")
                return False
            if not self.expect("IDENTIFIER"):
                self.add_error(SyntaxErrorType.INVALID_THIS, "Expected attribute name after 'this.'")
                return False
        else:
            self.add_error(SyntaxErrorType.INVALID_PRINT_ARGUMENT, "Invalid print argument")
            return False
            
        return True

        
    def parse_this_reference(self):
        self.advance()
        
        if not self.expect("DOT"):
            self.add_error(SyntaxErrorType.INVALID_THIS, "Expected '.' after 'this'")
            return
            
        if not self.expect("IDENTIFIER"):
            self.add_error(SyntaxErrorType.INVALID_THIS, "Expected attribute name after 'this.'")
            return

    def parse_assignment(self, identifier: str):
        self.advance()
        
        if self.current_token()["type"] == "NEW":
            self.advance() 
            
            if not self.expect("IDENTIFIER"):
                self.add_error(SyntaxErrorType.INVALID_OBJECT_CREATION, "Expected class name")
                return
                
            if not self.expect("LPAREN"):
                self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected '('")
                return
                
            while self.current_token() and self.current_token()["type"] != "RPAREN":
                current = self.current_token()
                if current["type"] in ["STRING_LITERAL", "INTEGER_LITERAL", "FLOAT_LITERAL", "IDENTIFIER"]:
                    self.advance()
                    if self.current_token() and self.current_token()["type"] == "COMMA":
                        self.advance()
                else:
                    self.add_error(SyntaxErrorType.INVALID_ARGUMENT, f"Invalid argument type: {current['type']}")
                    return

            if not self.expect("RPAREN"):
                self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")
                return
        else:
            self.parse_expression()

    def parse_method_call(self, identifier: str):
        self.advance()  

        if not self.expect("IDENTIFIER"):
            self.add_error(
                SyntaxErrorType.INVALID_METHOD_CALL,
                "Expected method name after '.'"
            )
            return

        if self.current_token()["type"] == "LPAREN":
            self.advance()
            while self.current_token() and self.current_token()["type"] != "RPAREN":
                if self.current_token()["type"] == "COMMA":
                    self.advance()
                else:
                    self.advance()
            
            if not self.expect("RPAREN"):
                self.add_error(
                    SyntaxErrorType.MISSING_PARENTHESIS,
                    "Expected ')' after method arguments"
                )
                return

    def parse_this_access(self):
        if not self.in_class:
            self.add_error(
                SyntaxErrorType.INVALID_THIS,
                "'this' keyword can only be used inside class methods"
            )
            return

        self.advance() 
        
        if not self.expect("DOT"):
            self.add_error(
                SyntaxErrorType.INVALID_THIS,
                "Expected '.' after 'this'"
            )
            return

        if not self.expect("IDENTIFIER"):
            self.add_error(
                SyntaxErrorType.INVALID_THIS,
                "Expected attribute name after 'this.'"
            )
            return
    
    def parse_class_method_body(self):
        while self.current_token() and self.current_token()["type"] != "DEDENT":
            token = self.current_token()
            
            if token["type"] == "THIS":
                self.parse_this_assignment()
            elif token["type"] == "PRINT":
                self.parse_print_statement()
            elif token["type"] == "ACTION":
                self.parse_method_definition()
            else:
                self.advance()

    def parse_this_assignment(self):
        self.advance()
        
        if not self.expect("DOT"):
            self.add_error(SyntaxErrorType.INVALID_THIS, "Expected '.' after 'this'")
            return
            
        if not self.expect("IDENTIFIER"):
            self.add_error(SyntaxErrorType.INVALID_THIS, "Expected attribute name")
            return
            
        if not self.expect("ASSIGN"):
            self.add_error(SyntaxErrorType.INVALID_ASSIGNMENT, "Expected '=' after attribute")
            return
            
        if not self.current_token() or self.current_token()["type"] not in ["IDENTIFIER", "STRING_LITERAL", "INTEGER_LITERAL", "FLOAT_LITERAL"]:
            self.add_error(SyntaxErrorType.INVALID_ASSIGNMENT, "Expected value after '='")
            return

        self.advance() 
        
    def parse_while_statement(self):
        self.advance() 
        
        if not self.expect("LPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected '(' after while")
            return

        if self.current_token()["type"] == "TRUE":
            self.advance()
        else:
            self.parse_condition()
        
        if not self.expect("RPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")
            return

        if not self.expect("COLON"):
            self.add_error(SyntaxErrorType.MISSING_COLON, "Expected ':' after condition")
            return

        if not self.expect("INDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected indented block")
            return

        while self.current_token() and self.current_token()["type"] != "DEDENT":
            self.parse_statement()

        if not self.expect("DEDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected dedent")

    def parse_for_loop(self):
        self.advance()
        
        if not self.expect("IDENTIFIER"):
            self.add_error(SyntaxErrorType.INVALID_STATEMENT, "Expected iterator variable")
            return

        if not self.expect("IN"):
            self.add_error(SyntaxErrorType.INVALID_STATEMENT, "Expected 'in' keyword")
            return

        if not self.expect("RANGE"):
            self.add_error(SyntaxErrorType.INVALID_STATEMENT, "Expected 'range'")
            return

        if not self.expect("LPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected '('")
            return

        self.parse_range_arguments()

        if not self.expect("RPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")
            return

        if not self.expect("COLON"):
            self.add_error(SyntaxErrorType.MISSING_COLON, "Expected ':'")
            return

        if not self.expect("INDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected indented block")
            return

        while self.current_token() and self.current_token()["type"] != "DEDENT":
            self.parse_statement()

        if not self.expect("DEDENT"):
            self.add_error(SyntaxErrorType.INVALID_INDENTATION, "Expected dedent")

    def parse_range_arguments(self):
        if not self.current_token() or self.current_token()["type"] not in ["INTEGER_LITERAL", "IDENTIFIER"]:
            self.add_error(SyntaxErrorType.INVALID_ARGUMENT, "Expected integer or identifier")
            return
        self.advance()

        if self.expect("COMMA"):
            if not self.current_token() or self.current_token()["type"] not in ["INTEGER_LITERAL", "IDENTIFIER"]:
                self.add_error(SyntaxErrorType.INVALID_ARGUMENT, "Expected integer or identifier")
                return
            self.advance()

    def parse_break_continue(self):
        token_type = self.current_token()["type"]
        if not (self.in_loop or self.scope_level > 0):
            self.add_error(SyntaxErrorType.INVALID_STATEMENT, 
                        f"{token_type.lower()} statement outside loop")
        self.advance()

    def parse_increment(self):
        identifier = self.current_token()["value"]
        self.advance()
        
        if not self.expect("PLUS_ASSIGN"):
            self.add_error(SyntaxErrorType.INVALID_ASSIGNMENT, "Expected '+='")
            return
            
        if not self.current_token() or self.current_token()["type"] != "INTEGER_LITERAL":
            self.add_error(SyntaxErrorType.INVALID_ASSIGNMENT, "Expected integer literal")
            return
        self.advance()

    def parse_condition(self):
        if not self.current_token() or self.current_token()["type"] not in ["IDENTIFIER", "INTEGER_LITERAL"]:
            self.add_error(SyntaxErrorType.INVALID_CONDITION, "Expected identifier or number")
            return
        self.advance()
                
        if not self.current_token() or self.current_token()["type"] not in ["LESS", "LESS_EQUAL", "GREATER", "GREATER_EQUAL", "EQUAL", "NOT_EQUAL"]:
            self.add_error(SyntaxErrorType.INVALID_CONDITION, "Expected comparison operator")
            return
        self.advance()
        
        if not self.current_token() or self.current_token()["type"] not in ["IDENTIFIER", "INTEGER_LITERAL"]:
            self.add_error(SyntaxErrorType.INVALID_CONDITION, "Expected identifier or number")
            return
        self.advance()

    def parse_expression(self):
        self.parse_term()
        
        while self.current_token() and self.current_token()["type"] in ["PLUS", "MINUS", "MULTIPLY", "DIVIDE"]:
            self.advance()
            self.parse_term()

    def parse_term(self):
        current = self.current_token()
        if not current:
            return
            
        if current["type"] in ["INTEGER_LITERAL", "FLOAT_LITERAL"]:
            self.advance()
        elif current["type"] == "IDENTIFIER":
            self.advance()
            while self.current_token() and self.current_token()["type"] == "DOT":
                self.advance()
                if not self.expect("IDENTIFIER"):
                    self.add_error(SyntaxErrorType.INVALID_EXPRESSION, "Expected identifier after '.'")
                    return
        elif current["type"] == "LPAREN":
            self.advance()
            self.parse_expression()
            if not self.expect("RPAREN"):
                self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")

    def parse_arithmetic_operand(self):
        if not self.current_token():
            return
            
        if self.current_token()["type"] in ["INTEGER_LITERAL", "FLOAT_LITERAL", "IDENTIFIER"]:
            self.advance()
        elif self.current_token()["type"] == "LPAREN":
            self.advance()
            self.parse_expression()
            if not self.expect("RPAREN"):
                self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")

    def validate_block_indentation(self, first_indent_level=None):
        if first_indent_level is None:
            token = self.current_token()
            if token and token["type"] == "INDENT":
                first_indent_level = len(token["value"])
            else:
                return

        while self.current_token() and self.current_token()["type"] not in ["DEDENT", "EOF"]:
            token = self.current_token()
            if token["type"] == "INDENT":
                current_indent = len(token["value"])
                if current_indent != first_indent_level:
                    self.add_error(
                        SyntaxErrorType.INVALID_INDENTATION,
                        f"Inconsistent indentation. Expected {first_indent_level} spaces, got {current_indent}"
                    )
            self.advance()

    def parse_identifier_list(self) -> List[str]:
        """Parse a comma-separated list of identifiers"""
        identifiers = []
        
        if self.current_token()["type"] == "IDENTIFIER":
            identifiers.append(self.current_token()["value"])
            self.advance()
        else:
            return identifiers

        while self.current_token() and self.current_token()["type"] == "COMMA":
            self.advance() 
            
            if not self.current_token() or self.current_token()["type"] != "IDENTIFIER":
                self.add_error(SyntaxErrorType.INVALID_ASSIGNMENT,
                            "Expected identifier after comma")
                break
                
            identifiers.append(self.current_token()["value"])
            self.advance()
            
        return identifiers

    def parse_multiple_assignment(self, identifiers: List[str]):
        self.advance()  
        
        values = self.parse_value_list()
        
        if len(values) != len(identifiers):
            self.add_error(
                SyntaxErrorType.INVALID_ASSIGNMENT,
                f"Number of variables ({len(identifiers)}) does not match number of values ({len(values)})"
            )

    def parse_value_list(self) -> List[str]:
        values = []
        
        if self.current_token()["type"] == "IDENTIFIER":
            next_token = self.peek_next()
            if next_token and next_token["type"] == "LPAREN":
                self.parse_function_call()
                return ["function_call"] 
        
        if not self.parse_single_value():
            return values
        values.append("value") 

        while self.current_token() and self.current_token()["type"] == "COMMA":
            self.advance()  
            
            if not self.parse_single_value():
                self.add_error(SyntaxErrorType.INVALID_ASSIGNMENT,
                            "Expected value after comma")
                break
                
            values.append("value") 
            
        return values

    def parse_single_value(self) -> bool:
        if not self.current_token():
            return False
            
        current = self.current_token()
        if current["type"] in ["INTEGER_LITERAL", "FLOAT_LITERAL", "STRING_LITERAL"]:
            self.advance()
            return True
        elif current["type"] == "IDENTIFIER":
            self.advance()
            if self.current_token() and self.current_token()["type"] == "DOT":
                self.parse_method_call(current["value"])
            return True
        elif current["type"] == "NEW":
            self.parse_object_creation()
            return True
        
        return False

    def parse_function_call(self):
        self.advance() 
        
        if not self.expect("LPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected '('")
            return
            
        while self.current_token() and self.current_token()["type"] != "RPAREN":
            if not self.parse_single_value():
                if self.current_token() and self.current_token()["type"] != "RPAREN":
                    self.add_error(SyntaxErrorType.INVALID_ARGUMENT,
                                "Invalid function argument")
                break
            
            if self.current_token() and self.current_token()["type"] == "COMMA":
                self.advance()
        
        if not self.expect("RPAREN"):
            self.add_error(SyntaxErrorType.MISSING_PARENTHESIS, "Expected ')'")