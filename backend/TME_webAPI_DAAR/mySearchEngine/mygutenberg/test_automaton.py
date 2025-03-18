import time
from mygutenberg.algorithms.automaton import RegExParser, NDFA, DFA, build_dfa_from_regex

def test_automaton():
    # Cas de test
    test_cases = [
        ("a", ["a"], ["b", "ab"]),  # Match exact
        ("ab", ["ab"], ["a", "b", "abc"]),  # Concaténation
        ("a|b", ["a", "b"], ["c", "ab"]),  # Alternance
        ("a*", ["", "a", "aa"], ["b", "ab"]),  # Étoile (0 ou plus)
        ("a.b", ["axb", "ayb"], ["ab", "a", "b"]),  # Dot (n’importe quel caractère)
    ]

    for regex, expected_matches, expected_non_matches in test_cases:
        print(f"\nTest de la regex : '{regex}'")
        
        # Construire le DFA
        try:
            dfa = build_dfa_from_regex(regex)
            print(f"DFA construit - État initial : {dfa.start_state}, États finaux : {dfa.final_states}")
        except Exception as e:
            print(f"Erreur lors de la construction : {e}")
            continue

        # Tester les correspondances
        print("Test des mots qui doivent matcher :")
        for word in expected_matches:
            result = dfa.match(word)
            print(f"  '{word}' -> {result}")
            assert result, f"'{word}' devrait matcher '{regex}'"

        # Tester les non-correspondances
        print("Test des mots qui ne doivent pas matcher :")
        for word in expected_non_matches:
            result = dfa.match(word)
            print(f"  '{word}' -> {result}")
            assert not result, f"'{word}' ne devrait pas matcher '{regex}'"

def test_performance():
    # Mesurer le temps de construction et de matching
    regex = "Gust.*"  # Exemple complexe
    words = ["Gustave", "Gusto", "Flaubert", "Gust", "Gusty"] * 1000  # Simuler beaucoup de mots
    
    # Temps avec DFA
    start_time = time.time()
    dfa = build_dfa_from_regex(regex)
    dfa_time_build = time.time() - start_time
    start_time = time.time()
    dfa_matches = [dfa.match(word) for word in words]
    dfa_time_match = time.time() - start_time
    print(f"DFA - Temps de construction : {dfa_time_build:.4f}s, Temps de matching : {dfa_time_match:.4f}s")

    # Temps avec re (comparaison)
    import re
    start_time = time.time()
    pattern = re.compile(regex)
    re_time_build = time.time() - start_time
    start_time = time.time()
    re_matches = [bool(pattern.match(word)) for word in words]
    re_time_match = time.time() - start_time
    print(f"re - Temps de construction : {re_time_build:.4f}s, Temps de matching : {re_time_match:.4f}s")

if __name__ == "__main__":
    print("=== Test de l'automate ===")
    test_automaton()
    print("\n=== Test de performance ===")
    test_performance()