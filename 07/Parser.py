"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        # input_lines = input_file.read().splitlines()
        self.input_lines = input_file.read().splitlines()
        self.current_command = None
        self.num_of_lines = len(self.input_lines)
        self.current_index = 0
        self.arithmetic_set = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
        self.memory_set = {"pop": "C_POP", "push": "C_PUSH"}

    def pre_process(self) -> None:
        """deletes all empty lines or lines that are only comments"""
        lines_to_delete = []
        for line in range(self.num_of_lines):
            if self.input_lines[line] == "" or self.input_lines[line].strip()[0] == '/':
                lines_to_delete.append(line)
        for line in reversed(lines_to_delete):
            del self.input_lines[line]
            self.num_of_lines -= 1

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        if self.current_index == self.num_of_lines:
            return False
        return True

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        # Your code goes here!
        self.current_command = self.input_lines[self.current_index]
        comment_pos = self.current_command.find('/')
        if comment_pos != -1:
            self.current_command = self.current_command[:comment_pos]
        self.current_command = self.current_command.strip()
        self.mac = self.current_command.split()
        self.current_index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # Your code goes here!
        if self.current_command in self.arithmetic_set:
            return "C_ARITHMETIC"
        return self.memory_set[self.mac[0]]

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        # Your code goes here!
        if self.command_type() == "C_ARITHMETIC":
            return self.mac[0]
        return self.mac[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        # Your code goes here!
        return int(self.mac[2])
