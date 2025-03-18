from collections import defaultdict

def compute_jaccard_similarity(book_ids, table_indices):
    print(f"Nombre de TableIndex à traiter: {len(table_indices)}")
    print(f"Nombre de livres à comparer: {len(book_ids)}")
    
    # Créer un dictionnaire pour stocker les ensembles de mots par livre
    word_sets = defaultdict(set)
    for index in table_indices:
        index_data = index.get_index_data()  # {book_id: {occurrences, tfidf, score}}
        for book_id in index_data.keys():
            book_id_int = int(book_id) if isinstance(book_id, str) else book_id
            word_sets[book_id_int].add(index.word)

    # Calculer la similarité de Jaccard entre toutes les paires possibles
    similarities = {}
    book_ids_list = list(book_ids)
    pair_count = 0
    total_pairs = (len(book_ids_list) * (len(book_ids_list) - 1)) // 2
    print(f"Nombre total de paires à calculer: {total_pairs}")
    for i in range(len(book_ids_list)):
        for j in range(i + 1, len(book_ids_list)):
            id1 = book_ids_list[i]
            id2 = book_ids_list[j]
            set1 = word_sets[id1]
            set2 = word_sets[id2]
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            similarity = intersection / union if union > 0 else 0
            similarities[(id1, id2)] = similarity
            pair_count += 1
            if pair_count % 100000 == 0:
                print(f"Paires calculées: {pair_count}/{total_pairs}, Dernière similarité: {similarity}")

    return similarities
