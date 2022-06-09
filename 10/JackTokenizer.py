"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """
    # dictionary for the tokens on the xml file
    tokens_in_xml = {"KEYWORD": "keyword", "SYMBOL": "symbol", "IDENTIFIER": "identifier",
                     "INT_CONST": "integerConstant", "STRING_CONST": "stringConstant"}

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is:
        # input_lines = input_stream.read().splitlines()

        # all the file as one string
        self.input_file = input_stream.read()
        # removes all comments from the input file
        self.remove_comments()
        # list of all the lines in the file
        self.input_lines = self.input_file.splitlines()
        # the number of lines in the file
        self.num_of_lines = len(self.input_lines)
        self.remove_empty_lines()
        # update number of lines after we deleted empty lines
        self.num_of_lines = len(self.input_lines)
        # list of all tokens
        self.tokens = []
        # the index of the current token
        self.current_token_index = 0
        # the current token
        self.current_token = None
        # number of tokens
        self.num_of_tokens = None

        self.keywords = {"class", "constructor", "function", "method", "field",
                         "static", "var", "int", "char", "boolean", "void", "true",
                         "false", "null", "this", "let", "do", "if", "else", "while", "return"}

        self.symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';',
                        '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}

    def remove_comments(self) -> None:
        """ Removes all comments from the text"""
        curr_ind = 0
        without_comments = ""
        while curr_ind < len(self.input_file):
            curr_char = self.input_file[curr_ind]
            # start of a string, include all that is inside
            if curr_char == '\"':
                end_of_string = self.input_file.find('\"', curr_ind + 1)
                without_comments += self.input_file[curr_ind:end_of_string + 1]
                curr_ind = end_of_string + 1
            elif curr_char == '/':
                if self.input_file[curr_ind + 1] == '/':  # end of line comment
                    curr_ind = self.input_file.find('\n', curr_ind + 1) + 1
                elif self.input_file[curr_ind + 1] == "*":  # in-line or multi-line comment
                    curr_ind = self.input_file.find("*/", curr_ind + 1) + 2
                else:
                    without_comments += '/'
                    curr_ind += 1
            else:
                without_comments += curr_char
                curr_ind += 1
        self.input_file = without_comments
        return

    def remove_empty_lines(self) -> None:
        """deletes all empty lines"""
        for line in reversed(range(self.num_of_lines)):
            self.input_lines[line] = self.input_lines[line].strip()
            if not self.input_lines[line]:  # if the line is empty, delete it
                self.input_lines.pop(line)

    def tokenize(self) -> None:
        """converts the input file to a list of individual tokens"""
        for line in self.input_lines:
            curr_ind = 0
            curr_char = line[curr_ind]
            while curr_ind < len(line):
                if curr_char in [" ", '\n', '\t'] :
                    curr_ind += 1
                    if curr_ind < len(line):
                        curr_char = line[curr_ind]
                elif curr_char in self.symbols:
                    self.tokens.append(curr_char)
                    curr_ind += 1
                    if curr_ind < len(line):
                        curr_char = line[curr_ind]
                elif curr_char == '\"':
                    end_of_string = line.find('\"', curr_ind + 1)
                    self.tokens.append(line[curr_ind:end_of_string + 1])
                    curr_ind = end_of_string + 1
                    if curr_ind < len(line):
                        curr_char = line[curr_ind]
                else:
                    curr_token = curr_char
                    curr_ind += 1
                    if curr_ind < len(line):
                        curr_char = line[curr_ind]
                    while curr_char not in self.symbols\
                            and curr_char not in [" ", '\n', '\t']\
                            and curr_ind < len(line):
                        curr_token += curr_char
                        curr_ind += 1
                        if curr_ind < len(line):
                            curr_char = line[curr_ind]
                    self.tokens.append(curr_token)
        self.num_of_tokens = len(self.tokens)

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.current_token_index == self.num_of_tokens:
            return False
        return True

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.current_token = self.tokens[self.current_token_index]
        self.current_token_index += 1


    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.current_token in self.keywords:
            return "KEYWORD"
        elif self.current_token in self.symbols:
            return "SYMBOL"
        elif re.match(r'\d+', self.current_token) is not None:
            return "INT_CONST"
        elif re.match(r'"[^"\n]*"', self.current_token) is not None:
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.current_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """

        if self.current_token == '<':
            return "&lt;"
        elif self.current_token == '>':
            return "&gt;"
        elif self.current_token == '"':
            return "&quot;"
        elif self.current_token == '&':
            return "&amp;"
        else:
            return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return self.current_token

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.current_token[1:-1]

    def write_token(self, output_file: typing.TextIO) -> None:
        """writes the token to the output_stream"""
        token_type = ""
        token = ""
        if self.token_type() == "KEYWORD":
            token_type = "keyword"
            token = self.keyword()
        elif self.token_type() == "SYMBOL":
            token_type = "symbol"
            token = self.symbol()
        elif self.token_type() == "IDENTIFIER":
            token_type = "identifier"
            token = self.identifier()
        elif self.token_type() == "INT_CONST":
            token_type = "integerConstant"
            token = str(self.int_val())
        elif self.token_type() == "STRING_CONST":
            token_type = "stringConstant"
            token = self.string_val()
        output_file.write('<' + token_type + '> ' + token + ' </' + token_type + '>\n')

    def peek(self):
        """returns the next token, if there is no more tokens, returns None"""
        if self.current_token_index < self.num_of_tokens:
            return self.tokens[self.current_token_index]
        else:
            return None

