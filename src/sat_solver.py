from copy import deepcopy


class KnowledgeBase:
    def __init__(self):
        self.clauses = []

    def add_clause(self, clause):
        clause = sorted(list(set(clause)))
        if clause not in self.clauses:
            self.clauses.append(clause)

    def remove_clause(self, clause):
        clause = sorted(list(set(clause)))
        if clause in self.clauses:
            self.clauses.remove(clause)

    def infer(self, not_alpha):
        clauses = deepcopy(self.clauses) + [[not_alpha]]
        sat = self.__sat_solver(clauses, [])

        return sat is None
    
    def __literal_negation(self, literal):
        if literal[0] == '-':
            return literal[1:]
        else:
            return '-' + literal

    def __score(self, literal, clauses):
        score = 0
        for clause in clauses:
            if literal in clause:
                score += 2 ** (-len(clause))
        return score

    '''
    This is the DPLL algorithm
    but the heuristic is Jeroslow-Wang
    '''

    def __sat_solver(self, clauses, assignment):
        # print("clauses: ", clauses)
        # print("assignment: ", assignment)

        if all(any([literal in assignment for literal in clause]) for clause in clauses):
            return assignment

        if any(all([self.__literal_negation(literal) in assignment for literal in clause]) for clause in clauses):
            return None

        for clause in clauses:
            if len(clause) == 1:
                literal = clause[0]
                return self.__sat_solver([c for c in clauses if literal not in c],
                                         assignment + [literal])

        literals = [literal for clause in clauses
                    for literal in clause
                    if literal not in assignment
                    and self.__literal_negation(literal) not in assignment]

        if not literals:
            return None

        for literal in literals:
            if self.__literal_negation(literal) not in literals:
                return self.__sat_solver([clause for clause in clauses if literal not in clause],
                                         assignment + [literal])

        # literal_heuristic = {
        #     literal: self.__score(literal, clauses)
        #     for literal in literals
        # }

        # literal = max(literal_heuristic, key=literal_heuristic.get)
        literal = literals[0]

        result = self.__sat_solver([clause for clause in clauses if literal not in clause],
                                   assignment + [literal])

        if result is not None:
            return result

        result = self.__sat_solver([clause for clause in clauses if self.__literal_negation(literal) not in clause],
                                   assignment + [self.__literal_negation(literal)])

        if result is not None:
            return result

        return None
