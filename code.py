import random
import os
import sys

class tajibnapis:

    compteur = 0                # Compteur des messages 

    def __init__(self, nom):
        self.nom = nom
        self.Voisins = []	# Voisins de u
        self.Distance = {}	# Distance de u vers v
        self.Nb = {}		# Le voisin prÃ©fÃ©rÃ© avec le chemin le plus court de u vers v
        self.Ndis = {}		# Distance de chaque noeud vers un autre
        self.Queue = {}		# Queue des messages
        self.Noeuds = []	# Ensemble de tous les noeuds
        self.N = 0		# Ensemble des noeuds 

    def __repr__(self):
        return self.nom

    def informations(self):
        print("Voisins de %s:      " % self, self.Voisins)
        print("Distance de %s vers:" % self, self.Distance)
        print("Nb de %s:           " % self, self.Nb)
        print("Ndis de %s:         " % self, end="")
        for i, j in enumerate(self.Ndis.keys()):
            if i == 0:
                print("  %s:" % j, self.Ndis[j])
            else:
                print(" "*20 ,"%s:" % j, self.Ndis[j])
        print("Queues de %s:        " % self, end="")
        for i, j in enumerate(self.Queue.keys()):
            if i == 0:
                print(" %s:" % j, self.Queue[j])
            else:
                print(" "*20 ,"%s:" % j, self.Queue[j])

    def creation(self, Voisins, Noeuds):
        self.Voisins = Voisins
        self.Noeuds = Noeuds
        self.N = len(Noeuds)
        for w in self.Voisins:
            self.Queue[repr(w)] = []

    def initialisation(self):
        for w in self.Voisins:
            self.Ndis[repr(w)] = {}
            for v in self.Noeuds:
                self.Ndis[repr(w)][repr(v)] = self.N

        for v in self.Noeuds:
            if v == self:
                self.Distance[repr(v)] = 0
                self.Nb[repr(v)] = "Local"
            else:
                self.Distance[repr(v)] = self.N
                self.Nb[repr(v)] = "Ndef"

        for w in self.Voisins:
            message = {"type_msg": "mydist", "contenu":[self, 0]}
            self.envoi_message(message, w)

    def recompute(self, v):
        Distance0 = self.Distance[repr(v)]
        if v == self:
            self.Distance[repr(v)] = 0
            self.Nb[repr(v)] = "Local"
        else:
            w = min(self.Voisins, key=lambda w: self.Ndis[repr(w)][repr(v)])
            d = 1 + self.Ndis[repr(w)][repr(v)]
            if d < self.N:
                self.Distance[repr(v)] = d
                self.Nb[repr(v)] = w
            else:
                self.Distance[repr(v)] = self.N
                self.Nb[repr(v)] = "Ndef"
        if self.Distance[repr(v)] != Distance0:
            for x in self.Voisins:
                message = {"type_msg": "mydist", "contenu":[v, self.Distance[repr(v)]]}
                self.envoi_message(message, x)

    def verifier_queue(self):
        for w in self.Voisins:
            if len(self.Queue[repr(w)]) > 0:
                return False
        return True

    def choisir_queue(self):
        lst = [w for w in self.Voisins if len(self.Queue[repr(w)]) > 0]
        if len(lst) == 0:
            return None
        return random.choice(lst)

    def reception(self):
        tajibnapis.compteur += 1
        w = self.choisir_queue()
        if w == None:
            print("%03d    Noeud: %s, pas de messages disponibles dans la Queue_%s"
                  % (tajibnapis.compteur, self, self))
            return
        message = self.Queue[repr(w)].pop(0)
        if message["type_msg"] == "mydist":
            v = message["contenu"][0]
            d = message["contenu"][1]
            self.Ndis[repr(w)][repr(v)] = d
            print("%03d    Noeud: %s, a reÃ§u <mydist,%s,%d> de %s"
                  % (tajibnapis.compteur, self, v, d, w))
            self.recompute(v)
        elif message["type_msg"] == "fail":
            v = message["contenu"]
            self.Voisins.remove(v)
            print("\n\n%03d    Noeud: %s, %s a Ã©tÃ© supprimÃ© des voisins parce que %s a reÃ§u un message fail\n\n" % (tajibnapis.compteur, self, v, self))
            del self.Queue[repr(v)]
            for i in (Noeuds):
                del self.Ndis[repr(v)][repr(i)]
            self.Nb[repr(v)] = "Ndef"
            self.Distance[repr(v)] = self.N
            self.informations()

            for x in self.Voisins:
                message = {"type_msg": "mydist", "contenu":[self, 0]}
                self.envoi_message(message, x)
                self.recompute(x)
        else:
            v = message["contenu"]
            self.Voisins.append(v)
            self.Queue[repr(v)] = []
            for x in self.Voisins:
                self.Ndis[repr(v)][(x)] = self.N
                msg = {"type_msg": "mydist", "contenu":[v, self.Distance[repr(v)]]}
                self.envoi_message(msg, x)

    def envoi_message(self, message, receveur):
        receveur.stockage_message(message, self)

    def stockage_message(self, message, identite):
        self.Queue[repr(identite)].append(message)

if __name__ == '__main__':

    input_file = sys.argv[1]
    with open(input_file) as file:
         content = file.readlines()
         content = [x.strip() for x in content]
         num_nodes = int(content[0])

    lst0 = []
    for i in range(num_nodes):
        string = content[i+1]
        stg0 = string.split(":")[0]
        lst0.append(stg0)

    A = tajibnapis(lst0[0])
    B = tajibnapis(lst0[1])
    C = tajibnapis(lst0[2])
    D = tajibnapis(lst0[3])

    Noeuds = [A, B, C, D]

    A.creation([B],       Noeuds)
    B.creation([A, C, D], Noeuds)
    C.creation([B, D],    Noeuds)
    D.creation([B, C],    Noeuds)

    for u in Noeuds:
        u.initialisation()

    print("\n\n------------- Etat initial -------------\n\n")
    for u in Noeuds:
        print("############# Table du noeud %s" % u, "#############")
        u.informations()
        print("\n\n")

    while not all([u.verifier_queue() for u in Noeuds]):
         u = random.choice([v for v in Noeuds if not v.verifier_queue()])
         u.reception()
    print("\n\n")

    print("------------- Etat aprÃ¨s l'échange des messages -------------\n\n")
    for u in Noeuds:
        print("############# Table du noeud %s" % u, "#############")
        print("Noeud:", u)
        u.informations()
        print("\n\n")

    print("------------- Etat après le fail -------------\n")

    input = open("graphe.txt", "r")
    lines = input.readlines()
    lines[1] = "A:\n"
    lines[2] = "B:C,D\n"
    input = open("graphe.txt", "w")
    input.writelines(lines)
    input.close()

    msg0 = {"type_msg": "fail", "contenu": A}
    A.envoi_message(msg0, B)

    msg1 = {"type_msg": "fail", "contenu": B}
    B.envoi_message(msg1, A)

#    for u in Noeuds:
#        print("############# Table du noeud %s" % u, "#############")
#        print("Noeud:", u)
#        u.informations()
#        print("\n\n")

    while not all([u.verifier_queue() for u in Noeuds]):
        u = random.choice([v for v in Noeuds if not v.verifier_queue()])
        u.reception()

    print("\n")
