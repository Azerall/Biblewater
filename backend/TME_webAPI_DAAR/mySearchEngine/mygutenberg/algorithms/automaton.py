from typing import List, Set
from collections import defaultdict, deque

class RegExTree:
    CONCAT = 1000
    ETOILE = ord('*')
    ALTERN = ord('|')
    DOT = ord('.')

    def __init__(self, root: int, subtrees: List['RegExTree'] = None):
        self.root = root
        self.subtrees = subtrees or []

    def __str__(self):
        if not self.subtrees:
            if self.root == self.CONCAT:
                return '.'
            if self.root == self.ETOILE:
                return '*'
            if self.root == self.ALTERN:
                return '|'
            if self.root == self.DOT:
                return '.'
            return chr(self.root)
        root_str = {self.CONCAT: '.', self.ETOILE: '*', self.ALTERN: '|', self.DOT: '.'}.get(self.root, chr(self.root))
        return f"{root_str}({','.join(str(t) for t in self.subtrees)})"

class RegExParser:
    def __init__(self, regex: str):
        self.regex = regex

    def char_to_root(self, c: str) -> int:
        return ord(c)

    def parse(self) -> RegExTree:
        trees = [RegExTree(self.char_to_root(c)) for c in self.regex]
        while len(trees) > 1 or ord('(') in [t.root for t in trees]:
            trees = self._process_parentheses(trees)
            trees = self._process_etoile(trees)
            trees = self._process_concat(trees)
            trees = self._process_altern(trees)
        return trees[0]

    def _process_parentheses(self, trees: List[RegExTree]) -> List[RegExTree]:
        result = []
        i = 0
        while i < len(trees):
            if trees[i].root == ord(')'):
                content = []
                while result and result[-1].root != ord('('):
                    content.insert(0, result.pop())
                if not result:
                    raise ValueError("Parenthèses non équilibrées")
                result.pop()
                sub_tree = self.parse_sub(content)
                result.append(sub_tree)
            else:
                result.append(trees[i])
            i += 1
        return result

    def parse_sub(self, trees: List[RegExTree]) -> RegExTree:
        while len(trees) > 1:
            trees = self._process_etoile(trees)
            trees = self._process_concat(trees)
            trees = self._process_altern(trees)
        return trees[0]

    def _process_etoile(self, trees: List[RegExTree]) -> List[RegExTree]:
        result = []
        i = 0
        while i < len(trees):
            if trees[i].root == RegExTree.ETOILE and not trees[i].subtrees and result:
                last = result.pop()
                result.append(RegExTree(RegExTree.ETOILE, [last]))
            else:
                result.append(trees[i])
            i += 1
        return result

    def _process_concat(self, trees: List[RegExTree]) -> List[RegExTree]:
        result = []
        i = 0
        while i < len(trees):
            if (result and i < len(trees) and 
                trees[i].root != RegExTree.ALTERN and 
                result[-1].root != RegExTree.ALTERN):
                last = result.pop()
                result.append(RegExTree(RegExTree.CONCAT, [last, trees[i]]))
            else:
                result.append(trees[i])
            i += 1
        return result

    def _process_altern(self, trees: List[RegExTree]) -> List[RegExTree]:
        result = []
        i = 0
        while i < len(trees):
            if trees[i].root == RegExTree.ALTERN and not trees[i].subtrees and result and i + 1 < len(trees):
                left = result.pop()
                right = trees[i + 1]
                result.append(RegExTree(RegExTree.ALTERN, [left, right]))
                i += 1
            else:
                result.append(trees[i])
            i += 1
        return result

class NFA:
    DOT_INDEX = 256

    def __init__(self):
        self.start_state = 0
        self.final_state = 0
        self.transitions = defaultdict(lambda: defaultdict(set))
        self.state_counter = 0
        self.symbols = set()

    def _next_state(self) -> int:
        self.state_counter += 1
        return self.state_counter - 1

    def from_regex_tree(self, tree: RegExTree) -> 'NFA':
        self.start_state, self.final_state = self._build_transitions(tree)
        return self

    def _build_transitions(self, tree: RegExTree) -> tuple[int, int]:
        if tree.root == RegExTree.CONCAT:
            if len(tree.subtrees) != 2:
                raise ValueError(f"Concaténation attend 2 sous-arbres, mais {len(tree.subtrees)} trouvé(s) : {tree}")
            start1, end1 = self._build_transitions(tree.subtrees[0])
            start2, end2 = self._build_transitions(tree.subtrees[1])
            self.transitions[end1][0].add(start2)
            return start1, end2

        elif tree.root == RegExTree.ALTERN:
            if len(tree.subtrees) != 2:
                raise ValueError(f"Alternance attend 2 sous-arbres, mais {len(tree.subtrees)} trouvé(s) : {tree}")
            start = self._next_state()
            end = self._next_state()
            start1, end1 = self._build_transitions(tree.subtrees[0])
            start2, end2 = self._build_transitions(tree.subtrees[1])
            self.transitions[start][0].add(start1)
            self.transitions[start][0].add(start2)
            self.transitions[end1][0].add(end)
            self.transitions[end2][0].add(end)
            return start, end

        elif tree.root == RegExTree.ETOILE:
            if len(tree.subtrees) != 1:
                raise ValueError(f"Étoile attend 1 sous-arbre, mais {len(tree.subtrees)} trouvé(s) : {tree}")
            start = self._next_state()
            end = self._next_state()
            inner_start, inner_end = self._build_transitions(tree.subtrees[0])
            self.transitions[start][0].add(inner_start)
            self.transitions[start][0].add(end)
            self.transitions[inner_end][0].add(inner_start)
            self.transitions[inner_end][0].add(end)
            return start, end

        else:  # Caractère ou DOT
            start = self._next_state()
            end = self._next_state()
            symbol = self.DOT_INDEX if tree.root == RegExTree.DOT else tree.root
            self.transitions[start][symbol].add(end)
            self.symbols.add(symbol)
            return start, end

class DFA:
    DOT_INDEX = 256

    def __init__(self):
        self.start_state = 0
        self.final_states = set()
        self.transitions = defaultdict(dict)
        self.state_counter = 0
        self.symbols = set()
        self.regex_length = 0  # Ajout pour limiter la longueur des mots acceptés

    def _next_state(self) -> int:
        self.state_counter += 1
        return self.state_counter - 1

    def _epsilon_closure(self, states: Set[int], nfa: NFA) -> Set[int]:
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for next_state in nfa.transitions[state].get(0, set()):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def from_nfa(self, nfa: NFA) -> 'DFA':
        self.symbols = nfa.symbols
        state_map = {}
        queue = deque()
        
        start_set = frozenset(self._epsilon_closure({nfa.start_state}, nfa))
        state_map[start_set] = self._next_state()
        self.start_state = state_map[start_set]
        queue.append(start_set)

        while queue:
            current_set = queue.popleft()
            current_state = state_map[current_set]

            for symbol in self.symbols:
                next_set = set()
                for state in current_set:
                    next_set.update(nfa.transitions[state].get(symbol, set()))
                if not next_set:
                    continue
                next_set = frozenset(self._epsilon_closure(next_set, nfa))

                if next_set not in state_map:
                    state_map[next_set] = self._next_state()
                    queue.append(next_set)
                self.transitions[current_state][symbol] = state_map[next_set]

            if nfa.final_state in current_set:
                self.final_states.add(current_state)

        return self

    def match(self, text: str) -> bool:
        current_state = self.start_state
        for char in text:
            symbol = ord(char)
            if symbol in self.transitions[current_state]:
                current_state = self.transitions[current_state][symbol]
            elif self.DOT_INDEX in self.transitions[current_state]:
                current_state = self.transitions[current_state][self.DOT_INDEX]
            else:
                return False
            if current_state in self.final_states:
                return True
        return current_state in self.final_states
    
    def transition(self, state: int, char: str) -> int:
        symbol = ord(char)
        if symbol in self.transitions[state]:
            return self.transitions[state][symbol]
        elif self.DOT_INDEX in self.transitions[state]:
            return self.transitions[state][self.DOT_INDEX]
        return -1  # Retourne -1 si aucune transition n'est possible

    def is_accepting(self, state: int) -> bool:
        return state in self.final_states

def build_dfa_from_regex(regex: str) -> DFA:
    parser = RegExParser(regex)
    tree = parser.parse()
    nfa = NFA().from_regex_tree(tree)
    return DFA().from_nfa(nfa)

if __name__ == "__main__":
    test_regexes = ["alice", ".*alice", "(ali*)", "..alice"]
    for regex in test_regexes:
        print(f"\nTesting regex: {regex}")
        dfa = build_dfa_from_regex(regex)
        print(f"Start state: {dfa.start_state}")
        print(f"Final states: {dfa.final_states}")
        print(f"Transitions: {dict(dfa.transitions)}")
        
        test_strings = ["alice", "malice", "chalice", "malicious", "ali", "alii", "waterfall"]
        for test_string in test_strings:
            print(f"Testing string: {test_string}")
            state = dfa.start_state
            for i, char in enumerate(test_string):
                state = dfa.transition(state, char)
                print(f"  After '{char}': state={state}, accepting={dfa.is_accepting(state)}")