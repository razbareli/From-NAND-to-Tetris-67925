"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        # tables. each entry will look like: {"name": [type, kind, #]}
        self.class_level = dict()
        self.subroutine_level = dict()
        # counters
        self.counters = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_level = dict()
        self.counters["ARG"] = 0
        self.counters["VAR"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in {"STATIC", "FIELD"}:
            self.class_level[name] = [type, kind, self.counters[kind]]
        if kind in {"ARG", "VAR"}:
            self.subroutine_level[name] = [type, kind, self.counters[kind]]
        self.counters[kind] += 1  # increase the counter of the variable kind

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.counters[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if self.subroutine_level.get(name) is not None:
            return self.subroutine_level[name][1]
        if self.class_level.get(name) is not None:
            return self.class_level[name][1]
        return "None"

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if self.subroutine_level.get(name) is not None:
            return self.subroutine_level[name][0]
        if self.class_level.get(name) is not None:
            return self.class_level[name][0]

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if self.subroutine_level.get(name) is not None:
            return self.subroutine_level[name][2]
        if self.class_level.get(name) is not None:
            return self.class_level[name][2]

    def is_var(self, name: str) -> bool:
        """returns true if the name is a variable in this table, false otherwise"""
        if self.subroutine_level.get(name) is not None:
            return True
        if self.class_level.get(name) is not None:
            return True
        return False
