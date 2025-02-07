from typing import Dict

class Token:
    def __init__(self, type_name: str, value: str, line: int):
        self.type = type_name
        self.value = value
        self.line = line
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "value": self.value,
            "line": self.line
        }