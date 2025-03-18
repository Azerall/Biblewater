from collections import defaultdict, deque

# Constantes
CONCAT = 0xC04CA7
ETOILE = 0xE7011E
ALTERN = 0xA17E54
PROTECTION = 0xBADDAD
PARENTHESEOUVRANT = 0x16641664
PARENTHESEFERMANT = 0x51515151
DOT = 0xD07
DOT_INDEX = 256

# Classe pour l'arbre syntaxique
class RegExTree:
    def __init__(self, root, sub_trees=None):
        self.root = root
        self.sub_trees = sub_trees if sub_trees is not None else []

    def __str__(self):
        if not self.sub_trees:
            return self.root_to_string()
        result = self.root_to_string() + "(" + self.sub_trees[0].__str__()
        for subtree in self.sub_trees[1:]:
            result += "," + subtree.__str__()
        return result + ")"

    def root_to_string(self):
        if self.root == CONCAT:
            return "."
        if self.root == ETOILE:
            return "*"
        if self.root == ALTERN:
            return "|"
        if self.root == DOT:
            return "."
        return chr(self.root)

# Parsing de la regex en arbre syntaxique
class RegExParser:
    reg_ex = ""

    @staticmethod
    def set_reg_ex(regex):
        RegExParser.reg_ex = regex

    @staticmethod
    def char_to_root(c):
        if c == '.':
            return DOT
        if c == '*':
            return ETOILE
        if c == '|':
            return ALTERN
        if c == '(':
            return PARENTHESEOUVRANT
        if c == ')':
            return PARENTHESEFERMANT
        return ord(c)

    @staticmethod
    def parse():
        result = [RegExTree(RegExParser.char_to_root(c)) for c in RegExParser.reg_ex]
        return RegExParser._parse(result)

    @staticmethod
    def _parse(result):
        while RegExParser._contain_parenthese(result):
            result = RegExParser._process_parenthese(result)
        while RegExParser._contain_etoile(result):
            result = RegExParser._process_etoile(result)
        while RegExParser._contain_concat(result):
            result = RegExParser._process_concat(result)
        while RegExParser._contain_altern(result):
            result = RegExParser._process_altern(result)
        if len(result) > 1:
            raise Exception("Invalid regex: multiple roots")
        return RegExParser._remove_protection(result[0])

    @staticmethod
    def _contain_parenthese(trees):
        return any(t.root in (PARENTHESEFERMANT, PARENTHESEOUVRANT) for t in trees)

    @staticmethod
    def _process_parenthese(trees):
        result = []
        found = False
        for t in trees:
            if not found and t.root == PARENTHESEFERMANT:
                content = []
                while result and result[-1].root != PARENTHESEOUVRANT:
                    content.insert(0, result.pop())
                if not result:
                    raise Exception("Unmatched closing parenthesis")
                result.pop()  # Retirer '('
                found = True
                result.append(RegExTree(PROTECTION, [RegExParser._parse(content)]))
            else:
                result.append(t)
        if not found:
            raise Exception("No closing parenthesis found")
        return result

    @staticmethod
    def _contain_etoile(trees):
        return any(t.root == ETOILE and not t.sub_trees for t in trees)

    @staticmethod
    def _process_etoile(trees):
        result = []
        found = False
        for t in trees:
            if not found and t.root == ETOILE and not t.sub_trees:
                if not result:
                    raise Exception("No operand for *")
                found = True
                last = result.pop()
                result.append(RegExTree(ETOILE, [last]))
            else:
                result.append(t)
        return result

    @staticmethod
    def _contain_concat(trees):
        first_found = False
        for t in trees:
            if not first_found and t.root != ALTERN:
                first_found = True
                continue
            if first_found and t.root != ALTERN:
                return True
            first_found = False
        return False

    @staticmethod
    def _process_concat(trees):
        result = []
        first_found = False
        found = False
        for t in trees:
            if not found and not first_found and t.root != ALTERN:
                first_found = True
                result.append(t)
            elif not found and first_found and t.root == ALTERN:
                first_found = False
                result.append(t)
            elif not found and first_found and t.root != ALTERN:
                found = True
                last = result.pop()
                result.append(RegExTree(CONCAT, [last, t]))
            else:
                result.append(t)
        return result

    @staticmethod
    def _contain_altern(trees):
        return any(t.root == ALTERN and not t.sub_trees for t in trees)

    @staticmethod
    def _process_altern(trees):
        result = []
        found = False
        gauche = None
        for i, t in enumerate(trees):
            if not found and t.root == ALTERN and not t.sub_trees:
                if not result:
                    raise Exception("No left operand for |")
                found = True
                gauche = result.pop()
            elif found and gauche is not None:
                result.append(RegExTree(ALTERN, [gauche, t]))
                return result + trees[i + 1:]
            else:
                result.append(t)
        return result

    @staticmethod
    def _remove_protection(tree):
        if tree.root == PROTECTION and len(tree.sub_trees) != 1:
            raise Exception("Invalid protection node")
        if not tree.sub_trees:
            return tree
        if tree.root == PROTECTION:
            return RegExParser._remove_protection(tree.sub_trees[0])
        return RegExTree(tree.root, [RegExParser._remove_protection(t) for t in tree.sub_trees])

# Classe NDFA
class NDFA:
    def __init__(self):
        self.counter_state = 0
        self.start_state = None
        self.final_state = None
        self.transitions = None
        self.epsilon_transitions = None
        self.symbols = []

    def next_state_id(self):
        state = self.counter_state
        self.counter_state += 1
        return state

    def calcul_nb_states(self, tree):
        if tree.root == CONCAT:
            return self.calcul_nb_states(tree.sub_trees[0]) + self.calcul_nb_states(tree.sub_trees[1])
        elif tree.root == ALTERN or tree.root == ETOILE:
            return self.calcul_nb_states(tree.sub_trees[0]) + 2
        return 2

    def tree_to_ndfa(self, tree):
        nb_states = self.calcul_nb_states(tree)
        self.transitions = [[-1] * 257 for _ in range(nb_states)]
        self.epsilon_transitions = [[] for _ in range(nb_states)]
        self.build_transitions(tree)
        return self

    def build_transitions(self, tree):
        if tree.root == CONCAT:
            self.build_transitions(tree.sub_trees[0])
            old_start1, old_final1 = self.start_state, self.final_state
            self.build_transitions(tree.sub_trees[1])
            old_start2, old_final2 = self.start_state, self.final_state
            self.epsilon_transitions[old_final1].append(old_start2)
            self.start_state, self.final_state = old_start1, old_final2
        elif tree.root == ALTERN:
            self.build_transitions(tree.sub_trees[0])
            old_start1, old_final1 = self.start_state, self.final_state
            self.build_transitions(tree.sub_trees[1])
            old_start2, old_final2 = self.start_state, self.final_state
            self.start_state = self.next_state_id()
            self.final_state = self.next_state_id()
            self.epsilon_transitions[self.start_state].extend([old_start1, old_start2])
            self.epsilon_transitions[old_final1].append(self.final_state)
            self.epsilon_transitions[old_final2].append(self.final_state)
        elif tree.root == ETOILE:
            self.build_transitions(tree.sub_trees[0])
            old_start, old_final = self.start_state, self.final_state
            self.start_state = self.next_state_id()
            self.final_state = self.next_state_id()
            self.epsilon_transitions[self.start_state].extend([old_start, self.final_state])
            self.epsilon_transitions[old_final].extend([old_start, self.final_state])
        else:
            self.start_state = self.next_state_id()
            self.final_state = self.next_state_id()
            symbol = DOT_INDEX if tree.root == DOT else tree.root
            self.transitions[self.start_state][symbol] = self.final_state
            if symbol not in self.symbols:
                self.symbols.append(symbol)
            
# Classe DFA
class DFA:
    def __init__(self):
        self.state_id = 0
        self.start_state = None
        self.final_states = []
        self.transitions = defaultdict(dict)
        self.symbols = []

    def next_state_id(self):
        state = self.state_id
        self.state_id += 1
        return state

    def add_transition(self, source, symbol, target):
        self.transitions[source][symbol] = target

    def epsilon_closure(self, states, epsilon_transitions):
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            for next_state in epsilon_transitions[state]:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def determinize(self, ndfa):
        self.symbols = ndfa.symbols
        states = {}
        queue = deque()
        start_set = frozenset(self.epsilon_closure({ndfa.start_state}, ndfa.epsilon_transitions))
        states[start_set] = self.next_state_id()
        self.start_state = states[start_set]
        queue.append(start_set)

        while queue:
            current_set = queue.popleft()
            current_state = states[current_set]
            for symbol in self.symbols:
                next_set = set()
                for state in current_set:
                    if ndfa.transitions[state][symbol] != -1:
                        next_set.update(self.epsilon_closure({ndfa.transitions[state][symbol]}, ndfa.epsilon_transitions))
                if next_set:
                    next_set = frozenset(next_set)
                    if next_set not in states:
                        states[next_set] = self.next_state_id()
                        queue.append(next_set)
                    self.add_transition(current_state, symbol, states[next_set])
        self.final_states = [state_id for state_set, state_id in states.items() if ndfa.final_state in state_set]
        print(f"Final states={self.final_states}")
        return self

    def match(self, text):
        state = self.start_state
        for char in text:
            char_code = ord(char)
            if char_code in self.transitions[state]:
                state = self.transitions[state][char_code]
            elif DOT_INDEX in self.transitions[state]:
                state = self.transitions[state][DOT_INDEX]
            else:
                return False
        return state in self.final_states

# Fonction utilitaire pour construire un DFA à partir d'une regex
def build_dfa_from_regex(regex):
    RegExParser.set_reg_ex(regex)
    tree = RegExParser.parse()
    ndfa = NDFA().tree_to_ndfa(tree)
    return DFA().determinize(ndfa)
