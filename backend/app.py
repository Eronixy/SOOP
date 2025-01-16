from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

KEYWORDS = {
    word: category.upper().replace(' ', '_')
    for category, words in {
        "Built in Methods": ["print", "input"],
        "Noise Words": ["in", "def"],
        "Object-Oriented": ["class", "template", "new", "setup", "action", "static", "inherits", "parent", "override", "this"],
        "Control Flow": ["if", "else", "else if", "for", "while", "break", "continue", "return", "switch"],
        "Exception Handling": ["try", "catch", "finally", "raise"],
        "Functionality": ["define", "import"],
        "Memory Management": ["create", "delete"],
        "Access Modifiers": ["public", "restricted", "private"],
        "Reserved for Future": ["async", "await", "concurrent", "immutable", "delegate", "yield", "thread"]
    }.items()
    for word in words
}

SYMBOLS = sorted([
    (symbol, category.upper().replace(' ', '_'))
    for category, symbol in {
        "Increment": "++",
        "Decrement": "--",
        "Plus Assignment": "+=",
        "Minus Assignment": "-=",
        "Multiply Assignment": "*=",
        "Divide Assignment": "/=",
        "Modulo Assignment": "%=",
        "Floor Division Assignment": "//=",
        "Greater Than or Equal": ">=",
        "Less Than or Equal": "<=",
        "Equal To": "==",
        "Not Equal": "!=",
        "Logical Or": "||",
        "Logical And": "&&",
        "Floor Division": "//",
        "Plus Symbol": "+",
        "Minus Symbol": "-",
        "Asterisk": "*",
        "Divide": "/",
        "Modulo": "%",
        "Caret": "^",
        "Greater Than": ">",
        "Less Than": "<",
        "Logical Not": "!",
        "Equals": "=",
        "Open Parenthesis": "(",
        "Close Parenthesis": ")",
        "Open Brace": "{",
        "Close Brace": "}",
        "Hash": "#",
        "Colon": ":",
        "Semi Colon": ";",
        "Comma": ",",
        "Period": ".",
        "Double Quotes": "\""
    }.items()
], key=lambda x: len(x[0]), reverse=True)

DATA_TYPES = {"int", "double", "float", "bool", "list", "dict", "string"}
BOOL_VALUES = {"true", "false"}

def create_token(type_name, value, line):
    return {"type": type_name, "value": value, "line": line}

def match_string(code, pos):
    quote = code[pos]
    end = pos + 1
    while end < len(code):
        if code[end] == quote and code[end-1] != '\\':
            return end + 1, create_token("STRING_LITERAL", code[pos:end+1], None)
        end += 1
    return end, None

def match_number(code, pos):
    end = pos
    has_decimal = False
    while end < len(code) and (code[end].isdigit() or (code[end] == '.' and not has_decimal)):
        if code[end] == '.':
            has_decimal = True
        end += 1
    number = code[pos:end]
    type_name = "FLOAT_LITERAL" if '.' in number else "INTEGER_LITERAL"
    return end, create_token(type_name, number, None)

def match_identifier(code, pos):
    end = pos
    while end < len(code) and (code[end].isalnum() or code[end] == '_'):
        end += 1
    word = code[pos:end]
    
    if word in KEYWORDS:
        return end, create_token(KEYWORDS[word], word, None)
    elif word in DATA_TYPES:
        return end, create_token("DATA_TYPE", word, None)
    elif word in BOOL_VALUES:
        return end, create_token("BOOLEAN_LITERAL", word, None)
    elif word == "null":
        return end, create_token("NULL_LITERAL", word, None)
    else:
        return end, create_token("IDENTIFIER", word, None)

def match_symbol(code, pos):
    for symbol, category in SYMBOLS:
        if code[pos:].startswith(symbol):
            return pos + len(symbol), create_token(category, symbol, None)
    return pos + 1, create_token("UNKNOWN", code[pos], None)

def tokenize(code):
    tokens = []
    lines = code.splitlines()
    
    for line_num, line in enumerate(lines, 1):
        indent_level = len(line) - len(line.lstrip())
        if indent_level > 0:
            tokens.append(create_token("INDENT", indent_level, line_num))
            
        if line.strip().startswith('#'):
            tokens.append(create_token("COMMENT", line.strip(), line_num))
            continue
            
        pos = 0
        line = line.strip()
        while pos < len(line):
            if line[pos].isspace():
                pos += 1
                continue
                
            token = None
            if line[pos] in '"\'':
                pos, token = match_string(line, pos)
            elif line[pos].isdigit():
                pos, token = match_number(line, pos)
            elif line[pos].isalpha() or line[pos] == '_':
                pos, token = match_identifier(line, pos)
            else:
                pos, token = match_symbol(line, pos)
                
            if token:
                token["line"] = line_num
                tokens.append(token)
    return tokens

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    code = data.get("code", "")
    tokens = tokenize(code)
    return jsonify(tokens)

if __name__ == '__main__':
    app.run(debug=True)