from typing import List, Dict, Tuple, Optional
from token_definitions import *
from soop_token import Token

class LexicalAnalyzer:
    def __init__(self, code: str):
        self.code = code
        self.tokens: List[Token] = []
        self.errors: List[Dict] = []
        self.indentation_stack = [0]  

    def match_string(self, line: str, pos: int, line_num: int) -> Tuple[int, Optional[Token], Optional[str]]:
        quote = line[pos]
        is_triple = False
        start_pos = pos
        
        if pos + 2 < len(line) and line[pos:pos + 3] == quote * 3:
            is_triple = True
            pos += 2

        end = pos + 1
        escaped = False
        string_content = []
        
        while end < len(line):
            curr_char = line[end]
            
            if escaped:
                if curr_char in 'nrt\\\'\"':
                    string_content.append('\\' + curr_char)
                else:
                    string_content.append(curr_char)
                escaped = False
            elif curr_char == '\\':
                escaped = True
            elif curr_char == quote:
                if is_triple:
                    if end + 2 < len(line) and line[end:end + 3] == quote * 3:
                        end += 2
                        return end + 1, Token(TOKEN_STRING_LITERAL, ''.join(string_content), line_num), None
                else:
                    return end + 1, Token(TOKEN_STRING_LITERAL, ''.join(string_content), line_num), None
            else:
                string_content.append(curr_char)
            end += 1
        
        partial_string = line[start_pos:end]
        error_msg = f"Unclosed {'triple ' if is_triple else ''}string literal starting at column {start_pos + 1}: {partial_string}"
        return end, Token(TOKEN_ERROR, error_msg, line_num), error_msg

    def match_number(self, line: str, pos: int, line_num: int) -> Tuple[int, Token]:
        end = pos
        base = 10
        is_float = False
        has_exponent = False
        
        if line[pos:pos+2].lower() in ['0x', '0o', '0b']:
            base = {'x': 16, 'o': 8, 'b': 2}[line[pos+1].lower()]
            end += 2
        
        while end < len(line):
            char = line[end]
            
            if char == '_' and end > pos and end+1 < len(line) and line[end+1].isdigit():
                end += 1
                continue
                
            if char == '.' and not is_float and not has_exponent and base == 10:
                if end+1 < len(line) and line[end+1].isdigit():
                    is_float = True
                    end += 1
                    continue
                else:
                    break

            if char.lower() == 'e' and base == 10 and not has_exponent:
                if end+1 < len(line) and (line[end+1] in '+-' or line[end+1].isdigit()):
                    has_exponent = True
                    end += 1
                    if line[end] in '+-':
                        end += 1
                    continue
                else:
                    break
                    
            if (base == 16 and char.lower() in '0123456789abcdef') or \
               (base == 8 and char in '01234567') or \
               (base == 2 and char in '01') or \
               (base == 10 and char.isdigit()):
                end += 1
            else:
                break
                
        number = line[pos:end].replace('_', '')
        
        try:
            if is_float or has_exponent:
                value = float(number)
                type_name = TOKEN_FLOAT_LITERAL
            else:
                value = int(number, base)
                type_name = TOKEN_INTEGER_LITERAL
        except ValueError:
            return end, Token(TOKEN_ERROR, number, line_num)
            
        return end, Token(type_name, number, line_num)

    def match_identifier(self, line: str, pos: int, line_num: int) -> Tuple[int, Token]:
        if not (line[pos].isalpha() or line[pos] == '_'):
            return pos, Token(TOKEN_ERROR, line[pos], line_num)
            
        end = pos
        while end < len(line):
            if not (line[end].isalnum() or line[end] == '_' or ord(line[end]) > 127):
                break
            end += 1
                
        word = line[pos:end]
        
        if word in KEYWORDS:
            return end, Token(KEYWORDS[word], word, line_num)
        elif word in DATA_TYPES:
            return end, Token(DATA_TYPES[word], word, line_num)
        elif word in BOOL_VALUES:
            return end, Token(BOOL_VALUES[word], word, line_num)
        else:
            return end, Token(TOKEN_IDENTIFIER, word, line_num)

    def handle_indentation(self, line: str, line_num: int) -> List[Token]:
        tokens = []
        
        if not line.strip():
            return tokens
            
        current_indent = len(line) - len(line.lstrip())
        last_indent = self.indentation_stack[-1]
        
        if current_indent > last_indent:
            self.indentation_stack.append(current_indent)
            tokens.append(Token(TOKEN_INDENT, current_indent, line_num))
            
        elif current_indent < last_indent:
            while self.indentation_stack and current_indent < self.indentation_stack[-1]:
                self.indentation_stack.pop()
                tokens.append(Token(TOKEN_DEDENT, current_indent, line_num))
                
            if current_indent != self.indentation_stack[-1]:
                self.errors.append({
                    "message": f"Inconsistent indentation at line {line_num}",
                    "line": line_num
                })
                
        return tokens
    
    def tokenize(self) -> Tuple[List[Dict], List[Dict]]:

        lines = self.code.splitlines()
        if not lines or (len(lines) == 1 and not lines[0]):
            # Handle empty input
            self.tokens.append(Token(TOKEN_EOF, "", 1))
            return [token.to_dict() for token in self.tokens], self.errors

        for line_num, line in enumerate(lines, 1):
 
            if line.strip():
                indent_tokens = self.handle_indentation(line, line_num)
                self.tokens.extend(indent_tokens)
                
            pos = 0
            line = line.rstrip() 
            
            while pos < len(line):
                column = pos + 1  
                
                if line[pos].isspace():
                    pos += 1
                    continue
                
                if line[pos] == '#':
                    comment = line[pos:].strip()
                    self.tokens.append(Token(TOKEN_COMMENT, comment, line_num))
                    break  
                
                if line[pos] in '"\'':
                    result = self.match_string(line, pos, line_num)
                    if result:
                        new_pos, token, error = result
                        if error:
                            self.errors.append({
                                "message": error,
                                "line": line_num,
                                "column": column
                            })
                        if token:
                            self.tokens.append(token)
                        pos = new_pos
                        continue
                
                if line[pos].isdigit() or (line[pos] == '.' and pos + 1 < len(line) and line[pos + 1].isdigit()):
                    result = self.match_number(line, pos, line_num)
                    if result:
                        new_pos, token = result
                        self.tokens.append(token)
                        pos = new_pos
                        continue
                
                if line[pos].isalpha() or line[pos] == '_':
                    result = self.match_identifier(line, pos, line_num)
                    if result:
                        new_pos, token = result
                        self.tokens.append(token)
                        pos = new_pos
                        continue
                
                symbol_matched = False
                for symbol, token_type in SYMBOLS:
                    if line[pos:].startswith(symbol):
                        self.tokens.append(Token(token_type, symbol, line_num))
                        pos += len(symbol)
                        symbol_matched = True
                        break
                
                if symbol_matched:
                    continue
                
                self.errors.append({
                    "message": f"Unknown character: {line[pos]}",
                    "line": line_num,
                    "column": column
                })
                self.tokens.append(Token(TOKEN_UNKNOWN, line[pos], line_num))
                pos += 1
            
            if line_num < len(lines):
                self.tokens.append(Token(TOKEN_NEWLINE, "\n", line_num))
        
        while len(self.indentation_stack) > 1:
            self.indentation_stack.pop()
            self.tokens.append(Token(TOKEN_DEDENT, 0, len(lines)))

        self.tokens.append(Token(TOKEN_EOF, "", len(lines)))
        
        return [token.to_dict() for token in self.tokens], self.errors

