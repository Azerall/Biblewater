def compute_lps_array(pattern):
    length = 0  # Longueur du préfixe/suffixe précédent
    lps = [0] * len(pattern)  # Tableau LPS
    i = 1

    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text, pattern):
    if not pattern or not text:
        return []

    M = len(pattern)
    N = len(text)
    lps = compute_lps_array(pattern)

    occurrences = []
    i = 0  # Index dans le texte
    j = 0  # Index dans le motif

    while i < N:
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == M:
            occurrences.append(i - j)  # Motif trouvé
            j = lps[j - 1]  # Revenir en arrière dans le motif
        elif i < N and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return occurrences
