"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import *


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
        self.table = SymbolTable()
        self.writer = VMWriter(output_stream)
        self.binary_operators = {'+': "add", '-': "sub", '*': "call Math.multiply 2",
                                 '/': "call Math.divide 2", '&': "and", '|': "or", '<': "lt",
                                 '>': "gt", '=': "eq"}
        self.unary_operators = {'-': "neg", '~': "not", '^': "shiftleft", '#': "shiftright"}
        self.class_name = ""
        self.num_of_class_vars = 0
        self.num_of_local_vars = 0
        self.label_counter = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.tokenizer.advance()  # advance to first token
        pass  # class declaration
        self.tokenizer.advance()
        self.class_name = self.tokenizer.current_token  # class name
        self.tokenizer.advance()
        pass  # '{' symbol
        # class variables declarations
        while self.tokenizer.peek() in {'static', 'field'}:
            self.num_of_class_vars += 1
            self.compile_class_var_dec()
        # class subroutine declarations
        while self.tokenizer.peek() in {'constructor', 'function', 'method'}:
            self.compile_subroutine()
        self.tokenizer.advance()
        pass  # '}' symbol

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.tokenizer.advance()
        pass  # 'static | field'
        token_kind = self.tokenizer.current_token.upper()
        self.tokenizer.advance()
        pass  # type of variable (int|char|boolean|className)
        token_type = self.tokenizer.current_token
        self.tokenizer.advance()
        pass  # varName
        token_name = self.tokenizer.current_token
        self.table.define(token_name, token_type, token_kind)
        while self.tokenizer.peek() != ';':
            # case of: var int a, b, ... ;
            self.tokenizer.advance()
            pass
            if self.tokenizer.token_type() == "IDENTIFIER":
                self.num_of_class_vars += 1
                token_name = self.tokenizer.current_token
                self.table.define(token_name, token_type, token_kind)
        self.tokenizer.advance()
        pass  # ';'

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        # subroutine declaration
        self.table.start_subroutine()
        self.num_of_local_vars = 0
        self.tokenizer.advance()
        pass  # constructor|function|method
        type_of_func = self.tokenizer.current_token  # constructor|function|method
        self.tokenizer.advance()
        pass  # void|type
        return_type = self.tokenizer.current_token
        self.tokenizer.advance()
        pass  # subroutineName
        name_of_func = self.class_name + '.' + self.tokenizer.current_token
        if type_of_func == "method":
            self.table.define("this", self.class_name, "ARG")
        self.tokenizer.advance()
        pass  # '('
        self.compile_parameter_list()
        self.tokenizer.advance()
        pass  # ')'

        # subroutine body
        self.tokenizer.advance()
        pass  # '{'
        while self.tokenizer.peek() == 'var':
            self.num_of_local_vars += 1
            self.compile_var_dec()
        self.writer.write_function(name_of_func, self.num_of_local_vars)
        if type_of_func == "method":
            self.writer.write_push("ARG", 0)
            self.writer.write_pop("POINTER", 0)
        if type_of_func == "constructor":
            self.writer.write_push("CONST", self.num_of_class_vars)
            self.writer.write_call("Memory.alloc", 1)
            self.writer.write_pop("POINTER", 0)
        self.compile_statements()
        self.tokenizer.advance()
        pass  # '}'

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        while self.tokenizer.peek() != ')':
            # write all function parameters
            self.tokenizer.advance()
            pass  # type of argument
            token_type = self.tokenizer.current_token
            self.tokenizer.advance()
            pass  # name of argument
            token_name = self.tokenizer.current_token
            self.table.define(token_name, token_type, "ARG")
            if self.tokenizer.peek() == ',':
                self.tokenizer.advance()
                pass  # ','

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.tokenizer.advance()
        pass  # 'var'
        token_kind = "VAR"
        self.tokenizer.advance()
        pass  # type of variable (int|char|boolean|className)
        token_type = self.tokenizer.current_token
        self.tokenizer.advance()
        pass  # varName
        token_name = self.tokenizer.current_token
        self.table.define(token_name, token_type, token_kind)
        while self.tokenizer.peek() != ';':
            # case of: var int a, b, ... ;
            self.tokenizer.advance()
            pass
            if self.tokenizer.token_type() == "IDENTIFIER":
                self.num_of_local_vars += 1
                token_name = self.tokenizer.current_token
                self.table.define(token_name, token_type, token_kind)
        self.tokenizer.advance()
        pass  # ';'

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
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

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.tokenizer.advance()
        pass  # do keyword
        self.compile_expression()
        self.tokenizer.advance()
        pass  # ';'
        self.writer.write_pop("TEMP", 0)  # throw away the value, because it's a do statement

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.tokenizer.advance()
        pass  # let
        self.tokenizer.advance()
        pass  # varName
        var_name = self.tokenizer.current_token
        var_segment = self.table.kind_of(var_name)
        var_segment_index = self.table.index_of(var_name)
        if self.tokenizer.peek() == '[':  # varName[index]
            self.tokenizer.advance()
            pass  # '['
            self.compile_expression()
            self.writer.write_push(var_segment, var_segment_index)
            self.writer.write_arithmetic(self.binary_operators['+'])  # pushing the target address onto the stack
            self.tokenizer.advance()
            pass  # ']'
            self.tokenizer.advance()
            pass  # '='
            self.compile_expression()
            self.writer.write_pop("TEMP", 0)
            self.writer.write_pop("POINTER", 1)
            self.writer.write_push("TEMP", 0)
            self.writer.write_pop("THAT", 0)
            self.tokenizer.advance()
            pass  # ';'
        else:
            self.tokenizer.advance()
            pass  # '='
            self.compile_expression()
            self.tokenizer.advance()
            pass  # ';'
            self.writer.write_pop(var_segment, var_segment_index)

    def compile_while(self) -> None:
        """Compiles a while statement."""

        # create labels
        while_start_label = "WHILE_START" + str(self.label_counter)
        while_end_label = "WHILE_END" + str(self.label_counter)
        self.label_counter += 1

        self.writer.write_label(while_start_label)
        self.tokenizer.advance()
        pass  # while
        self.tokenizer.advance()
        pass  # '('
        self.compile_expression()
        self.writer.write_arithmetic(self.unary_operators['~'])  # negate the expression
        self.writer.write_if(while_end_label)  # exit the while loop
        self.tokenizer.advance()
        pass  # ')'
        self.tokenizer.advance()
        pass  # '{'
        self.compile_statements()
        self.tokenizer.advance()
        self.writer.write_goto(while_start_label)  # go back to the start of the while
        pass  # '}'
        self.writer.write_label(while_end_label)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.tokenizer.advance()
        pass  # return
        if self.tokenizer.peek() != ';':
            self.compile_expression()
        else:  # case of return; (void function)
            self.writer.write_push("CONST", 0)
        self.tokenizer.advance()
        pass  # ';'
        self.writer.write_return()

    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause."""
        # create labels
        if_false_label = "IF_FALSE" + str(self.label_counter)
        if_end_label = "IF_END" + str(self.label_counter)
        self.label_counter += 1

        self.tokenizer.advance()
        pass  # if
        self.tokenizer.advance()
        pass  # '('
        self.compile_expression()
        self.writer.write_arithmetic(self.unary_operators['~'])  # negate the expression
        self.writer.write_if(if_false_label)
        self.tokenizer.advance()
        pass  # ')'
        self.tokenizer.advance()
        pass  # '{'
        self.compile_statements()
        self.tokenizer.advance()
        pass  # '}'
        self.writer.write_goto(if_end_label)
        self.writer.write_label(if_false_label)
        if self.tokenizer.peek() == 'else':
            self.tokenizer.advance()
            pass  # else
            self.tokenizer.advance()
            pass  # '{'
            self.compile_statements()
            self.tokenizer.advance()
            pass  # '}'
        self.writer.write_label(if_end_label)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.tokenizer.peek() in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
            self.tokenizer.advance()
            operation = self.binary_operators[self.tokenizer.current_token]  # binary operation
            self.compile_term()
            self.writer.write_arithmetic(operation)

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

        self.tokenizer.advance()

        if self.tokenizer.token_type() == 'INT_CONST':  # integer constant
            self.writer.write_push("CONST", self.tokenizer.int_val())

        elif self.tokenizer.token_type() == 'STRING_CONST':  # string constant
            self.writer.write_push("CONST", len(self.tokenizer.string_val()))
            self.writer.write_call("String.new", 1)
            for character in self.tokenizer.string_val():
                self.writer.write_push("CONST", ord(character))  # push const ascii value
                self.writer.write_call("String.appendChar", 2)

        elif self.tokenizer.token_type() == 'KEYWORD':  # keyword constant
            if self.tokenizer.current_token == "this":
                self.writer.write_push("POINTER", 0)
            elif self.tokenizer.current_token == "true":
                self.writer.write_push("CONST", 1)
                self.writer.write_arithmetic(self.unary_operators['-'])
            else:  # false|null
                self.writer.write_push("CONST", 0)

        elif self.tokenizer.token_type() == 'IDENTIFIER':
            # 4 options: class name, single variable name, array variable name, method name
            identifier = self.tokenizer.current_token
            # so we can have: '[' for array, '.' for class, '(' for method,
            if self.tokenizer.peek() == '[':  # varName[expression]
                self.tokenizer.advance()
                pass  # '['
                self.compile_expression()
                self.writer.write_push(self.table.kind_of(identifier),
                                       self.table.index_of(identifier))
                self.writer.write_arithmetic(self.binary_operators['+'])  # pushing the target address onto the stack
                self.tokenizer.advance()
                pass  # ']'
                self.writer.write_pop("POINTER", 1)
                self.writer.write_push("THAT", 0)
            elif self.tokenizer.peek() == '(':  # this.subroutineName(expressionList)
                self.tokenizer.advance()
                pass  # '('
                self.writer.write_push("POINTER", 0)  # 'push this'
                num_of_args = self.compile_expression_list()
                self.tokenizer.advance()
                pass  # ')'
                call_name = self.class_name + '.' + identifier
                self.writer.write_call(call_name, num_of_args + 1)
            elif self.tokenizer.peek() == '.':  # className/varName.subroutineName(expressionList)
                if not self.table.is_var(identifier):  # case of className.subroutineName(expressionList)
                    self.tokenizer.advance()
                    identifier += self.tokenizer.current_token  # '.'
                    self.tokenizer.advance()
                    identifier += self.tokenizer.current_token  # subroutineName
                    self.tokenizer.advance()
                    pass  # '('
                    num_of_args = self.compile_expression_list()
                    self.tokenizer.advance()
                    pass  # ')'
                    self.writer.write_call(identifier, num_of_args)
                else:  # case of varName.subroutineName(expressionList)
                    self.tokenizer.advance()
                    type_of_var = self.table.type_of(identifier)
                    self.writer.write_push(self.table.kind_of(identifier),
                                           self.table.index_of(identifier))
                    pass  # '.'
                    self.tokenizer.advance()
                    method_name = self.tokenizer.current_token  # subroutineName
                    self.tokenizer.advance()
                    pass  # '('
                    num_of_args = self.compile_expression_list()
                    self.tokenizer.advance()
                    pass  # ')'
                    call_name = type_of_var + '.' + method_name
                    self.writer.write_call(call_name, num_of_args + 1)
            else:  # only varName
                self.writer.write_push(self.table.kind_of(self.tokenizer.current_token),  # push varName
                                       self.table.index_of(self.tokenizer.current_token))
        elif self.tokenizer.current_token == '(':  # case of (expression)
            pass  # '('
            self.compile_expression()
            self.tokenizer.advance()
            pass  # ')'
        elif self.tokenizer.current_token in {'-', '~', '^', '#'}:
            unary_operator = self.tokenizer.current_token  # write unary operation
            self.compile_term()
            self.writer.write_arithmetic(self.unary_operators[unary_operator])

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        num_of_exp = 0
        while self.tokenizer.peek() != ')':
            num_of_exp += 1
            self.compile_expression()
            if self.tokenizer.peek() == ',':
                self.tokenizer.advance()
                pass  # ','
        return num_of_exp
