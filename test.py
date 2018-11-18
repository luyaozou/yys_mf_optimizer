#! encoding = utf-8

import pulp

LEVEL_NUM = 5
CREEP_NUM = 3
STAMINA = [3, 3, 3, 3, 6]
TABLE = [[2, 0, 0, 1, 1],
         [1, 2, 1, 0, 0],
         [0, 0, 0, 3, 1]]
CONSTRAINT = [8, 13, 2]  # len(OBJECTIVE) == CREEP_NUM

prob = pulp.LpProblem(name = 'yys_test', sense=pulp.LpMinimize)

var_name = ["x{:d}".format(i) for i in range(5)]

variable = [pulp.LpVariable(var_name[i], lowBound=0, cat=pulp.LpInteger) for i in range (5)]

obj = pulp.LpAffineExpression([(variable[i], STAMINA[i]) for i in range(LEVEL_NUM)])

# objective function
prob +=  pulp.lpSum(obj)

# adding constraint

for i in range(CREEP_NUM):
    prob += sum(variable[j] * TABLE[i][j] for j in range(LEVEL_NUM)) >= CONSTRAINT[i]

prob.solve()

# print
print('status'), pulp.LpStatus[prob.status]

for v in prob.variables():
    print("{:s}={:g}".format(v.name, v.varValue))
