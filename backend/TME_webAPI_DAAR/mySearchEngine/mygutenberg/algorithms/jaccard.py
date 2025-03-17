from collections import defaultdict

def compute_jaccard_similarity(book_ids, table_indices):
    # Créer un dictionnaire pour stocker les ensembles de mots par livre
    word_sets = defaultdict(set)
    for index in table_indices:
        index_data = index.get_index_data()
        for book_id in index_data.keys():
            word_sets[book_id].add(index.word)

    # Calculer la similarité de Jaccard entre toutes les paires possibles
    similarities = {}
    book_ids_list = list(book_ids)
    for i, id1 in enumerate(book_ids_list):
        for id2 in book_ids_list[i+1:]:  # Commencer après id1 pour éviter les doublons
            if id1 == id2:
                continue
            set1 = word_sets[id1]
            set2 = word_sets[id2]
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            similarity = intersection / union if union > 0 else 0
            similarities[(id1, id2)] = similarity

    return similarities
