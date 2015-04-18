import sys
import os
import platform
from colorama import init, Fore

ESPACES_PAR_TABULATION = 4

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
        return -1

    def reporter_danger(self, msg, ligne):
        print (Fore.YELLOW + "\tDanger: ", end = "")
        print (Fore.YELLOW + msg, end = "")
        print (Fore.YELLOW + " ligne " + str(ligne), end = ""),
        print (Fore.RESET)
        return -1

    def ajouter_auteur(self, nom):
        if nom not in auteurs:
            auteurs.append(nom)

    def inspecter_nombre_colonnes(self):
        for index, line in enumerate(self.lines):
            if len(line.expandtabs(ESPACES_PAR_TABULATION)) > 80:
                self.reporter_erreur("Nombre de colonnes > 80", index + 1)

    def inspecter_nombre_instruction(self):
        chaines = False
        for index, line in enumerate(self.lines):
            strtab = line.split()
            if line.count(';') > 1 and strtab[0] != "for":
                n_inst = 0
                for c in line:
                    if c == '"':
                        chaines = not chaines
                    if c == ';' and chaines == False:
                        n_inst += 1
                if n_inst > 1:
                    self.reporter_erreur("Nombres d'instructions > 1", index + 1)

    def inspecter_entete(self):
        if self.nb_lignes < 9:
            return self.reporter_erreur("Entete manquante", 1)
        if self.lines[0] != "/*\n":
            return self.reporter_erreur("Entete manquante, ou pas a la 1ere ligne (ouais j'suis chiant)", 1)
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

    def inspecter_macro_temoin(self):
        i = 0
        if platform.system() == "Windows":
            macro_attendue = self.nom_fichier.upper().split('\\')[-1].split('.')[0] + "_H_"
        else:
            macro_attendue = self.nom_fichier.upper().split('/')[-1].split('.')[0] + "_H_"
        macro_temoin = []
        while i < len(self.lines) and self.lines[i].startswith("#ifndef ") == False:
            i += 1
        if i == len(self.lines) or len(self.lines[i].split()) < 2:
            return self.reporter_erreur("Pas de macro temoin", i + 1)
        macro_temoin = self.lines[i].split()[1]
        if macro_temoin != macro_attendue:
            return self.reporter_erreur("Macro temoin differente de celle attendue (" + macro_attendue + ")", i + 1)
        if self.lines[i + 1].startswith("# define") == False or len(self.lines[i + 1].split()) < 3:
            return self.reporter_erreur("#ifndef doit etre suivi de \"# define \" sur la ligne suivante", i + 2)
        if self.lines[i + 1].split()[2] != macro_temoin:
            return self.reporter_erreur("Deux macros temoins differentes", i + 2)
        while i < len(self.lines) and self.lines[i].startswith("#endif /* !" + macro_temoin + " */") == False:
            i += 1
        if i == len(self.lines):
            return self.reporter_erreur("Pas de #endif pour la macro temoin, ou mal formate: \"#endif /* !MACRO /*\"", i + 1)

    def recuperer_fin_fonction(self, index_debut):
        for index, line in enumerate(self.lines):
            if index > index_debut and line[0] == '}':
                return index
        return 0

    def inspecter_nombre_ligne_par_fonction(self):
        for index, line in enumerate(self.lines):
            if (index > 0 and line[0] == '{' and self.lines[index - 1].split()[-1] != '='):
                fin_fonction = self.recuperer_fin_fonction(index)
                nb_lignes = fin_fonction - index - 1
                if nb_lignes > 25:
                    self.reporter_erreur("Fonction de " + str(nb_lignes) + " lignes", index + 1)

    def inspecter_h(self):
        self.inspecter_entete()
        self.inspecter_macro_temoin()

    def inspecter_fichier(self):
        try:
            self.f = open(self.nom_fichier, "r")
        except:
            print ("Impossible d'ouvrir " + self.nom_fichier)

        for line in self.f:
            self.lines.append(line)
        self.f.close()
        self.nb_lignes = len(self.lines)

        print ("fichier: " + file)
        if self.nom_fichier.endswith(".h"):
            self.inspecter_h()
        self.inspecter_nombre_colonnes()
        self.inspecter_nombre_instruction()
        self.inspecter_nombre_ligne_par_fonction()

def get_list_files(dir_name):
    files = []
    for path, dirs, filenames in os.walk(dir_name):
        for file in filenames:
            if file.endswith(".h") or file.endswith(".c"):
                files.append(os.path.join(path, file))
    return files

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print ("Usage: ./" + sys.argv[0] + " __DIRECTORY__")
    else:
        if platform.system() == "Windows":
            init()
        files = get_list_files(sys.argv[1])
        for file in files:
            check = Norme(file)
            check.inspecter_fichier()
        print ("\nauteurs: " + " ".join(auteurs))