import copy

class KnowledgeBase:
    def __init__(self):
        self.clauses = []

    def add_clause(self, clause):
        # Add a clause to the Knowledge Base if it's not already present
        clause = sorted(list(set(clause)))  # Remove duplicates and sort for consistency
        if clause not in self.clauses:
            self.clauses.append(clause)

    def del_clause(self, clause):
        # Remove a clause from the Knowledge Base if it exists
        clause = sorted(list(set(clause)))
        if clause in self.clauses:
            self.clauses.remove(clause)

    def infer(self, not_alpha):
        # Perform inference to check whether a logical statement is satisfiable or not
        clause_list = copy.deepcopy(self.clauses)
        negative_alpha = not_alpha
        for it in negative_alpha:
            clause_list.append(it)
        solution = self.dpll(clause_list, [])
        return solution is None

    def dpll(self, clauses, assignment=[]):
        # If every clause is satisfied, return the assignment
        if all(any(literal in assignment for literal in clause) for clause in clauses):
            return assignment

        # Select the variable with the highest Jeroslow-Wang score
        literals = [literal for clause in clauses for literal in clause if literal not in assignment and ('-' + literal) not in assignment]
        if not literals:
            return None
        scores = {literal: sum(2**-len(clause) for clause in clauses if literal in clause) for literal in literals}
        literal = max(scores, key=scores.get)

        # Try assigning the literal to True
        result = self.dpll([clause for clause in clauses if literal not in clause], assignment + [literal])
        if result is not None:
            return result

        # If that didn't work, try assigning the literal to False
        result = self.dpll([[-lit if lit[0] == '-' else '-' + lit for lit in clause if lit != '-' + literal] for clause in clauses if '-' + literal not in clause], assignment + ['-' + literal])
        if result is not None:
            return result

        # If neither worked, the formula is unsatisfiable
        return None

def solve_sat(formula):
    # Remove parentheses
   # Remove parentheses
    formula = formula.replace("(", "").replace(")", "")
    
    # Convert the formula into a list of clauses
    clauses = [clause.split(' or ') for clause in formula.split(" and ")]

    # Instantiate KnowledgeBase and add clauses
    kb = KnowledgeBase()
    for clause in clauses:
        kb.add_clause(clause)

    # Start the DPLL algorithm with an empty assignment
    return kb.dpll(clauses)

# testing sat solver with complex formula
formula="(-A or B or -C) and (A or -B or C) and (-A or -B or -C) and (A or B or C)"
print("Formula: " + formula)
print("Solution: " + str(solve_sat(formula)))
print()


