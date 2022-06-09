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
        # the stream to write onto
        self.output_stream = output_stream
        # counter for loop labels
        self.loop_counter = 0
        # counter for return labels
        self.return_counter = 0
        # the name of the vm file we are processing
        self.file_name = ""

        # dictionaries
        self.boolean_arithmetics = {"lt": "JLT", "gt": "JGT"}
        self.non_loop_arithmetics = {"add", "sub", "neg", "and", "or", "not", "shiftright", "shiftleft"}
        self.segments = {"argument": "ARG", "local": "LCL", "this": "THIS", "that": "THAT"}

        # templates for translation:
        # template for add, sub, and, or operations
        self.calculation = "@SP\n" + \
                           "AM=M-1\n" + \
                           "D=M\n" + \
                           "A=A-1\n"
        # dictionary with asm code for all non loop arithmetics
        self.arithmetic_dict = {"add": self.calculation + "M=M+D\n"
            , "sub": self.calculation + "M=M-D\n"
            , "neg": "@SP\n" +
                     "A=M-1\n" +
                     "M=-M\n"
            , "and": self.calculation + "M=M&D\n"
            , "or": self.calculation + "M=M|D\n"
            , "not": "@SP\n" +
                     "A=M-1\n" +
                     "M=!M\n"
            , "shiftright": "@SP\n" +
                            "A=M-1\n" +
                            "M=M>>\n"
            , "shiftleft": "@SP\n" +
                           "A=M-1\n" +
                           "M=M<<\n"}
        # template for lg, gt and eq operations
        self.boolean = "@SP\n" + \
                       "AM=M-1\n" + \
                       "A=A-1\n" + \
                       "D=M\n"
        # template for push: push the value held in D to the main stack, and SP++
        self.push = "@SP\n" + \
                    "A=M\n" + \
                    "M=D\n" + \
                    "@SP\n" + \
                    "M=M+1\n"
        # template for pop: SP-- and the actual pop operation.
        # pops to the address that is held in D
        self.pop = "@R13\n" + \
                   "M=D\n" \
                   "@SP\n" + \
                   "M=M-1\n" + \
                   "A=M\n" + \
                   "D=M\n" + \
                   "@R13\n" + \
                   "A=M\n" + \
                   "M=D\n"

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
                  "A=A-1\n" + \
                  "D=M-D\n" + \
                  "@TRUE" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "D;JEQ\n" + \
                  "@FALSE" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(TRUE" + "$" + self.file_name + "." + str(self.loop_counter) + ")\n" + \
                  "@SP\n" + \
                  "A=M-1\n" + \
                  "M=-1\n" + \
                  "@END" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(FALSE" + "$" + self.file_name + "." + str(self.loop_counter) + ")\n" + \
                  "@SP\n" + \
                  "A=M-1\n" + \
                  "M=0\n" + \
                  "@END" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(END" + "$" + self.file_name + "." + str(self.loop_counter) + ")\n"

            self.loop_counter += 1
            self.output_stream.write(ans)
        else:
            # command is one of: lt, gt
            ans = "@SP\n" + \
                  "AM=M-1\n" + \
                  "A=A-1\n" + \
                  "D=M\n" + \
                  "@POSX" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "D;" + self.boolean_arithmetics[command] + "\n" + \
                  "@NEGX" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(POSX" + "$" + self.file_name + "." + str(self.loop_counter) + ")\n" + \
                  "@SP\n" + \
                  "A=M\n" + \
                  "D=M\n" + \
                  "@SAME_SIGN" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "D;" + self.boolean_arithmetics[command] + "\n" + \
                  "@TRUE" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(NEGX" + "$" + self.file_name + "." + str(self.loop_counter) + ")\n" + \
                  "@SP\n" + \
                  "A=M\n" + \
                  "D=M\n" + \
                  "@FALSE" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "D;" + self.boolean_arithmetics[command] + "\n" + \
                  "@SAME_SIGN" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(SAME_SIGN" + "$" + self.file_name + "." + str(self.loop_counter) + ")\n" + \
                  "@SP\n" + \
                  "A=M\n" + \
                  "D=M\n" + \
                  "A=A-1\n" + \
                  "D=M-D\n" + \
                  "@TRUE" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "D;" + self.boolean_arithmetics[command] + "\n" + \
                  "@FALSE" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(TRUE" + "$" + self.file_name + "." + str(self.loop_counter) + ")\n" + \
                  "@SP\n" + \
                  "A=M-1\n" + \
                  "M=-1\n" + \
                  "@END" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(FALSE" + "$" + self.file_name + "." + str(self.loop_counter) + ")\n" + \
                  "@SP\n" + \
                  "A=M-1\n" + \
                  "M=0\n" + \
                  "@END" + "$" + self.file_name + "." + str(self.loop_counter) + "\n" + \
                  "0;JMP\n" + \
                  "(END" + "$" + self.file_name + "." + str(self.loop_counter) + ")\n"
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
            ans += self.push

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

            # SP-- and the actual pop operation. pops to the address that is held in D
            ans += self.pop

        self.output_stream.write(ans)

    def write_branching(self, command: str, label: str) -> None:
        """Writes the assembly code that is the translation of the given
                command, where command is either C_GOTO, C_IF or C_LABEL.

        Args:
            command (str): C_GOTO, C_IF or C_LABEL.
            label (str): the label to go to
        """
        ans = ""
        if command == "C_GOTO":
            ans += "@" + label + "\n" + \
                   "0;JMP\n"
        elif command == "C_LABEL":
            ans += "(" + label + ")\n"
        elif command == "C_IF":
            ans += "@SP\n" + \
                   "AM=M-1\n" \
                   "D=M\n" + \
                   "@" + label + "\n" + \
                   "D;JNE\n"
        self.output_stream.write(ans)

    def write_call(self, func_name: str, n_args: int) -> None:
        """Writes the assembly code for calling a function.
        Args:
            func_name (str): the name of the function we are calling
            n_args (int): number of arguments that the function has
        """
        ans = ""
        ans += "@" + func_name + "$ret" + str(self.return_counter) + '\n' \
                                                              "D=A\n" + \
               self.push + \
               "@LCL\n" \
               "D=M\n" + \
               self.push + \
               "@ARG\n" \
               "D=M\n" + \
               self.push + \
               "@THIS\n" \
               "D=M\n" + \
               self.push + \
               "@THAT\n" \
               "D=M\n" + \
               self.push + \
               "@SP\n" + \
               "D=M\n" + \
               "@5\n" + \
               "D=D-A\n" + \
               "@" + str(n_args) + "\n" + \
               "D=D-A\n" + \
               "@ARG\n" + \
               "M=D\n" + \
               "@SP\n" + \
               "D=M\n" + \
               "@LCL\n" + \
               "M=D\n" + \
               "@" + func_name + '\n' + \
               "0;JMP\n" + \
               "(" + func_name + "$ret" + str(self.return_counter) + ")\n"

        self.return_counter += 1
        self.output_stream.write(ans)

    def write_function(self, func_name: str, n_vars: int) -> None:
        """Writes the assembly code for executing a function.
        Args:
            func_name (str): the name of the function we are calling
            n_vars (int): number of variables that the function has
        """
        ans = ""
        ans += "(" + func_name + ")\n"
        for i in range(n_vars):
            ans += "@0\n" + \
                   "D=A\n" + \
                   self.push
        self.output_stream.write(ans)

    def write_return(self) -> None:
        """Writes the assembly code for returning an argument from a function"""
        ans = ""
        ans += "@LCL\n" + \
               "D=M\n" + \
               "@R14\n" + \
               "M=D\n" + \
               "@5\n" + \
               "A=D-A\n" + \
               "D=M\n" + \
               "@R15\n" + \
               "M=D\n" + \
               "@ARG\n" + \
               "D=M\n" + \
               self.pop + \
               "@ARG\n" + \
               "D=M\n" + \
               "@SP\n" + \
               "M=D+1\n"
        restoration = ["THAT", "THIS", "ARG", "LCL"]
        for i in restoration:
            ans += "@R14\n" + \
                   "MD=M-1\n" + \
                   "A=D\n" + \
                   "D=M\n" + \
                   "@" + i + '\n' + \
                   "M=D\n"
        ans += "@R15\n" + \
               "A=M\n" + \
               "0;JMP\n"

        self.output_stream.write(ans)

    def write_init(self):
        """writes the assembly code for initializing the VM"""
        ans = ""
        ans += "@256\n" + \
               "D=A\n" + \
               "@SP\n" + \
               "M=D\n"
        self.output_stream.write(ans)
        self.write_call("Sys.init", 0)

    def close(self) -> None:
        """Closes the output file."""
        self.output_stream.close()
