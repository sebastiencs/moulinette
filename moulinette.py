#!/usr/bin/env python3
import sys
import os
import platform
import subprocess
from colorama import init, Fore

VERSION = 0.111
ESPACES_PAR_TABULATION = 8
FLAGS_CLANG = "-Wall -Wextra -pedantic"

auteurs = []


class Norme(object):
    """Verifie la norme d'un fichier"""
    def __init__(self, nom_fichier):
        self.nom_fichier = nom_fichier
        self.f = 0
        self.lines = []
        self.nb_lignes = 0
        self.erreurs = []
        self.dangers = []
        self.nom_afficher = 0

    def reporter_erreur(self, msg, ligne):
        self.erreurs.append(Fore.RED + "\tErreur: " + Fore.YELLOW
                            + msg + Fore.RED + " ligne " + str(ligne)
                            + Fore.RESET)
        # print (self.nom_fichier)
        # print (Fore.RED + msg + " line " + str(ligne) + Fore.RESET)
        return -1

    def reporter_danger(self, msg, ligne):
        self.dangers.append(Fore.YELLOW + "\tDanger: "
                            + msg + " ligne " + str(ligne)
                            + Fore.RESET)
        # print (self.nom_fichier)
        # print (Fore.YELLOW + msg + " line " + str(ligne) + Fore.RESET)
        return -1

    def afficher_erreurs(self):
        if self.nom_afficher == 0 and len(self.erreurs) > 0:
            print (Fore.CYAN + self.nom_fichier)
            self.nom_afficher = 1
        for erreur in self.erreurs:
            print (erreur)

    def afficher_dangers(self):
        if self.nom_afficher == 0 and len(self.dangers) > 0:
            print (Fore.CYAN + self.nom_fichier)
            self.nom_afficher = 1
        for danger in self.dangers:
            print (danger)

    def nombres_erreurs_et_dangers(self):
        return len(self.erreurs) + len(self.dangers)

    def ajouter_auteur(self, nom):
        if nom not in auteurs:
            auteurs.append(nom)

    def inspecter_nombre_colonnes(self):
        for index, line in enumerate(self.lines):
            size = len(line.expandtabs(ESPACES_PAR_TABULATION))
            if size > 80:
                self.reporter_erreur("Ligne de " + str(size) + " colonnes",
                                     index + 1)

    def inspecter_nombre_instruction(self):
        chaines = False
        for index, line in enumerate(self.lines):
            strtab = line.split()
            if line.count(';') > 1 and strtab[0] != "for":
                n_inst = 0
                for c in line:
                    if c == '"':
                        chaines = not chaines
                    if c == ';' and chaines is False:
                        n_inst += 1
                if n_inst > 1:
                    self.reporter_erreur("Nombres d'instructions > 1",
                                         index + 1)

    def inspecter_entete(self):
        if self.nb_lignes < 9:
            return self.reporter_erreur("Entête manquante", 1)
        if self.lines[0] != "/*\n":
            return self.reporter_erreur("Entête manquante, ou n'étant pas à la 1ère \
ligne", 1)
        for i in range(1, 8):
            if self.lines[i].startswith("**") is False:
                self.reporter_erreur("Entête: début de ligne different de \
\"**\"", i)
        if self.lines[8] != "*/\n":
            self.reporter_erreur("Fin de l'entête bidon (\"*/\" attendu)", 9)
        if len(self.lines[1].split()) < 6:
            self.reporter_danger("Seconde ligne de l'entête non-conforme: \
\"FICHIER for PROJET in REPERTOIRE\" ", 2)
        else:
            if self.nom_fichier.endswith(self.lines[1].split()[1]) is False:
                self.reporter_danger("Nom de fichier dans l'entête different \
du vrai nom de fichier", 2)
            if "/home/" in self.lines[1].split()[5]:
                self.ajouter_auteur(self.lines[1].split()[5].split('/')[2])
        if len(self.lines[3].split()) < 4:
            self.reporter_danger("Quatrieme ligne de l'entête non-conforme: \
\"Made by TROU_DU_CUL\" ", 2)
        else:
            self.ajouter_auteur(self.lines[3].split()[3])
        if len(self.lines[4].split()) < 3:
            self.reporter_danger("Cinquieme ligne de l'entête non-conforme: \
\"Login TROU@DANS_TON_CUL\" ", 2)
        if len(self.lines[6].split()) < 9:
            self.reporter_danger("Septieme ligne de l'entête non-conforme: \
\"Started on [la suite]\" ", 2)
        else:
            self.ajouter_auteur(self.lines[6].split()[8])
        if len(self.lines[7].split()) < 9:
            self.reporter_danger("Huitieme ligne de l'entête pas conforme: \
\"Last [la suite]\" ", 2)
        else:
            self.ajouter_auteur(self.lines[7].split()[8])

    def inspecter_macro_temoin(self):
        i = 0
        if platform.system() == "Windows":
            macro_attendue = self.nom_fichier.upper().split('\\')[-1].split('.')[0] + "_H_"
        else:
            macro_attendue = self.nom_fichier.upper().split('/')[-1].split('.')[0] + "_H_"
        macro_temoin = []
        while (i < len(self.lines)
               and self.lines[i].startswith("#ifndef ") is False):
            i += 1
        if i == len(self.lines) or len(self.lines[i].split()) < 2:
            return self.reporter_erreur("Pas de macro témoin", i + 1)
        macro_temoin = self.lines[i].split()[1]
        if macro_temoin != macro_attendue:
            return self.reporter_erreur("Macro témoin differente de celle \
attendue (" + macro_attendue + ")", i + 1)
        if (self.lines[i + 1].startswith("# define") is False or
           len(self.lines[i + 1].split()) < 3):
            return self.reporter_erreur("#ifndef doit etre suivi \
de \"# define \" sur la ligne suivante", i + 2)
        if self.lines[i + 1].split()[2] != macro_temoin:
            return self.reporter_erreur("Deux macros témoins différentes",
                                        i + 2)
        while (i < len(self.lines)
               and self.lines[i].startswith("#endif /* !" +
                                            macro_temoin + " */") is False):
            i += 1
        if i == len(self.lines):
            return self.reporter_erreur("Pas de #endif pour la macro témoin, \
ou mal formate: \"#endif /* !MACRO /*\"", i + 1)

    def recuperer_fin_fonction(self, index_debut):
        for index, line in enumerate(self.lines):
            if index > index_debut and line[0] == '}':
                return index
        return 0

    def inspecter_nombre_ligne_par_fonction(self):
        for index, line in enumerate(self.lines):
            if (index > 0 and line[0] == '{' and
               self.lines[index - 1].split()[-1] != '='):
                fin_fonction = self.recuperer_fin_fonction(index)
                nb_lignes = fin_fonction - index - 1
                if nb_lignes > 25:
                    self.reporter_erreur("Fonction de " + str(nb_lignes)
                                         + " lignes", index + 1)

    def inspecter_nombre_fonctions(self):
        nb_fonctions = 0
        keyword = ["typedef", "enum", "struct", "union"]
        for index, line in enumerate(self.lines):
            if (index > 0 and line[0] == '{'
                and self.lines[index - 1].split()[-1] != '=' and
                    self.lines[index - 1].split()[0] not in keyword):
                nb_fonctions += 1
        if nb_fonctions > 5:
            self.reporter_erreur(str(nb_fonctions)
                                 + " fonctions dans le fichier", 1)

    def inspecter_macro_multilignes(self):
        for index, line in enumerate(self.lines):
            strtab = line.split()
            if (len(strtab) > 0 and strtab[0] == '#'
               and strtab[1].upper() == "define" and strtab[-1] == '\\'):
                self.reporter_erreur("Macro multilignes", index + 1)

    def inspecter_fonctions_dans_header(self):
        keyword = ["return", "while", "for", "if"]
        for index, line in enumerate(self.lines):
            for key in keyword:
                if key in line.split() and line.startswith("**") is False:
                    self.reporter_danger("Il semble y avoir du code dans \
un fichier header: utilisation du mot clef " + key,
                                         index + 1)
                if ('(' in line and ')' in line
                    and 'DEFINE' not in line.upper() and
                        ';' not in line):
                    if index == 0:
                        self.reporter_danger("Il semble y avoir du code \
dans un fichier header", index + 1)
                    elif (len(self.lines[index - 1]) > 0 and
                          len(self.lines[index - 1].split()) > 0 and
                          self.lines[index - 1].split()[-1] != '\\'):
                        self.reporter_danger("Il semble y avoir du code \
dans un fichier header", index + 1)

    def inspecter_macro_dans_code(self):
        for index, line in enumerate(self.lines):
            strtab = line.split()
            if ((len(strtab) > 1 and strtab[0] == '#'
                 and strtab[1].upper() == 'DEFINE') or
                    (len(strtab) > 0 and strtab[0].upper() == "#DEFINE")):
                self.reporter_erreur("Présence de macros dans un fichier .c",
                                     index + 1)

    def mot_clef_dans_ligne(self, ligne):
        keyword = ["return", "while", "for", "if", "+", "-", "%"]
        strtab = ligne.split()
        for key in keyword:
            if key in strtab:
                return 1
        return 0

    def inspecter_prototype_dans_code(self):
        """ Gère pas le multiligne """
        for index, line in enumerate(self.lines):
            strtab = line.split()
            if ('=' not in line and '(' in line and ')' in line and ';' in line
                and len(strtab) > 1 and '(' in strtab[1]
                and self.mot_clef_dans_ligne(line) == 0 and
                    '(' not in strtab[0]):
                i = 0
                if line[line.index('(') + 1] == ')':
                    self.reporter_erreur("Prototype dans un fichier .c",
                                         index + 1)
                else:
                    for c in line[line.index('('):line.index(')')]:
                        if c == ' ' and i != 0:
                            self.reporter_erreur("Prototype dans \
                            un fichier .c", index + 1)
                        if c == ',':
                            i = 0
                        else:
                            i += 1

    def dans_une_chaine(self, line, index):
        chaine = False
        for i, c in enumerate(line):
            if c == '"':
                chaine = not chaine
            if i == index and chaine is True:
                return True
        return False

    def inspecter_mots_clefs_interdits(self):
        for index, line in enumerate(self.lines):
            if (len(line.split()) > 1 and
                ((line.split()[0] == "do"
                  and line.split()[1].startswith("(")) or
                (line.split()[0] == "switch"
                 and line.split()[1].startswith("(")) or
                (line.split()[0] == "for"
                 and line.split()[1].startswith("(")) or
                (line.split()[0] == "goto"
                 and line.split()[1].startswith("(")))):
                self.reporter_erreur("Mot clef interdit: " + line.split()[0],
                                     index + 1)

    def inspecter_espace_apres_mot_clef(self):
        for index, line in enumerate(self.lines):
            if (len(line.split()) > 0 and
                (line.split()[0].startswith("if(") is True or
                 line.split()[0].startswith("else(") is True or
                 line.split()[0].startswith("return(") is True or
                 line.split()[0].startswith("return;") is True or
                 line.split()[0].startswith("while(") is True or
                 line.split()[0].startswith("for(") is True or
                 line.split()[0].startswith("do(") is True or
                 line.split()[0].startswith("switch(") is True)):
                self.reporter_erreur("Il manque un espace apres le mot clef '"
                                     + line.split()[0] + "'", index + 1)
            elif (len(line.split()) > 1 and
                  line.split()[0] == "else" and
                  line.split()[1].startswith("if(")):
                self.reporter_erreur("Il manque un espace apres le mot clef '"
                                     + "else if'", index + 1)

    def inspecter_commentaire_cpp(self):
        for index, line in enumerate(self.lines):
            found = line.find("//")
            if found >= 0 and self.dans_une_chaine(line, found) is False:
                self.reporter_erreur("Commentaire CPP", index + 1)

    def dans_une_fonction(self, index):
        fonction = False
        for i, line in enumerate(self.lines):
            if len(line) > 0 and line[0] == '{':
                fonction = True
            if len(line) > 0 and line[0] == '}':
                fonction = False
            if i == index and fonction is True:
                return True
        return False

    def inspecter_commentaire_dans_fonction(self):
        for index, line in enumerate(self.lines):
            found = line.find("/*")
            if found >= 0 and self.dans_une_chaine(line, found) is False:
                if self.dans_une_fonction(index) is True:
                    self.reporter_erreur("Commentaire dans du code", index + 1)

    def get_alignement_apres_type(self, line, debut):
        line = line.expandtabs(ESPACES_PAR_TABULATION)
        while debut < len(line) and line[debut] == ' ':
            debut += 1
        return debut + 1

    def is_variable_declaration(self, index):
        strtab = self.lines[index].split()
        if len(strtab) > 0 and '#' not in strtab[0]:
            if len(strtab) > 0 and strtab[0] == "static":
                return True
            elif len(strtab) == 2 and '(' not in self.lines[index]:
                return True
            elif (len(strtab) == 3 and '(' not in self.lines[index] and
                  strtab[0] == "unsigned"):
                return True
        return False

    def pass_type(self, line, index):
        i = 0
        while i < len(line) and (line[i] == ' ' or line[i] == '\t'):
            i += 1
        if line.find("static "          , i, i + 7 ) != -1:      i += 7
        if line.find("const "           , i, i + 6 ) != -1:      i += 6
        if line.find("unsigned "        , i, i + 9 ) != -1:      i += 9
        if line.find("signed "          , i, i + 7 ) != -1:      i += 7
        if line.find("long long"        , i, i + 9 ) != -1:      i += 9
        if line.find("inline"           , i, i + 6 ) != -1:      i += 6
        if line.find("__attribute__"    , i, i + 13) != -1:      i += 13
        if line.find("((always_inline))", i, i + 17) != -1:      i += 17
        while i < len(line) and line[i].isalnum() is True or line[i] == '_':
            i += 1
        debut = i
        while i < len(line) and (line[i] == ' ' or line[i] == '\t'):
            if line[i] == ' ':
                self.reporter_erreur("Utilisation d'espace entre le type \
et le nom de la variable/fonction", index + 1)
                return -1
            i += 1
        return debut

    def get_alignement_variable(self, line, index):
        debut = self.pass_type(line, index)
        if debut == -1:
            return -1
        alignement_variable = self.get_alignement_apres_type(line, debut)
        return alignement_variable

    def get_alignement_nom_variable(self, index):
        alignements = []
        while index < len(self.lines) and self.lines[index][0] != '{':
            index += 1
        index += 1
        while self.is_variable_declaration(index) is True:
            align_variable = self.get_alignement_variable(self.lines[index],
                                                          index)
            if align_variable == -1:
                return [-1]
            alignements.append(align_variable)
            index += 1
#        print (alignements)
        return alignements

    def debut_de_fonction(self, line, index):
        if (index < len(self.lines) - 1 and len(self.lines[index + 1]) > 0
           and self.lines[index][0] != ' ' and self.lines[index][0] != '\t'
           and (self.lines[index + 1][0] == '{'
                or ((index < len(self.lines) - 2
                     and self.lines[index + 2][0] == '{'))
                or ((index < len(self.lines) - 3
                     and self.lines[index + 3][0] == '{'))
                or ((index < len(self.lines) - 4
                     and self.lines[index + 4][0] == '{')))
           and len(self.lines[index]) > 0 and self.lines[index][0] != '}'
           and self.lines[index][0] != '\n'
           and '#' not in line
           and "extern" not in line
           and line.startswith("**") is False
           and line.startswith("*/") is False
           and line.startswith("/*") is False
           and line.find('(') >= 0
           and '=' not in line):
            return True
        return False

    def inspecter_alignement(self):
        for index, line in enumerate(self.lines):
            if self.debut_de_fonction(line, index) is True:
                debut = self.pass_type(line, index)
                align_nom_fonction = self.get_alignement_apres_type(line,
                                                                    debut)
                align_nom_variable = self.get_alignement_nom_variable(index)
                if (len(align_nom_variable) > 0 and
                   align_nom_fonction != -1):
                    for var in align_nom_variable:
                        if align_nom_fonction != var and var != -1:
                            return self.reporter_erreur("Mauvais alignements \
de la fonction avec les variables", index + 1)

    def inspecter_macro_majuscule(self):
        for index, line in enumerate(self.lines):
            if len(line) > 0:
                strtab = line.split("(")[0].split()
                if (len(strtab) > 1 and strtab[0].upper() == "#DEFINE" and
                   strtab[1].upper() != strtab[1]):
                    self.reporter_erreur("La macro doit être en majuscule",
                                         index + 1)
                elif (len(strtab) > 2 and strtab[0] == '#' and
                      strtab[1].upper() == "DEFINE"
                      and strtab[2].upper() != strtab[2]):
                    self.reporter_erreur("La macro doit être en majuscule",
                                         index + 1)

    def inspecter_typedef(self):
        for index, line in enumerate(self.lines):
            strtab = line.split()
            if len(strtab) > 0 and strtab[0] == "typedef":
                if len(strtab) > 2:
                    if (strtab[1] == "struct" and
                       strtab[2].startswith("s_") is False):
                        self.reporter_erreur("Le nom de structure doit \
commencer par \"s_\"", index + 1)
                    elif (strtab[1] == "union" and
                          strtab[2].startswith("u_") is False):
                        self.reporter_erreur("Le nom d'union doit commencer \
par \"u_\"", index + 1)
                    if ';' in line and strtab[-1].startswith("t_") is False:
                        self.reporter_erreur("Le nom d'un type doit commencer \
par \"t_\"", index + 1)
                    elif ';' not in line:
                        i = index
                        while i < len(self.lines) and self.lines[i][0] != '}':
                            i += 1
                        if i != len(self.lines):
                            strtab2 = self.lines[i].split()
                            if (len(strtab2[-1]) > 0 and
                               strtab2[-1].startswith("t_") is False):
                                self.reporter_erreur("Le nom d'un type doit \
commencer par \"t_\"", index + 1)

    def inspecter_global(self):
        for index, line in enumerate(self.lines):
            strtab = line.split()
            if (len(strtab) > 1 and self.dans_une_fonction(index) is False
               and line.startswith("**") is False
               and line.startswith("/*") is False
               and line.startswith("*/") is False and '#' not in line
               and '(' not in line and ')' not in line):
                if (len(strtab) > 3 and strtab[-1] == '{' and strtab[-2] == '='
                   and strtab[-3].startswith("g_") is False):
                    self.reporter_erreur("1Une globale doit commencer \"g_\"",
                                         index + 1)
                elif (len(strtab) > 2 and strtab[-1] == '='
                      and strtab[-2].startswith("g_") is False):
                    self.reporter_erreur("2Une globale doit commencer \"g_\"",
                                         index + 1)
                elif (strtab[1].startswith("g_") is False
                      and strtab[1][-1] == ';' and strtab[0] != '}'):
                    self.reporter_erreur("3Une globale doit commencer \"g_\"",
                                         index + 1)

    def inspecter_h(self):
        self.inspecter_macro_temoin()
        self.inspecter_fonctions_dans_header()

    def inspecter_c(self):
        self.inspecter_macro_dans_code()
        self.inspecter_prototype_dans_code()
        self.inspecter_alignement()

    def inspecter_fichier(self):
        try:
            self.f = open(self.nom_fichier, "r")
        except:
            print ("Impossible d'ouvrir " + self.nom_fichier)
            return -1

        for line in self.f:
            self.lines.append(line)
        self.f.close()
        self.nb_lignes = len(self.lines)

#        print (file)
        if self.nom_fichier.endswith(".h"):
            self.inspecter_h()
        else:
            self.inspecter_c()
        self.inspecter_entete()
        self.inspecter_nombre_colonnes()
        self.inspecter_nombre_instruction()
        self.inspecter_nombre_ligne_par_fonction()
        self.inspecter_nombre_fonctions()
        self.inspecter_macro_multilignes()
        self.inspecter_commentaire_cpp()
        self.inspecter_commentaire_dans_fonction()
        self.inspecter_macro_majuscule()
        self.inspecter_typedef()
        self.inspecter_global()
        self.inspecter_mots_clefs_interdits()
        self.inspecter_espace_apres_mot_clef()


def get_list_files(dir_name):
    files = []
    for path, dirs, filenames in os.walk(dir_name):
        for file in filenames:
            if file.endswith(".h") or file.endswith(".c"):
                files.append(os.path.join(path, file))
    return files


def get_list_makefile(dir_name):
    files = []
    for path, dirs, filenames in os.walk(dir_name):
        for file in filenames:
            if file == "Makefile":
                files.append(os.path.join(path, file))
    return files


def afficher_erreur(nb):
    if nb == 0:
        print (Fore.GREEN
               + "Aucune erreur trouvée."
               + Fore.RESET)
    else:
        print("")
        print (Fore.YELLOW
               + str(nb)
               + " Erreurs et warnings trouvés."
               + Fore.RESET)


def afficher_logins():
    user = os.getenv("USER")
    if len(auteurs) > 0:
        print ("Logins trouvés: ", end="")
        for auteur in auteurs:
            if auteur == user:
                print (Fore.GREEN + auteur, end=" ")
            else:
                print (Fore.YELLOW + auteur, end=" ")
        print (Fore.RESET)
    else:
        print ("Aucun login trouvé")


def options_presentes(argv):
    if "--help" in argv:
        return True
    return False


def aide(argv):
    if options_presentes(argv) is False or "--help" in argv:
        print ("Usage: " + sys.argv[0] + " <répertoire>\n")
        print ("Options:")
        print ("\t--ici\t\t:Analyse le dossier courant.")
        print ("\t--help\t\t:Affiche cette aide.")
        print ("\nVERSION: " + str(VERSION))


def verifier_makefile(makefile):
    all, clean, fclean, re, name = 0, 0, 0, 0, 0
    wildcard, ligne_wildcard = 0, 0
    make = open(makefile, "r")
    for i, line in enumerate(make):
        if len(line) > 0 and line.startswith("all:"):
            all = 1
        if len(line) > 0 and line.startswith("clean:"):
            clean = 1
        if len(line) > 0 and line.startswith("fclean:"):
            fclean = 1
        if len(line) > 0 and line.startswith("re:"):
            re = 1
        if len(line) > 0 and line.startswith("$(NAME):"):
            name = 1
        if "*" in line:
            wildcard = 1
            ligne_wildcard = i
    if not all or not clean or not fclean or not re or not name:
        print (Fore.CYAN + makefile + ":" + Fore.RED)
    if not all:
        print ("\til manque la regle 'all'")
    if not clean:
        print ("\til manque la regle 'clean'")
    if not fclean:
        print ("\til manque la regle 'fclean'")
    if not re:
        print ("\til manque la regle 're'")
    if not name:
        print ("\til manque la regle '$(NAME)'")
    if wildcard:
        print ("\tWildcard interdit ligne " + str(ligne_wildcard))
    print (Fore.RESET, end="")


def afficher_erreurs_clang(file, files):
    headers = []
    includes = ""
    for f in files:
        if f.endswith('.h') and os.path.dirname(f) not in headers:
            headers.append(os.path.dirname(f))
    includes = " ".join(headers)
    src = []
    sources = ""
    for f in files:
        if f.endswith('.c') and f not in src:
            src.append(f)
    sources = " ".join(src)
    cmd = ("clang -fsyntax-only " + FLAGS_CLANG + " -I " + includes
           + " " + sources)
    print ("\n\nClang:")
    os.popen(cmd).read()
    print ("")
    # out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
    #                        stderr=subprocess.PIPE)#.stderr.read()
    # normal, erreur = out.communicate()
    # print (erreur)


if __name__ == '__main__':
    if len(sys.argv) <= 1 or options_presentes(sys.argv) is True:
        aide(sys.argv)
    else:
        if platform.system() == "Windows":
            init()
        if "--ici" in sys.argv:
            dossier = "."
        else:
            dossier = sys.argv[1]
        makefiles = get_list_makefile(dossier)
        for makefile in makefiles:
            verifier_makefile(makefile)
        files = get_list_files(dossier)
        nb_erreurs = 0
        for file in files:
            check = Norme(file)
            check.inspecter_fichier()
            check.afficher_dangers()
            check.afficher_erreurs()
            nb_erreurs += check.nombres_erreurs_et_dangers()
        # afficher_erreurs_clang(file, files)
        afficher_erreur(nb_erreurs)
        afficher_logins()
