from dataclasses import dataclass
from enum import Enum
from typing import List


class TokenType(Enum):
    """Token types for command parsing."""
    WORD = "WORD"
    PIPE = "PIPE"
    AND = "AND"
    OR = "OR"
    SEMICOLON = "SEMICOLON"
    REDIRECT_OUT = "REDIRECT_OUT"
    REDIRECT_APPEND = "REDIRECT_APPEND"
    REDIRECT_IN = "REDIRECT_IN"

@dataclass
class Token:
    """Represents a token in command parsing."""
    type: TokenType
    value: str
    position: int

@dataclass
class CommandPipeline:
    """Represents a pipeline of commands."""
    commands: List[List[str]]
    operator: TokenType

class CommandParser:
    """Parses command line input into executable commands."""
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.position = 0
    
    def tokenize(self, input_text: str) -> List[Token]:
        """Tokenize input text."""
        tokens = []
        position = 0
        
        # Special operators
        operators = {
            "|": TokenType.PIPE,
            "&&": TokenType.AND,
            "||": TokenType.OR,
            ";": TokenType.SEMICOLON,
            ">>": TokenType.REDIRECT_APPEND,
            ">": TokenType.REDIRECT_OUT,
            "<": TokenType.REDIRECT_IN,
        }
        
        i = 0
        while i < len(input_text):
            char = input_text[i]
            
            # Skip whitespace
            if char.isspace():
                i += 1
                continue
            
            # Check for two-character operators
            if i + 1 < len(input_text):
                two_char = input_text[i:i+2]
                if two_char in operators:
                    tokens.append(Token(operators[two_char], two_char, i))
                    i += 2
                    continue
            
            # Check for single-character operators
            if char in operators:
                tokens.append(Token(operators[char], char, i))
                i += 1
                continue
            
            # Parse words (including quoted strings)
            if char in ['"', "'"]:
                quote_char = char
                word_start = i
                i += 1
                word = ""
                
                while i < len(input_text) and input_text[i] != quote_char:
                    word += input_text[i]
                    i += 1
                
                if i < len(input_text):
                    i += 1  # Skip closing quote
                
                tokens.append(Token(TokenType.WORD, word, word_start))
            else:
                # Regular word
                word_start = i
                word = ""
                
                while (i < len(input_text) and 
                       not input_text[i].isspace() and 
                       input_text[i] not in operators):
                    word += input_text[i]
                    i += 1
                
                if word:
                    tokens.append(Token(TokenType.WORD, word, word_start))
        
        return tokens
    
    def parse(self, input_text: str) -> List['CommandPipeline']:
        """Parse input text into command pipelines."""
        tokens = self.tokenize(input_text)
        pipelines = []
        
        current_pipeline = []
        current_command = []
        current_redirect = None
        
        for token in tokens:
            if token.type == TokenType.WORD:
                if current_redirect:
                    # This is the filename for redirection
                    current_command.append(f"{current_redirect.value}{token.value}")
                    current_redirect = None
                else:
                    current_command.append(token.value)
            elif token.type == TokenType.PIPE:
                if current_command:
                    current_pipeline.append(current_command)
                    current_command = []
            elif token.type in [TokenType.AND, TokenType.OR, TokenType.SEMICOLON]:
                if current_command:
                    current_pipeline.append(current_command)
                    current_command = []
                
                if current_pipeline:
                    pipelines.append(CommandPipeline(current_pipeline, token.type))
                    current_pipeline = []
            elif token.type in [TokenType.REDIRECT_OUT, TokenType.REDIRECT_APPEND, TokenType.REDIRECT_IN]:
                current_redirect = token
        
        # Handle remaining command
        if current_command:
            current_pipeline.append(current_command)
        
        if current_pipeline:
            pipelines.append(CommandPipeline(current_pipeline, TokenType.SEMICOLON))
        
        return pipelines
