"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        self.output_stream = output_stream
        self.loop_counter = 0
        # template for add, sub, and, or operations
        self.calculation = "@SP\n" + \
                           "AM=M-1\n" + \
                           "D=M\n" + \
                           "A=A-1\n"

        self.boolean_arithmetics = {"lt": "JLT", "gt": "JGT"}
        self.non_loop_arithmetics = {"add", "sub", "neg", "and", "or", "not"}
        # dictionary with asm code for all non loop arithmetics
        self.arithmetic_dict = {"add": self.calculation + "M=M+D\n"
            , "sub": self.calculation + "M=M-D\n"
            , "neg": "@SP\n" + \
                     "A=M-1\n" + \
                     "M=-M\n"
            , "and": self.calculation + "M=M&D\n"
            , "or": self.calculation + "M=M|D\n"
            , "not": "@SP\n" + \
                     "A=M-1\n" + \
                     "M=!M\n"
            , "shiftright": "@SP\n" + \
                            "A=M-1\n" + \
                            "M=M>>\n"
            , "shiftleft": "@SP\n" + \
                           "A=M-1\n" + \
                           "M=M<<\n"}

        # template for lg, gt and eq operations
        self.boolean = "@SP\n" + \
                       "AM=M-1\n" + \
                       "A=A-1\n" + \
                       "D=M\n"
        self.static_counter = 16
        self.file_name = ""
        self.segments = {"argument": "ARG", "local": "LCL", "this": "THIS", "that": "THAT"}

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        self.file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        if command in self.non_loop_arithmetics:
            # command is one of: and, sub, add, or, not, neg
            self.output_stream.write(self.arithmetic_dict[command])
        elif command == "eq":
            # command is eq
            ans = "@SP\n" + \
                  "AM=M-1\n" + \
                  "D=M\n" + \
                  "A=A-1\n"+\
                  "D=M-D\n"+ \
                  "@TRUE" + str(self.loop_counter) + "\n" + \
                  "D;JEQ\n" + \
                  "@FALSE" + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(TRUE" + str(self.loop_counter) + ")\n" + \
                  "@SP\n" + \
                  "A=M-1\n" + \
                  "M=-1\n" + \
                  "@END" + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(FALSE" + str(self.loop_counter) + ")\n" + \
                  "@SP\n" + \
                  "A=M-1\n" + \
                  "M=0\n" + \
                  "@END" + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(END" + str(self.loop_counter) + ")\n"

            self.loop_counter += 1
            self.output_stream.write(ans)
        else:
            # command is one of: lt, gt
            ans = "@SP\n" + \
                   "AM=M-1\n" + \
                   "A=A-1\n" + \
                   "D=M\n"+\
                   "@POSX" + str(self.loop_counter) + "\n" + \
                   "D;" + self.boolean_arithmetics[command] + "\n" + \
                   "@NEGX" + str(self.loop_counter) + "\n" + \
                   "0;JMP\n" + \
                   "(POSX" + str(self.loop_counter) + ")\n" + \
                   "@SP\n" + \
                   "A=M\n" + \
                   "D=M\n" + \
                   "@SAME_SIGN" + str(self.loop_counter) + "\n" + \
                   "D;" + self.boolean_arithmetics[command] + "\n" + \
                   "@TRUE" + str(self.loop_counter) + "\n" + \
                   "0;JMP\n" + \
                   "(NEGX" + str(self.loop_counter) + ")\n" + \
                   "@SP\n" + \
                   "A=M\n" + \
                   "D=M\n" + \
                   "@FALSE" + str(self.loop_counter) + "\n" + \
                   "D;" + self.boolean_arithmetics[command] + "\n" + \
                   "@SAME_SIGN" + str(self.loop_counter) + "\n" + \
                   "0;JMP\n" + \
                   "(SAME_SIGN" + str(self.loop_counter) + ")\n" + \
                   "@SP\n" + \
                   "A=M\n" + \
                   "D=M\n" + \
                   "A=A-1\n" + \
                   "D=M-D\n" + \
                   "@TRUE" + str(self.loop_counter) + "\n" + \
                   "D;" + self.boolean_arithmetics[command] + "\n" + \
                   "@FALSE" + str(self.loop_counter) + "\n" + \
                   "0;JMP\n" + \
                   "(TRUE" + str(self.loop_counter) + ")\n" + \
                   "@SP\n" + \
                   "A=M-1\n" + \
                   "M=-1\n" + \
                   "@END" + str(self.loop_counter) + "\n" + \
                   "0;JMP\n" + \
                   "(FALSE" + str(self.loop_counter) + ")\n" + \
                   "@SP\n" + \
                   "A=M-1\n" + \
                   "M=0\n" + \
                   "@END" + str(self.loop_counter) + "\n" + \
                   "0;JMP\n" + \
                   "(END" + str(self.loop_counter) + ")\n"
            self.loop_counter += 1
            self.output_stream.write(ans)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        ans = ""
        if command == "C_PUSH":

            if segment == "constant":
                ans += "@" + str(index) + "\n" + \
                       "D=A\n"

            elif segment == "static":
                ans += "@" + self.file_name + "." + str(index) + "\n" + \
                       "D=M\n"

            elif segment == "pointer":
                index += 3
                ans += "@" + str(index) + "\n" + \
                       "D=M\n"

            elif segment == "temp":
                ans += "@" + str(index + 5) + "\n" + \
                       "D=M\n"
            else:
                ans += "@" + self.segments[segment] + "\n" + \
                       "D=M\n" + \
                       "@" + str(index) + "\n" + \
                       "A=D+A\n" + \
                       "D=M\n"

            # the actual push operation and SP++
            ans += "@SP\n" + \
                   "A=M\n" + \
                   "M=D\n" + \
                   "@SP\n" + \
                   "M=M+1\n"

        elif command == "C_POP":

            if segment == "static":
                ans += "@" + self.file_name + "." + str(index) + "\n" + \
                       "D=A\n"

            elif segment == "pointer":
                index += 3
                ans += "@" + str(index) + "\n" + \
                       "D=A\n"

            elif segment == "temp":
                ans += "@" + str(index + 5) + "\n" + \
                       "D=A\n"
            else:
                ans += "@" + self.segments[segment] + "\n" + \
                       "D=M\n" + \
                       "@" + str(index) + "\n" + \
                       "D=D+A\n"

            # SP-- and the actual pop operation
            ans += "@R13\n" + \
                   "M=D\n" \
                   "@SP\n" + \
                   "M=M-1\n" + \
                   "A=M\n" + \
                   "D=M\n" + \
                   "@R13\n" + \
                   "A=M\n" + \
                   "M=D\n"
        self.output_stream.write(ans)

    def close(self) -> None:
        """Closes the output file."""
        self.output_stream.close()
