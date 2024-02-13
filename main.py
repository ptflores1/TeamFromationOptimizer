import gurobipy as gp

from load_data import people, teams, n_people, n_teams, P, E, T, U, F, A, DA, DC, YO, UMin, UMax, S

m = gp.Model("teams")

# Create variables
X = {}
for i in range(n_people):
    for j in range(n_teams):
        X[f"x_{i}_{j}"] = m.addVar(vtype=gp.GRB.BINARY, name=f"x_{i}_{j}")

E_min = m.addVar(vtype=gp.GRB.INTEGER, name="E_min")
DA_min = m.addVar(vtype=gp.GRB.INTEGER, name="DA_min")
DC_min = m.addVar(vtype=gp.GRB.INTEGER, name="DC_min")
A_min = m.addVar(vtype=gp.GRB.INTEGER, name="A_min")

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

# Fix some people to some teams
m.addConstr(X[f"x_{people.index('catherine_parada')}_0"] == 1)
m.addConstr(X[f"x_{people.index('valentina_lopez')}_1"] == 1)
m.addConstr(X[f"x_{people.index('pablo_flores')}_2"] == 1)
m.addConstr(X[f"x_{people.index('josefina_sudy')}_3"] == 1)
m.addConstr(X[f"x_{people.index('santiago_herrera')}_3"] == 1)
m.addConstr(X[f"x_{people.index('matias_peñafiel')}_4"] == 1)
m.addConstr(X[f"x_{people.index('gonzalo_auquilen')}_5"] == 1)
m.addConstr(X[f"x_{people.index('josefina_moraga')}_5"] == 1)

for j in range(n_teams):
    # Limit min and max number of people in each team
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] for i in range(n_people)) >= UMin[j])
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] for i in range(n_people)) <= UMax[j])
    # Define E_min
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] * E[i] for i in range(n_people)) >= E_min)
    # Define DA_min
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] * DA[i] for i in range(n_people)) >= DA_min)
    # Define DC_min
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] * DC[i] for i in range(n_people)) >= DC_min)
    # Define A_min
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] * X[f"x_{ip}_{j}"] * A[i][ip] for i in range(n_people) for ip in range(i + 1, n_people)) >= A_min)

    # At least one person of each sex in each team
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] * (1 - S[i]) for i in range(n_people)) >= 1)
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] * S[i] for i in range(n_people)) >= 1)


for i in range(n_people):
    # Each person must be in one team
    m.addConstr(gp.quicksum(X[f"x_{i}_{j}"] for j in range(n_teams)) == 1)

    # Team age constraints
    m.addConstr(X[f"x_{i}_5"] * YO[i] + 24 * (1 - X[f"x_{i}_5"]) >= 24)
    m.addConstr(X[f"x_{i}_4"] * YO[i] + 21 * (1 - X[f"x_{i}_4"]) >= 21)
    
# Follow people's preferences
O1 = gp.quicksum(X[f"x_{i}_{j}"] * P[i][j] for i in range(n_people) for j in range(n_teams))
# Spread Experience over teams
O2 = gp.LinExpr() + E_min
# Prioritize people with education in the units
O3 = gp.quicksum(X[f"x_{i}_{j}"] * F[i][j] for i in range(n_people) for j in range(n_teams))
# Follow affinity between people
O4 = gp.LinExpr() + A_min

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