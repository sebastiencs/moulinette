import sys
import os
from colorama import init, Fore

auteurs = []

class Norme(object):
    """Verifie la norme d'un fichier"""
    def __init__(self, nom_fichier):
        self.nom_fichier = nom_fichier
        self.f = 0
        self.lines = []
        self.nb_lignes = 0

    def reporter_erreur(self, msg, ligne):
        print (Fore.RED + "\tErreur: ", end = "")
        print (Fore.YELLOW + msg, end = "")
        print (Fore.RED + " ligne " + str(ligne), end = ""),
        print (Fore.RESET)

    def reporter_danger(self, msg, ligne):
        print (Fore.BLUE + "\tDanger: ", end = "")
        print (Fore.YELLOW + msg, end = "")
        print (Fore.BLUE + " ligne " + str(ligne), end = ""),
        print (Fore.RESET)

    def ajouter_auteur(self, nom):
        if nom not in auteurs:
            auteurs.append(nom)

    def inspecter_entete(self):
        if self.nb_lignes < 9:
            self.reporter_erreur("Entete manquante", 1)
            return -1
        if self.lines[0] != "/*\n":
            self.reporter_erreur("Entete manquante, ou pas a la 1ere ligne (ouais j'suis chiant)", 1)
            return -1
        for i in range(1, 8):
            if self.lines[i].startswith("**") == False:
                self.reporter_erreur("Entete: debut de ligne different de \"**\"", i)
        if self.lines[8] != "*/\n":
            self.reporter_erreur("Fin de l'entete bidon (\"*/\" attendu)", 9)
        if len(self.lines[1].split()) < 6:
            self.reporter_danger("Seconde ligne de l'entete pas conforme: \"FICHIER for PROJET in REPERTOIRE\" ", 2)
        else:
            if self.nom_fichier.endswith(self.lines[1].split()[1]) == False:
                self.reporter_danger("Nom de fichier dans l'entete different du vrai nom de fichier", 2)
            if "/home/" in self.lines[1].split()[5]:
                self.ajouter_auteur(self.lines[1].split()[5].split('/')[2])
        if len(self.lines[3].split()) < 4:
            self.reporter_danger("Quatrieme ligne de l'entete pas conforme: \"Made by TROU_DU_CUL\" ", 2)
        else:
            self.ajouter_auteur(self.lines[3].split()[3])
        if len(self.lines[4].split()) < 3:
            self.reporter_danger("Cinquieme ligne de l'entete pas conforme: \"Login TROU@DANS_TON_CUL\" ", 2)
        if len(self.lines[6].split()) < 9:
            self.reporter_danger("Septieme ligne de l'entete pas conforme: \"Started on [la suite]\" ", 2)
        else:
            self.ajouter_auteur(self.lines[6].split()[8])
        if len(self.lines[7].split()) < 9:
            self.reporter_danger("Huitieme ligne de l'entete pas conforme: \"Last [la suite]\" ", 2)
        else:
            self.ajouter_auteur(self.lines[7].split()[8])

    def inspecter_h(self):
        self.inspecter_entete()

    def inspecter_fichier(self):
        try:
            self.f = open(self.nom_fichier, "r")
        except:
            print ("Impossible d'ouvrir " + self.nom_fichier)

        for line in self.f:
            self.lines.append(line)
        self.nb_lignes = len(self.lines)

        if self.nom_fichier.endswith(".h"):
            print ("fichier: " + file)
            self.inspecter_h()
        else:
            pass

        self.f.close()

def get_list_files(dir_name):
    files = []
    for path, dirs, filenames in os.walk(dir_name):
        for file in filenames:
            if file.endswith(".h"): #or file.endswith(".c"):
                files.append(os.path.join(path, file))
    return files

if __name__ == '__main__':

    init()

    if len(sys.argv) <= 1:
        print ("Usage: ./" + sys.argv[0] + " __DIRECTORY__")
    else:
        files = get_list_files(sys.argv[1])
        for file in files:
            check = Norme(file)
            check.inspecter_fichier()
        print (auteurs)