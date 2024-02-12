import gurobipy as gp

from load_data import people, teams, n_people, n_teams, P, E, T, U, F, A, DA, DC

m = gp.Model("teams")

# Create variables
X = {}
for i in range(n_people):
    for j in range(n_teams):
        X[f"x_{i}_{j}"] = m.addVar(vtype=gp.GRB.BINARY, name=f"x_{i}_{j}")

E_min = m.addVar(vtype=gp.GRB.INTEGER, name="E_min")
DA_min = m.addVar(vtype=gp.GRB.INTEGER, name="DA_min")
DC_min = m.addVar(vtype=gp.GRB.INTEGER, name="DC_min")

# Load parameters

lam_1 = 1
lam_2 = 1
lam_3 = 1
lam_4 = 1
lam_5 = 1
lam_6 = 1
lam_7 = 1
lam_8 = 1

# Add constraints
for j in range(n_teams):
    # Each team must have at least 3 people
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] for i in range(n_people)) >= 3)
    # Each team must have at most 6 people
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] for i in range(n_people)) <= 6)
    # Define E_min
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] * E[i] for i in range(n_people)) >= E_min)
    # Define DA_min
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] * DA[i] for i in range(n_people)) >= DA_min)
    # Define DC_min
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] * DC[i] for i in range(n_people)) >= DC_min)

for i in range(n_people):
    # Each person must be in one team
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] for j in range(n_teams)) == 1)
    
# Follow people's preferences
O1 = gp.quicksum(X[f"x_{i}_{j}"] * P[i][j] for i in range(n_people) for j in range(n_teams))
# Spread Experience over teams
O2 = gp.LinExpr() + E_min
# Prioritize people with education in the units
O3 = gp.quicksum(X[f"x_{i}_{j}"] * F[i][j] for i in range(n_people) for j in range(n_teams))
# Follow affinity between people
O4 = gp.quicksum(X[f"x_{i}_{j}"] * X[f"x_{ip}_{j}"] * A[i][ip] for i in range(n_people) for ip in range(i + 1, n_people) for j in range(n_teams))

O5 = gp.LinExpr()
O6 = gp.LinExpr()
for i in range(n_people):
    # People with little time in the unit should stay
    if T[i] <= 2:
        O5 += gp.quicksum(X[f"x_{i}_{j}"] * U[i][j] for j in range(n_teams))
    # People with a lot of time in the unit should leave
    if T[i] >= 4:
        O6 -= gp.quicksum(X[f"x_{i}_{j}"] * U[i][j] for j in range(n_teams))
# Spread availabilities over teams
O7 = gp.LinExpr() + DA_min
O8 = gp.LinExpr() + DC_min

# Set objective
m.setObjective(lam_1 * O1 + lam_2 * O2 + lam_3 * O3 + lam_4 * O4 + lam_5 * O5 + lam_6 * O6 + lam_7 * O7 + lam_8 * O8, gp.GRB.MAXIMIZE)


m.optimize()

for j in range(n_teams):
    print(f'{teams[j].capitalize()}:')
    for i in range(n_people):
        if X[f'x_{i}_{j}'].x > 0:
            print(f'\t{people[i].replace("_", " ").title()}')
    print()

print("O1:", O1.getValue())
print("O2:", O2.getValue())
print("O3:", O3.getValue())
print("O4:", O4.getValue())
print("O5:", O5.getValue())
print("O6:", O6.getValue())
print("O7:", O7.getValue())
print("O8:", O8.getValue())