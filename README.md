Moulinette faite sur un coup de tête et pour apprendre le pyton.
Parsing à base de split et readline, donc oui c'est tout sauf du parsing et c'est bien degueulasse

Ca vérifie l'alignement des noms de fonctions avec les variables mais dans certains cas (les mots clefs auxquels j'ai pas pense) ca ne marchera pas.

Si ca pète de fausses erreurs pour les alignements ou les 80 colonnes, il faut modifiee la variable ESPACES_PAR_TABULATIONS au debut du fichier.

VERSION: 0.107

##DEPENDENCES:
yum based distros:
```bash
- yum install python3-colorama
```
arch based distros:
```bash
yaourt -S python-colorama-git
```

##FAIT:

- Affiche les logins trouvés dans les fichiers (tu me dois 42 points)
- 80 colonnes max
- Une instruction par ligne
- 25 lignes par fonction
- 5 fonctions par fichier
- Seuls les inclusions de headers, les declarations, les defines, les prototypes et les macros sont autorises dans les fichiers headers.
- Macros multilignes
- Vérification du header
- Les protopypes et macros se trouvent uniquement dans les fichiers headers
- Commentaires dans le code
- Commentaires C++
- Alignement du nom de fonctions et des variables
- Noms de macros en majuscules
- Vérification des prefix pour les structures, unions, globales et types
- Vérification de la macro temoin dans le header

##POUR BIENTOT:

- Identifiants en minuscules, chiffres et _
- Saut de ligne entre les declarations de variables et les instructions
- Pas de ligne vide dans du code
- Declaration et affectation interdite sur la meme ligne
- Saut de ligne apres une structure de controle
- 4 parametres par fonctions
- Un espace apres la virgule
- Pas d'espace entre le nom de fonctions et la parenthese
- Espace entre mot clef et la parenthese ou le point virgule
- Pas d'espace apres un operateur unaire
- Operateurs binaires et ternaires separes par un espace de chaque cote
- indenter #if et #ifdef
- indenter macro imbrique
- saut de ligne entre chaque fonction
- mots clefs interdits: switch, for, goto, do while
- Verification du Makefile