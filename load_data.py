import csv
import difflib

teams = ["bandada", "manada", "compañia", "tropa", "avanzada", "clan"]
people = ["Catherine Parada", "Mauricio Carrasco", "Isidora Cortes", "Isidora Olivares", "Viviana Vargas", "Catalina Galvez", "Emma Corona", "Antara Neira", "Martina Carvajal", "Valentina Lopez", "Carolina Lillo", "Camila Olave", "Benjamin Oliva", "Jorge Ramirez", "Rosario Seguel", "Pablo Flores", "Josefina Sudy", "Marco Guzman", "Erick Ukrow", "Matias Peñafiel", "Eileen Peragallo", "Nicolas Llanos", "Gonzalo Auquilen", "Josefina Moraga", "Santiago Herrera"]
people = [x.lower().replace(" ", "_") for x in people]
n_teams = len(teams)
n_people = len(people)

preference2value = {"Primera Preferencia": 3, "Segunda Preferencia": 2, "Tercera Preferencia": 1, "Ninguna": 0}
education2value = {"Ninguno": 0, "Curso Medio (nivel en progreso o por comenzar)": 1, "Nivel Medio": 2, "Curso Avanzado (nivel en progreso o por comenzar)": 3, "Nivel Avanzado": 4}

with open("data.csv", "r") as file:
    reader = list(csv.reader(file))

P = [[0 for _ in range(n_teams)] for _ in range(n_people)] # (people, n_teams)
E = [0 for _ in range(n_people)] # (n_people)
T = [0 for _ in range(n_people)] # (n_people)
U = [[0 for _ in range(n_teams)] for _ in range(n_people)] # (n_people, n_teams)
F = [[0 for _ in range(n_teams)] for _ in range(n_people)] # (n_people, n_teams)
A = [[0. for _ in range(n_people)] for _ in range(n_people)] # (n_people, n_people)
DA = [0. for _ in range(n_people)] # (n_people)
DC = [0. for _ in range(n_people)] # (n_people)


for row in reader[1:]:
    p_idx = people.index(difflib.get_close_matches(row[1], people)[0])
    if row[2] != "Ninguna":
        U[p_idx][teams.index(row[2].lower())] = 1
    T[p_idx] = int(row[3])
    E[p_idx] = int(row[4])
    for i in range(5, 11):
        P[p_idx][i - 5] = preference2value[row[i]]
    DA[p_idx] = int(row[11]) / 100
    DC[p_idx] = int(row[12]) / 100
    for i in range(13, 19):
        F[p_idx][i - 13] = education2value[row[i]]
    for p in row[19].split(", "):
        A[p_idx][people.index(p.lower().replace(" ", "_"))] += .5
