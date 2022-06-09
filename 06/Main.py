"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    #
    # You should use the two-pass implementation suggested in the book:
    #
    # *Initialization*
    # Initialize the symbol table with all the predefined symbols and their
    # pre-allocated RAM addresses, according to section 6.2.3 of the book.
    #
    # *First Pass*
    # Go through the entire assembly program, line by line, and build the symbol
    # table without generating any code. As you march through the program lines,
    # keep a running number recording the ROM address into which the current
    # command will be eventually loaded.
    # This number starts at 0 and is incremented by 1 whenever a C-instruction
    # or an A-instruction is encountered, but does not change when a label
    # pseudo-command or a comment is encountered. Each time a pseudo-command
    # (Xxx) is encountered, add a new entry to the symbol table, associating
    # Xxx with the ROM address that will eventually store the next command in
    # the program.
    # This pass results in entering all the programs labels along with their
    # ROM addresses into the symbol table.
    # The programs variables are handled in the second pass.

    table = SymbolTable()
    parser = Parser(input_file)
    parser.pre_process()
    rom_address = 0
    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        if command_type == "L_COMMAND" and not table.contains(parser.symbol()):
            table.add_entry(parser.symbol(), rom_address)
        else:
            rom_address += 1
    parser.reset()
    # *Second Pass*
    # Now go again through the entire program, and parse each line.
    # Each time a symbolic A-instruction is encountered, namely, @Xxx where Xxx
    # is a symbol and not a number, look up Xxx in the symbol table.
    # If the symbol is found in the table, replace it with its numeric meaning
    # and complete the commands translation.
    # If the symbol is not found in the table, then it must represent a new
    # variable. To handle it, add the pair (Xxx,n) to the symbol table, where n
    # is the next available RAM address, and complete the commands translation.
    # The allocated RAM addresses are consecutive numbers, starting at address
    # 16 (just after the addresses allocated to the predefined symbols).
    # After the command is translated, write the translation to the output file.
    ram_address = 16
    while parser.has_more_commands():
        parser.advance()
        command_type = parser.command_type()
        if command_type == "A_COMMAND":
            a_command = parser.symbol()
            # print(parser.symbol())
            if a_command.isnumeric():
                output_file.write((f"{int(a_command):016b}"+'\n'))
            elif table.contains(a_command):
                output_file.write((f"{int(table.get_address(a_command)):016b}"+'\n'))
            else:
                table.add_entry(a_command, ram_address)
                output_file.write((f"{int(table.get_address(a_command)):016b}"+'\n'))
                ram_address += 1

        elif command_type == "C_COMMAND":
            comp = Code.comp_dict[parser.comp()]
            dest = Code.dest_dict[parser.dest()]
            jump = Code.jump_dict[parser.jump()]
            shift = parser.shift()
            c_instruction = shift + comp + dest + jump
            output_file.write((c_instruction+'\n'))


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
