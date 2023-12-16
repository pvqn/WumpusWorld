'''
A util file for generating knowledge base of the agent

Atom form: <predicate>(<x>, <y>)

Clause form: [<operator>, <operand1>, <operand2>, ...]
'''


def to_cnf(phi):
    cnf = nnf(impl_free(phi))
    cnf = dist(cnf)
    cnf = associate(cnf)

    # Remove duplicates
    for i in range(1, len(cnf)):
        tmp = []
        for j in range(len(cnf[i])):
            if cnf[i][j] not in tmp:
                tmp.append(cnf[i][j])
        cnf[i] = tmp

    return cnf

"""
Remove implication, equivalence, and xor:
    - A => B becomes ~A | B
    - A <=> B becomes (~A | B) & (~B | A)
    - A <= B becomes A | ~B
    - A ^ B becomes (~A | B) & (A | ~B)
"""
def impl_free(phi):
    ops = ['=>', '<=>', '<=', '^']

    if phi[0] not in ops:
        return phi

    mapped = list(map(impl_free, phi[1:]))
    if phi[0] == '=>':
        return ['|', ['~', mapped[0]], mapped[1]]
    elif phi[0] == '<=':
        return ['|', mapped[0], ['~', mapped[1]]]
    elif phi[0] == '^':
        return ['|', ['&', mapped[0], ['~', mapped[1]]], ['&', ['~', mapped[0]], mapped[1]]]
    else:
        return ['&', ['|', ['~', mapped[0]], mapped[1]], ['|', ['~', mapped[1]], mapped[0]]]

"""
Push all the negation inwards:
    - ~~A becomes A
    - ~(A | B) becomes ~A & ~B
    - ~(A & B) becomes ~A | ~B
"""
def nnf(phi):
    if phi[0] == '~':
        if isinstance(phi[1], str):
            return phi
        elif phi[1][0] == '~':
            return nnf(phi[1][1])
        elif phi[1][0] == '|':
            return ['&', *[nnf(['~', x]) for x in phi[1][1:]]]
        elif phi[1][0] == '&':
            return ['|', *[nnf(['~', x]) for x in phi[1][1:]]]
    if phi[0] == '|':
        return ['|', *[nnf(x) for x in phi[1:]]]
    if phi[0] == '&':
        return ['&', *[nnf(x) for x in phi[1:]]]
    return phi

"""
After impl_free and nnf, distribute | over &:
    - A | (B & C) becomes (A | B) & (A | C)
    - (A & B) | C becomes (A | C) & (B | C)
"""
def dist(phi):
    if phi[0] == '|':
        if phi[1][0] == '&':
            return ['&', *[dist(['|', x] + phi[2:]) for x in phi[1][1:]]]
        elif phi[2][0] == '&':
            return ['&', *[dist(['|', phi[1]] + [x]) for x in phi[2][1:]]]
    elif phi[0] == '&':
        return ['&', *[dist(x) for x in phi[1:]]]
    return phi

"""
    From ['|', 'A', ['|', 'B', 'C']] to ['|', 'A', 'B', 'C']
"""
def associate(phi):
    associate_ops = ['|', '&']

    if len(phi) <= 2:
        return phi

    for i in range(1, len(phi)):
        phi[i] = associate(phi[i])

    if phi[0] in associate_ops:
        new_phi = [phi[0]]

        for i in range(1, len(phi)):
            if phi[i][0] == phi[0]:
                for j in range(1, len(phi[i])):
                    if phi[i][j] not in new_phi:
                        new_phi.append(phi[i][j])
            else:
                new_phi.append(phi[i])

        return new_phi

    return phi


def format_output(phi):
    if len(phi) == 1:
        return phi[0]
    if len(phi) == 2:
        return '~' + format_output(phi[1])
    if len(phi) >= 3:
        join = '('

        for i in range(1, len(phi)):
            join += format_output(phi[i]) + ' ' + phi[0] + ' '

        join = join[:-3] + ')'

        return join

# if __name__ == '__main__':
#     # print(impl_free(['=>', 'A', ['<=', 'B', 'C']]))
#     # print(impl_free(['=>', 'A', ['^', 'B', 'C']]))
#     # print(impl_free(['A']))
#     # print(nnf(['~', ['|', ['~', 'A'], 'B']]))
#     clause = ['|', ['|', 'p', ['~', 'q']], ['&', 'p', ['|', ['~', 'r'], 'q']]]

#     # print(format_output(
#     #     clause
#     # ))

#     # print(format_output(
#     #     to_cnf(clause)
#     # ))
