"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.output = output_stream

    def write(self, kind: str, root: bool) -> None:
        ans = ""
        if root:
            ans += '<' + kind + '> \n'
        else:
            ans += '</' + kind + '>\n'
        self.output.write(ans)

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.write('class', True)
        self.tokenizer.advance()  # advance to first token
        self.tokenizer.write_token(self.output)  # class declaration
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # class name
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '{' symbol
        # class variables declarations
        while self.tokenizer.peek() in {'static', 'field'}:
            self.compile_class_var_dec()
        # class subroutine declarations
        while self.tokenizer.peek() in {'constructor', 'function', 'method', 'void'}:
            self.compile_subroutine()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '}' symbol
        self.write('class', False)

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.write('classVarDec', True)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # 'static | field'
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # type of variable (int|char|boolean|className)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # varName
        while self.tokenizer.peek() != ';':
            # case of: var int a, b, ... ;
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # ';'
        self.write('classVarDec', False)

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        # subroutine declaration
        self.write('subroutineDec', True)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # constructor|function|method
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # void|type
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # subroutineName
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '('
        self.compile_parameter_list()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # ')'
        # subroutine body
        self.write('subroutineBody', True)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '{'
        while self.tokenizer.peek() == 'var':
            self.compile_var_dec()
        self.compile_statements()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '}'
        self.write('subroutineBody', False)
        self.write('subroutineDec', False)

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.write('parameterList', True)
        while self.tokenizer.peek() != ')':
            # write all function parameters
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)
        self.write('parameterList', False)

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write('varDec', True)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # 'var'
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # type of variable (int|char|boolean|className)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # varName
        while self.tokenizer.peek() != ';':
            # case of: var int a, b, ... ;
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # ';'
        self.write('varDec', False)

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.write('statements', True)
        while self.tokenizer.peek() != '}':
            if self.tokenizer.peek() == 'let':
                self.compile_let()
            elif self.tokenizer.peek() == 'if':
                self.compile_if()
            elif self.tokenizer.peek() == 'while':
                self.compile_while()
            elif self.tokenizer.peek() == 'do':
                self.compile_do()
            elif self.tokenizer.peek() == 'return':
                self.compile_return()
        self.write('statements', False)

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.write('doStatement', True)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # do keyword
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # subroutineName |(className|varName)
        if self.tokenizer.peek() == '.':
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)  # '.'
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)  # subroutineName
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '('
        self.compile_expression_list()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # ')'
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # ';'
        self.write('doStatement', False)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.write('letStatement', True)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # let
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # varName
        if self.tokenizer.peek() == '[':
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)  # '['
            self.compile_expression()
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)  # ']'
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '='
        self.compile_expression()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # ';'
        self.write('letStatement', False)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.write('whileStatement', True)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # while
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '('
        self.compile_expression()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # ')'
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '{'
        self.compile_statements()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '}'
        self.write('whileStatement', False)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.write('returnStatement', True)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # return
        if self.tokenizer.peek() != ';':
            self.compile_expression()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # ';'
        self.write('returnStatement', False)

    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause."""
        self.write('ifStatement', True)
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # if
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '('
        self.compile_expression()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # ')'
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '{'
        self.compile_statements()
        self.tokenizer.advance()
        self.tokenizer.write_token(self.output)  # '}'
        while self.tokenizer.peek() == 'else':
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)  # else
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)  # '{'
            self.compile_statements()
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)  # '}'
        self.write('ifStatement', False)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.write('expression', True)
        self.compile_term()
        while self.tokenizer.peek() in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)  # binary operation
            self.compile_term()
        self.write('expression', False)

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.write('term', True)
        self.tokenizer.advance()
        if self.tokenizer.token_type() in {'KEYWORD', 'INT_CONST', 'STRING_CONST'}:
            self.tokenizer.write_token(self.output)
        elif self.tokenizer.token_type() == 'IDENTIFIER':
            # 4 options: class name, singe variable name, array variable name, method name
            self.tokenizer.write_token(self.output)
            # so we can have: '[' for array, '.' for class, '(' for method,
            if self.tokenizer.peek() == '[':  # varName[expression]
                self.tokenizer.advance()
                self.tokenizer.write_token(self.output)  # '['
                self.compile_expression()
                self.tokenizer.advance()
                self.tokenizer.write_token(self.output)  # ']'
            elif self.tokenizer.peek() == '(':  # subroutineName(expressionList)
                self.tokenizer.advance()
                self.tokenizer.write_token(self.output)  # '('
                self.compile_expression_list()
                self.tokenizer.advance()
                self.tokenizer.write_token(self.output)  # ')'
            elif self.tokenizer.peek() == '.':  # className/varName.subroutineName(expressionList)
                self.tokenizer.advance()
                self.tokenizer.write_token(self.output)  # '.'
                self.tokenizer.advance()
                self.tokenizer.write_token(self.output)  # subroutineName
                self.tokenizer.advance()
                self.tokenizer.write_token(self.output)  # '('
                self.compile_expression_list()
                self.tokenizer.advance()
                self.tokenizer.write_token(self.output)  # ')'
            else:  # only varName
                pass
        elif self.tokenizer.current_token == '(':  # case of (expression)
            self.tokenizer.write_token(self.output)  # '('
            self.compile_expression()
            self.tokenizer.advance()
            self.tokenizer.write_token(self.output)  # ')'
        elif self.tokenizer.current_token in {'-', '~', '^', '#'}:
            self.tokenizer.write_token(self.output)  # write unary operation
            self.compile_term()
        self.write('term', False)

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.write('expressionList', True)
        while self.tokenizer.peek() != ')':
            self.compile_expression()
            if self.tokenizer.peek() == ',':
                self.tokenizer.advance()
                self.tokenizer.write_token(self.output)  # ','
        self.write('expressionList', False)
