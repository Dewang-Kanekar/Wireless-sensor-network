import numpy as np
import random
import matplotlib.pyplot as plt
import networkx as nx

# Parameters
num_nodes = 20  # Number of sensor nodes
area_size = 100  # Size of the simulation area (100x100 grid)
initial_energy = 10.0  # Initial energy in Joules for each node
tx_energy = 0.5  # Transmission energy per message
rx_energy = 0.3  # Reception energy per message
rounds = 10  # Number of rounds for the simulation

# Node class
class Node:
    def __init__(self, node_id, x, y, energy):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.energy = energy
        self.is_cluster_head = False
        self.is_isolated = False

    def distance_to(self, other_node):
        return np.sqrt((self.x - other_node.x)**2 + (self.y - other_node.y)**2)

    def drain_energy(self, amount):
        self.energy -= amount
        if self.energy < 0:
            self.energy = 0

# Create random nodes
nodes = [Node(i, random.uniform(0, area_size), random.uniform(0, area_size), initial_energy) for i in range(num_nodes)]

# Clustering function (simplified for demonstration)
def form_clusters(nodes):
    cluster_heads = []
    for node in nodes:
        if random.random() < 0.2:  # 20% chance of becoming a cluster head
            node.is_cluster_head = True
            cluster_heads.append(node)
        else:
            node.is_cluster_head = False
    return cluster_heads

# Function to find isolated nodes (those too far from any cluster head)
def find_isolated_nodes(nodes, cluster_heads, threshold=30):
    isolated_nodes = []
    for node in nodes:
        if not node.is_cluster_head:
            distances = [node.distance_to(ch) for ch in cluster_heads]
            if min(distances) > threshold:
                node.is_isolated = True
                isolated_nodes.append(node)
            else:
                node.is_isolated = False
    return isolated_nodes

# Simulate energy consumption for communication
def simulate_communication(nodes, cluster_heads):
    for node in nodes:
        if node.is_isolated:
            node.drain_energy(tx_energy * 2)  # Higher energy consumption for isolated nodes
        elif node.is_cluster_head:
            node.drain_energy(tx_energy)  # Cluster heads drain energy
        else:
            node.drain_energy(rx_energy)  # Cluster members drain energy for receiving

# Visualization function
def visualize_network(nodes, cluster_heads, isolated_nodes, round_num):
    plt.figure(figsize=(8, 8))
    plt.xlim(0, area_size)
    plt.ylim(0, area_size)
    G = nx.Graph()
    
    # Add nodes
    for node in nodes:
        color = 'green' if node.energy > 0 else 'red'
        G.add_node(node.node_id, pos=(node.x, node.y), node_color=color)

    # Plot cluster heads, isolated nodes, and other nodes
    for ch in cluster_heads:
        plt.scatter(ch.x, ch.y, c='blue', s=100, label='Cluster Head' if ch == cluster_heads[0] else "")
    for iso in isolated_nodes:
        plt.scatter(iso.x, iso.y, c='orange', s=100, label='Isolated Node' if iso == isolated_nodes[0] else "")
    for node in nodes:
        if not node.is_cluster_head and node not in isolated_nodes:
            plt.scatter(node.x, node.y, c='green', s=50, label='Member Node' if node == nodes[0] else "")

    # Draw energy levels as labels
    for node in nodes:
        plt.text(node.x, node.y, f"{node.energy:.2f}", fontsize=8)

    plt.title(f"WSN Clustering and Energy Levels - Round {round_num}")
    plt.legend()
    plt.show()

# Run the simulation for a number of rounds
for round_num in range(1, rounds + 1):
    cluster_heads = form_clusters(nodes)
    isolated_nodes = find_isolated_nodes(nodes, cluster_heads)
    simulate_communication(nodes, cluster_heads)
    visualize_network(nodes, cluster_heads, isolated_nodes, round_num)
