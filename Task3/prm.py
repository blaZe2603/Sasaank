import cv2 as cv
import numpy as np

# Load the image
image = cv.imread("Task3/maze.png")
height, width, _ = image.shape
image = cv.imread("Task3/maze.png", cv.IMREAD_GRAYSCALE)

# Define start and end points
start_1 = (40, height-30)
start_2 = (150, 30)
end_1 = (100, height-30)
end_2 = (450, height-30)

NODES = 100
RADIUS = 100
RADIUS_SQ = RADIUS ** 2
node = np.random.randint([20, 30], [width-20, height-30], size=(NODES, 2), dtype=np.int16)

node_possible = [start_1]
# node_possible = [start_2]
nodes = []
graph = {}

# Faster distance computation
def squ_dist(p1, p2):
    return np.sum((p1 - p2) ** 2)

def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Check if we can connect two points without an obstacle
def check_white_pixels(image, point1, point2):
    line_pixels = image.copy()
    cv.line(line_pixels, point1, point2, 128, 1) 
    line_points = cv.line(np.zeros_like(image), point1, point2, 128, 1)
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            if line_points[y, x] == 128:  
                if not image[y, x] == 255 and not image[y, x] == 128:
                    return False
    return True

#checks if we satisfy both 
def dist_check(image, p1, p2):
    if check_white_pixels(image, p1, p2):
        return squ_dist(p1, p2) < RADIUS_SQ
    else:
        return False  

# Add valid nodes to node_possible
for i in node:
    if (image[i[1], i[0]] == 255).all():
        cv.circle(image, tuple(i), 2, (128, 0, 0), -1)  
        node_possible.append(i)  

node_possible.append(end_1)  
node_possible = np.array(node_possible)
cv.circle(image, start_1, 2, 128, -1)
cv.circle(image, end_1, 2, 128, -1)

# node_possible.append(end_2)  
# node_possible = np.array(node_possible)
# cv.circle(image, start_2, 2, 128, -1)
# cv.circle(image, end_2, 2, 128, -1)


cv.imshow("image", image)
cv.waitKey(2000)
cv.destroyAllWindows()

# Check connectivity between nodes
for i in range(len(node_possible)):
    for j in range(i + 1, len(node_possible)):  
        if dist_check(image, node_possible[i], node_possible[j]):
            cv.line(image, tuple(node_possible[i]), tuple(node_possible[j]), 128, thickness=1, lineType=8, shift=0)
            nodes.append((node_possible[i], node_possible[j]))

cv.imshow("image", image)
cv.waitKey(5000)
cv.destroyAllWindows()

# Build the graph with distances
for (node1, node2) in nodes:
    node1_tuple = tuple(node1)
    node2_tuple = tuple(node2)
    dist = squ_dist(node1, node2)
    
    if node1_tuple not in graph:
        graph[node1_tuple] = []
    if node2_tuple not in graph:
        graph[node2_tuple] = []
    
    graph[node1_tuple].append((node2_tuple, dist))
    graph[node2_tuple].append((node1_tuple, dist))  

# Dijkstra's algorithm
def dijkstra(graph, start, goal):
    # Store shortest distances from start node
    shortest_distances = {start: 0}  
    # Store previous nodes for path reconstruction
    previous_nodes = {start: None}  
    # List of nodes that are still unvisited
    unvisited_nodes = set(graph.keys())  

    while unvisited_nodes:
        # Find the node with the smallest known distance
        current_node = min(
            unvisited_nodes, 
            key=lambda node: shortest_distances.get(node, float('inf'))
        )

        # If the smallest distance is infinity, remaining nodes are unreachable
        if shortest_distances.get(current_node, float('inf')) == float('inf'):
            break  

        # If we reached the goal, reconstruct the path
        if current_node == goal:
            path = []
            while current_node is not None:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            return path[::-1]  # Reverse to get correct order from start → goal

        # Explore neighbors and update distances
        for neighbor, weight in graph[current_node]:
            new_distance = shortest_distances[current_node] + weight
            if new_distance < shortest_distances.get(neighbor, float('inf')):
                shortest_distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node

        # Mark current node as visited
        unvisited_nodes.remove(current_node)

    return None  # No path found

# Convert start and goal nodes to tuples of integers
start_node = tuple(map(int, node_possible[0]))
goal_node = tuple(map(int, node_possible[-1]))

# Find the shortest path
path = dijkstra(graph, start_node, goal_node)

print("Shortest Path:", path)
# print(graph)
# Visualize the path
if path:
    for i in range(len(path) - 1):
        cv.line(image, tuple(path[i]), tuple(path[i + 1]), 0, thickness=2, lineType=8, shift=0)


cv.imshow("image", image)
cv.waitKey(5000)
cv.destroyAllWindows()
