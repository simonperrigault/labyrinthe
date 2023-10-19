from collections import defaultdict
import tkinter as tk
import math
import time

fichier = "cartes/carte.txt"
COULEUR_MUR = "grey"
COULEUR_SOL = "white"
COULEUR_FLECHE = "yellow"
COLONNES_MAX = 200
LIGNES_MAX = 100

class Fenetre:
    def __init__(self, carte, parcours="astar"):
        self.carte = carte
        self.depart = None
        self.arrivee = None
        self.carreaux = []

        self.fenetre = tk.Tk()
        self.width = self.fenetre.winfo_screenwidth()-200
        self.height = self.fenetre.winfo_screenheight()-200
        self.fenetre.geometry(f"{self.width}x{self.height+50}+10+10")

        self.taille_carreau = min(self.width//len(self.carte[0]), self.height//len(self.carte))
        self.canvas = tk.Canvas(self.fenetre, background=COULEUR_SOL)
        self.canvas.pack(expand=True, fill="both")
        self.creer_carte()

        frame = tk.Frame(self.fenetre, bg="red").pack(side="bottom")
        self.choix_parcours = tk.StringVar(value=parcours)
        tk.Radiobutton(frame, text="A*",font=("Arial", 16), variable=self.choix_parcours, value="astar", command=self.again).pack(side="left")
        tk.Radiobutton(frame, text="BFS",font=("Arial", 16), variable=self.choix_parcours, value="bfs", command=self.again).pack(side="left")
        self.label_time = tk.Label(frame, text=f"Temps d'exécution : 0", font=("Arial", 14))
        self.label_time.pack(side="left", padx=20)

        tk.Button(frame, text="Again", command=self.again, bg="lightblue", width=50).pack(side="right",fill="both", padx=20)

        tk.Button(frame, text="Changer la carte", bg="lightblue", width=50, command=self.dessin_carte).pack(side="right", fill="both", padx=20)

        self.fenetre.mainloop()
    
    def creer_carte(self):
        for i in range(len(self.carte)):
            self.carreaux.append([])
            for j in range(len(self.carte[i])):
                haut_gauche = (j*self.taille_carreau, i*self.taille_carreau)
                bas_droite = ((j+1)*self.taille_carreau, (i+1)*self.taille_carreau)
                rempli = COULEUR_SOL if self.carte[i][j] == "-" else COULEUR_MUR
                curr = self.canvas.create_rectangle(haut_gauche, bas_droite, fill=rempli, width=1)
                self.carreaux[i].append(curr)
                self.canvas.tag_bind(curr, "<Button-1>", lambda event, id=curr, row=i, col=j : self.choix_depart_arrivee(event, id, row, col))
    
    def choix_depart_arrivee(self, event, id, row, col):
        if self.canvas.itemcget(id, "fill") == COULEUR_MUR: return
        if self.depart is None:
            self.depart = (row, col)
            self.canvas.itemconfigure(id, fill="green")
        elif self.arrivee is None:
            debut = time.time()
            self.arrivee = (row, col)
            self.canvas.itemconfigure(id, fill="red")
            chemin = self.astar() if self.choix_parcours.get() == "astar" else self.bfs()
            self.label_time["text"] = f"Temps d'exécution : {time.time()-debut : .4f} s"
            if chemin is None:
                self.again()
                return
            chemin = [(b*self.taille_carreau+self.taille_carreau//2, a*self.taille_carreau+self.taille_carreau//2) for (a,b) in chemin]
            self.canvas.create_line(chemin, fill=COULEUR_FLECHE, width=2, arrow="last")
            
    
    def bfs(self):
        graph = defaultdict(list)
        for i in range(len(self.carte)):
            for j in range(len(self.carte[i])):
                if self.carte[i][j] == "-":
                    if i > 0 and self.carte[i-1][j] == "-": graph[(i,j)].append((i-1, j))
                    if j > 0 and self.carte[i][j-1] == "-": graph[(i,j)].append((i, j-1))
                    if i < len(self.carte)-1 and self.carte[i+1][j] == "-": graph[(i,j)].append((i+1, j))
                    if j < len(self.carte[i])-1 and self.carte[i][j+1] == "-": graph[(i,j)].append((i, j+1))

        queue = [self.depart]
        visite = {self.depart : [self.depart]}
        while queue:
            curr = queue.pop(0)
            if curr != self.depart:
                self.canvas.itemconfigure(self.carreaux[curr[0]][curr[1]], fill="lightblue")
            for v in graph[curr]:
                if not v in visite:
                    queue.append(v)
                    visite[v] = visite[curr]+[v]
                    if v == self.arrivee: return visite[v]
                    self.canvas.itemconfigure(self.carreaux[v[0]][v[1]], fill="lightgreen")
    
    def astar(self):
        graph = defaultdict(list)
        for i in range(len(self.carte)):
            for j in range(len(self.carte[i])):
                if self.carte[i][j] == "-":
                    if i > 0 and self.carte[i-1][j] == "-": graph[(i,j)].append((i-1, j))
                    if j > 0 and self.carte[i][j-1] == "-": graph[(i,j)].append((i, j-1))
                    if i < len(self.carte)-1 and self.carte[i+1][j] == "-": graph[(i,j)].append((i+1, j))
                    if j < len(self.carte[i])-1 and self.carte[i][j+1] == "-": graph[(i,j)].append((i, j+1))
        
        open_list = {self.depart: [0, 0, None]} # sommet : [distance depart, distance arrivee, parent]
        closed_list = {}
        while len(open_list) > 0:
            curr = Fenetre.find_min(open_list)
            if curr != self.depart:
                self.canvas.itemconfigure(self.carreaux[curr[0]][curr[1]], fill="lightblue")
            for voisin in graph[curr]:
                new_w = open_list[curr][0] + 1
                distance = Fenetre.distance(voisin, self.arrivee)
                if voisin in closed_list: continue
                if not voisin in open_list or new_w + distance < open_list[voisin][0]+open_list[voisin][1]:
                    open_list[voisin] = [new_w, distance, curr]
                if voisin == self.arrivee:
                    closed_list[voisin] = open_list[voisin][2]
                    closed_list[curr] = open_list[curr][2]
                    chemin = [self.arrivee]
                    while chemin[0] != self.depart:
                        chemin.insert(0, closed_list[chemin[0]])
                    return chemin
                self.canvas.itemconfigure(self.carreaux[voisin[0]][voisin[1]], fill="lightgreen")
            closed_list[curr] = open_list[curr][2]
            open_list.pop(curr)
        
    def again(self):
        self.fenetre.destroy()
        Fenetre(self.carte, self.choix_parcours.get())
    
    def dessin_carte(self):
        self.fenetre.destroy()
        DessinCarte(self.carte)
    
    @staticmethod
    def find_min(dic):
        som_min, mini = (0,0), math.inf
        for som, tup in dic.items():
            if tup[0]+tup[1] < mini:
                mini = tup[0]+tup[1]
                som_min = som
        return som_min
    
    def distance(depart, arrivee):
        # return abs(depart[0]-arrivee[0])+abs(depart[1]-arrivee[1])
        # return math.sqrt((depart[0]-arrivee[0])**2+(depart[1]-arrivee[1])**2)
        return (depart[0]-arrivee[0])**2+(depart[1]-arrivee[1])**2
    

class DessinCarte:
    def __init__(self, carte):
        self.carreaux = []
        self.carte = carte

        self.fenetre = tk.Tk()
        self.width = self.fenetre.winfo_screenwidth()-200
        self.height = self.fenetre.winfo_screenheight()-200
        self.fenetre.geometry(f"{self.width}x{self.height+50}+10+10")

        self.taille_carreau = min(self.width//len(self.carte[0]), self.height//len(self.carte))
        self.canvas = tk.Canvas(self.fenetre, background=COULEUR_SOL)
        self.canvas.pack(expand=True, fill="both")
        self.creer_carte()
        self.canvas.bind("<B1-Motion>", self.ajouter_mur)
        self.canvas.bind("<B3-Motion>", self.enlever_mur)

        self.nombre_lignes = tk.IntVar(self.fenetre, str(len(self.carte)))
        self.nombre_colonnes = tk.IntVar(self.fenetre, str(len(self.carte[0])))
        frame = tk.Frame(self.fenetre)
        frame.pack(side="bottom", fill="both")

        tk.Label(frame, text=f"Nombre de lignes :").pack(side="left", padx=20)
        tk.Scale(frame, variable=self.nombre_lignes, from_=2, to=LIGNES_MAX, command=self.changer_lignes, orient="horizontal").pack(side="left")
        tk.Label(frame, text=f"Nombre de colonnes :").pack(side="left", padx=20)
        tk.Scale(frame, variable=self.nombre_colonnes, from_=2, to=COLONNES_MAX, command=self.changer_colonnes, orient="horizontal").pack(side="left")

        tk.Button(frame, text="Confirmer", bg="lightblue", width=50, height=2, command=self.confirmer).pack(side="right", fill="both", padx=20)
        tk.Button(frame, text="Effacer", bg="lightblue", width=50, height=2, command=self.effacer_carte).pack(side="right", fill="both", padx=20)

        self.fenetre.mainloop()
    
    def creer_carte(self):
        self.taille_carreau = min(self.width//len(self.carte[0]), self.height//len(self.carte))
        self.carreaux = []
        self.canvas.delete("all")
        for i in range(len(self.carte)):
            self.carreaux.append([])
            for j in range(len(self.carte[i])):
                haut_gauche = (j*self.taille_carreau, i*self.taille_carreau)
                bas_droite = ((j+1)*self.taille_carreau, (i+1)*self.taille_carreau)
                rempli = COULEUR_SOL if self.carte[i][j] == "-" else COULEUR_MUR
                curr = self.canvas.create_rectangle(haut_gauche, bas_droite, fill=rempli, width=1)
                self.carreaux[i].append(curr)
                # self.canvas.tag_bind(curr, "<B1-Motion>", lambda event, id=curr, row=i, col=j : self.ajouter_mur(event, id, row, col))
                # self.canvas.tag_bind(curr, "<B3-Motion>", lambda event, id=curr, row=i, col=j : self.enlever_mur(event, id, row, col))
    
    def changer_lignes(self, val):
        while len(self.carte) > int(val):
            self.carte.pop(-1)
        while len(self.carte) < int(val):
            self.carte.append("-"*len(self.carte[0]))
        self.creer_carte()
    
    def changer_colonnes(self, val):
        while len(self.carte[0]) > int(val):
            self.carte = [ligne[:-1] for ligne in self.carte]
        while len(self.carte[0]) < int(val):
            self.carte = [ligne+"-" for ligne in self.carte]
        self.creer_carte()
    
    def ajouter_mur(self, event):
        id = self.canvas.find_closest(event.x, event.y, halo=None, start=None)
        row = event.y // self.taille_carreau
        col = event.x // self.taille_carreau
        if self.canvas.itemcget(id, "fill") == COULEUR_SOL:
            self.canvas.itemconfigure(id, fill=COULEUR_MUR)
            self.carte[row] = self.carte[row][:col]+"#"+self.carte[row][col+1:]

    def enlever_mur(self, event):
        id = self.canvas.find_closest(event.x, event.y, halo=None, start=None)
        row = event.y // self.taille_carreau
        col = event.x // self.taille_carreau
        if self.canvas.itemcget(id, "fill") == COULEUR_MUR:
            self.canvas.itemconfigure(id, fill=COULEUR_SOL)
            self.carte[row] = self.carte[row][:col]+"-"+self.carte[row][col+1:]
    
    def effacer_carte(self):
        self.carte = ["-"*len(row) for row in self.carte]
        self.creer_carte()
    
    def confirmer(self):
        with open(fichier, "w") as f:
            for row in self.carte:
                f.write(row)
                f.write("\n")
        self.fenetre.destroy()
        Fenetre(self.carte)

with open(fichier, "r") as f:
    carte = [line.strip() for line in f.readlines()]
Fenetre(carte)