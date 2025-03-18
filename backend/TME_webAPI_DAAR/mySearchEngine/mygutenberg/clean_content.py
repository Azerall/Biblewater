import re

def nettoyer_texte(texte):
    """ Sépare les métadonnées et le contenu du livre. """
    texte = texte.lstrip("\ufeff")  # Supprime le BOM (Byte Order Mark) s'il est présent

    metadata = ""
    texte_clean = texte  # Par défaut, tout le texte est considéré propre

    # Détection de la ligne `*** START ... ***`
    match = re.search(r"(?m)^.*\*\*\* START .*? \*\*\*.*$", texte)
    if match:
        metadata = texte[:match.start()].strip()  # Stocke les infos avant `START`
        texte_clean = texte[match.end():]  # Garde uniquement le texte après cette ligne

    # Détection de la ligne `*** END ... ***`
    match_end = re.search(r"(?m)^.*\*\*\* END .*? \*\*\*.*$", texte_clean)
    if match_end:
        texte_clean = texte_clean[:match_end.start()]  # Coupe avant `END`

    return metadata, texte_clean.strip()  # Retourne les métadonnées et le texte nettoyé
