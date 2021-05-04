# Using a Python dictionary to act as an adjacency list
# graph = {
#     'A': ['B', 'D'],
#     'B': ['C'],
#     'C': ['F'],
#     'D': ['G'],
#     'E': [],
#     'F': ['I'],
#     'G': ['H'],
#     'H': ['I'],
#     'I': []

# }

graph = {}

visited = set()  # Set to keep track of visited nodes.
queue = []
count = 0


def mod_dfs(visited, graph, node, dest):
    global count
    if node not in visited:
        print(node)
        if node == dest:
            count = count + 1
        else:
            visited.add(node)
        for neighbour in graph[node]:
            mod_dfs(visited, graph, neighbour, dest)


def dfs(visited, graph, node):
    if node not in visited:
        print(node)

        visited.add(node)
        for neighbour in graph[node]:
            dfs(visited, graph, neighbour)

# TODO


def bfs(visited, graph, node):
    if node not in visited:
        print(node)
        visited.add(node)
        # Add the nrighbor in the quque
        for neighbour in graph[node]:
            queue.append(neighbour)
        bfs(visited, graph, queue.pop(0))


# build a graph based on matrix
obstacleGrid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
row, col = len(obstacleGrid), len(obstacleGrid[0])


def idx(i, j):
    return ((i*col) + (j+1))
# def rev_idx(idx)


for i in range(row):
    for j in range(col):
        node = str(idx(i, j))
        node_neighbor = []
        if j < col-1 and obstacleGrid[i][j+1] == 0:  # right
            node_neighbor.append(str(idx(i, j+1)))
            #graph[node] = str(idx(i, j+1))
        if i < row-1 and j < col and obstacleGrid[i+1][j] == 0:  # down
            node_neighbor.append(str(idx(i+1, j)))
            #graph[node] = str(idx(i+1, j))
        graph[node] = node_neighbor

# print graph (as it is dictionary)
for i in graph:
    print(i, graph[i])

# Driver Code
#dfs(visited, graph, '1')
#bfs(visited, graph, '1')
mod_dfs(visited, graph, str(1), str(row*col))
print("count = ", count)
