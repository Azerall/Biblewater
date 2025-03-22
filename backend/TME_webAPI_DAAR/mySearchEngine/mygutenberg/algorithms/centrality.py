from collections import defaultdict, deque

def build_graph(table_jaccard):
    graph = defaultdict(set)
    for sim in table_jaccard:
        book1_id = sim.book1.gutenberg_id
        book2_id = sim.book2.gutenberg_id
        graph[book1_id].add(book2_id)
        graph[book2_id].add(book1_id)  # Graphe non dirigé
    return graph

def closeness_centrality(graph, book_ids):
    closeness = {}
    for book_id in book_ids:
        distances = bfs_shortest_path(graph, book_id)
        total_distance = sum(dist for dist in distances.values() if dist != float('inf') and dist > 0)
        if total_distance > 0:
            # Normalisation par le nombre de noeuds accessibles - 1
            n = len([d for d in distances.values() if d != float('inf')]) - 1
            closeness[book_id] = n / total_distance if n > 0 else 0
        else:
            closeness[book_id] = 0
    return closeness

def bfs_shortest_path(graph, start):
    distances = {start: 0}
    queue = deque([start])
    visited = {start}

    while queue:
        current = queue.popleft()
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
    # Remplir les noeuds non atteints avec une distance infinie
    for node in graph:
        if node not in distances:
            distances[node] = float('inf')
    return distances

def betweenness_centrality(graph, book_ids):
    betweenness = defaultdict(float)
    all_nodes = set(graph.keys())

    for s in all_nodes:
        # BFS pour trouver les chemins les plus courts
        predecessors, shortest_paths = bfs_with_predecessors(graph, s)
        for t in all_nodes:
            if s == t:
                continue
            # Compter les chemins passant par chaque nœud
            paths_through = defaultdict(int)
            stack = [t]
            visited = set()
            while stack:
                v = stack.pop()
                if v in visited:
                    continue
                visited.add(v)
                if v in predecessors and s in predecessors[v]:
                    for u in predecessors[v][s]:
                        if u != s and u != t:
                            paths_through[u] += 1
                        stack.append(u)
            # Ajouter la contribution au score de betweenness
            for v in paths_through:
                betweenness[v] += paths_through[v] / shortest_paths[t] if shortest_paths[t] > 0 else 0

    # Normaliser et limiter aux book_ids demandés
    n = len(all_nodes)
    norm_factor = (n - 1) * (n - 2) / 2 if n > 2 else 1
    return {book_id: betweenness[book_id] / norm_factor for book_id in book_ids}

def bfs_with_predecessors(graph, start):
    distances = {start: 0}
    shortest_paths = {start: 1}
    predecessors = defaultdict(lambda: defaultdict(list))
    queue = deque([start])
    visited = {start}

    while queue:
        current = queue.popleft()
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                distances[neighbor] = distances[current] + 1
                shortest_paths[neighbor] = shortest_paths[current]
                predecessors[neighbor][start].append(current)
                queue.append(neighbor)
            elif distances[neighbor] == distances[current] + 1:
                shortest_paths[neighbor] += shortest_paths[current]
                predecessors[neighbor][start].append(current)
    return predecessors, shortest_paths
