"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """

    # Note: you can get the input file's name using:
    input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    parser = Parser(input_file)
    parser.pre_process()
    code_writer = CodeWriter(output_file)
    code_writer.set_file_name(input_filename)
    func_name = None
    if start_of_file:
        code_writer.write_init()
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "C_ARITHMETIC":
            code_writer.write_arithmetic(parser.arg1())
        elif parser.command_type() == "C_PUSH" \
                or parser.command_type() == "C_POP":
            code_writer.write_push_pop(parser.command_type(), parser.arg1(), parser.arg2())
        elif parser.command_type() == "C_GOTO" \
                or parser.command_type() == "C_IF" \
                or parser.command_type() == "C_LABEL":
            code_writer.write_branching(parser.command_type(), func_name+ "$"+ parser.arg1())
        elif parser.command_type() == "C_CALL":
            code_writer.write_call(parser.arg1(), parser.arg2())
        elif parser.command_type() == "C_FUNCTION":
            func_name = parser.arg1()
            code_writer.write_function(parser.arg1(), parser.arg2())
        elif parser.command_type() == "C_RETURN":
            code_writer.write_return()


if "__main__" == __name__:

    # Parses the input path and calls translate_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        start_of_file = True
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file)
            start_of_file = False
