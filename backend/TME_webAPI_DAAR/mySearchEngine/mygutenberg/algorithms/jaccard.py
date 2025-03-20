from collections import defaultdict

def compute_jaccard_similarity(book_ids, all_docs, threshold):
    similarities = {}
    book_sets = {book_id: set(words) for book_id, words in all_docs.items()}
    
    for i, id1 in enumerate(book_ids):
        for id2 in book_ids[i+1:]:
            set1 = book_sets[id1]
            set2 = book_sets[id2]
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            similarity = intersection / union if union > 0 else 0
            if similarity >= threshold:
                similarities[(id1, id2)] = similarity
    
    return similarities
