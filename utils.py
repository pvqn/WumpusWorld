import sys
import re
from enum import Enum

"""
The knowledge base for the Wumpus World.

The literals is represented with the form:
    <state>(<x>, <y>)

Where <state> is one of the following:
    - B(x, y): Breeze, there is a pit nearby
    - S(x, y): Stench, there is a wumpus nearby
    - T(x, y): Treasure, there is a treasure at this location
    - P(x, y): Pit, there is a pit at this location
    - W(x, y): Wumpus, there is a wumpus at this location
    - A(x, y): Agent, the agent is at this location
    - V(x, y): Visited, the agent has visited this location

Operators:
    - & : and
    - | : or
    - ~ : not
    - =>: implication
    - <=>: equivalence
Example:
    If the original rule is:
        B(1, 1) & S(1, 1) => P(1, 2) | P(2, 1)
    It should be converted to:
        ['=>', ['&', 'B(1, 1)', 'S(1, 1)'], ['|', 'P(1, 2)', 'P(2, 1)']]

NOTE: the tuple with operations have the following form:
    (operator, lhs, rhs)
    where
        operator: one of the operators defined above
        lhs: left hand side of the operator
        rhs: right hand side of the operator
    
    This makes the result rule forms a binary tree
    Or duplicate atoms might be observed in the rule

    For example: 
    (((P | ~Q) | P) & ((P | ~Q) | (~R | Q)))
    instead of:
    ((P | ~Q | P) & (P | ~Q | ~R | Q))

    This ensures that the recusion is implemented quicker

All the rules are stored in a list and converted to CNF form.
"""


class Operators(Enum):
    AND = "&"
    OR = "|"
    NOT = "~"
    IMPLICATION = "=>"
    EQUIVALENCE = "<=>"


class KB:
    def __init__(self):
        self.rules = []

    def tell(self, rule):
        raise NotImplementedError

    def ask(self, query):
        raise NotImplementedError

    def to_cnf(self, rule):
        '''
        Algorithm based on:
        Logic in Computer Science, Modelling and Reasoning about Systems, 2nd Edition
        '''

        impl_free = self.impl_free(rule)
        nnf = self.nnf(impl_free)

        if self.is_literal(nnf):
            return nnf
        else:
            if nnf[0] == Operators.AND.value:
                return [
                    Operators.AND.value,
                    self.to_cnf(nnf[1]),
                    self.to_cnf(nnf[2])
                ]
            elif nnf[0] == Operators.OR.value:
                return self.distr(
                    self.to_cnf(nnf[1]),
                    self.to_cnf(nnf[2])
                )

            raise "Uh-oh! We should not be here!"

    def impl_free(self, rule):
        if self.is_literal(rule):
            return rule

        # print(rule)

        if rule[0] == Operators.NOT.value:
            return [
                Operators.NOT.value,
                self.impl_free(rule[1])
            ]
        elif rule[0] == Operators.EQUIVALENCE.value:
            return [
                Operators.AND.value,
                self.impl_free([
                    Operators.IMPLICATION.value,
                    rule[1],
                    rule[2]
                ]),
                self.impl_free([
                    Operators.IMPLICATION.value,
                    rule[2],
                    rule[1]
                ])
            ]
        elif rule[0] == Operators.IMPLICATION.value:
            return [
                Operators.OR.value,
                self.impl_free([
                    Operators.NOT.value,
                    rule[1]
                ]),
                self.impl_free(rule[2])
            ]
        else:
            return [
                rule[0],
                self.impl_free(rule[1]),
                self.impl_free(rule[2])
            ]

    def nnf(self, rule):
        if self.is_literal(rule):
            if rule[0] == Operators.NOT.value and rule[1][0] == Operators.NOT.value:
                return self.nnf(rule[1][1])
            else:
                return rule

        if rule[0] == Operators.NOT.value:
            if rule[1][0] == Operators.AND.value:
                return [Operators.OR.value, self.nnf(['~', rule[1][1]]), self.nnf(['~', rule[1][2]])]
            elif rule[1][0] == Operators.OR.value:
                return [Operators.AND.value, self.nnf(['~', rule[1][1]]), self.nnf(['~', rule[1][2]])]

        if rule[0] == Operators.AND.value:
            return [Operators.AND.value, self.nnf(rule[1]), self.nnf(rule[2])]
        elif rule[0] == Operators.OR.value:
            return [Operators.OR.value, self.nnf(rule[1]), self.nnf(rule[2])]

    def distr(self, clause1, clause2):
        '''
        Consider: clause1 | clause2

        Case 1:
            <clause1> := <clause11> & <clause12>
            => distr(clause) = distr(clause11+clause2) & distr(clause12+clause2)

        Case 2:
            <clause2> := <clause21> & <clause22>
            => distr(clause) = distr(clause1+clause21) & distr(clause1+clause22)

        Else:
            return clause
        '''

        if clause1[0] == Operators.AND.value:
            return [
                Operators.AND.value,
                self.distr(clause1[1], clause2),
                self.distr(clause1[2], clause2)
            ]
        elif clause2[0] == Operators.AND.value:
            return [
                Operators.AND.value,
                self.distr(clause1, clause2[1]),
                self.distr(clause1, clause2[2])
            ]
        else:
            return [
                Operators.OR.value,
                clause1,
                clause2
            ]

    def is_literal(self, rule):
        '''
        <literal> ::= <state>(<x>, <y>) | ['~', <state>(<x>, <y>)]
        '''
        if isinstance(rule, list):
            return rule[0] == Operators.NOT.value and self.is_literal(rule[1])
        else:
            return isinstance(rule, str)

    def to_str(self, rule):
        if self.is_literal(rule):
            return ''.join(rule)
        else:
            # Case 1: Negation
            if rule[0] == Operators.NOT.value:
                return f"({rule[0]}{self.to_str(rule[1])})"
            return f"({self.to_str(rule[1])} {rule[0]} {self.to_str(rule[2])})"


def testing():
    kb = KB()

    # convert1 = kb.impl_free(
    #     ['=>', ['&', 'B(1, 1)', ['~', 'S(1, 1)']], ['|', 'P(1, 2)', 'P(2, 1)']])
    # print(convert1)

    # convert1 = kb.impl_free(
    #     ['=>', ['~', 'S(1, 1)'], ['|', 'P(1, 2)', 'P(2, 1)']])
    # print(convert1)

    # Testing equivalence in equivalence
    # ¬p ∧ q → p ∧ (r → q)
    clause = ['=>', ['&', ['~', 'P'], 'Q'], ['&', 'P', ['=>', 'R', 'Q']]]

    # convert = kb.impl_free(clause)
    # print("IMPL_FREE =", kb.to_str(convert))

    # convert = kb.nnf(convert)
    # print("NNF =", kb.to_str(convert))

    print("CNF =", kb.to_str(kb.to_cnf(clause)))

    # print("Test negation")
    # convert2 = kb.nnf(['&', 'B(1, 1)', 'S(1, 1)'])
    # print(convert2)

    # convert2 = kb.nnf(['|', 'P(1, 2)', 'P(2, 1)'])
    # print(convert2)

    # convert2 = kb.nnf(['~', 'S(1, 1)'])
    # print(convert2)


if __name__ == "__main__":
    testing()
