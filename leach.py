import numpy as np
import random
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *

# Parameters
num_nodes = 50  # Number of sensor nodes
area_size = 100  # Size of the simulation area (100x100 grid)
initial_energy = 10.0  # Initial energy in Joules for each node
tx_energy = 0.5  # Transmission energy per message
rx_energy = 0.3  # Reception energy per message
cluster_range = 20  # Communication range for cluster formation (reduced for visibility)
round_duration = 100  # Duration of each round in milliseconds
max_rounds = 50  # Maximum number of rounds
cluster_head_probability = 0.2  # Probability of a node becoming a cluster head

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
nodes = [Node(i, random.uniform(10, area_size-10), random.uniform(10, area_size-10), initial_energy) for i in range(num_nodes)]

# LEACH clustering function
def form_clusters(nodes, round_num):
    cluster_heads = []
    for node in nodes:
        if random.random() < cluster_head_probability and node.energy > 0:
            node.is_cluster_head = True
            cluster_heads.append(node)
        else:
            node.is_cluster_head = False
    return cluster_heads

# Find isolated nodes (those too far from any cluster head)
def find_isolated_nodes(nodes, cluster_heads, threshold=cluster_range):
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

# Energy consumption simulation
def simulate_communication(nodes, cluster_heads):
    for node in nodes:
        if node.is_isolated:
            node.drain_energy(tx_energy * 2)  # Higher energy consumption for isolated nodes
        elif node.is_cluster_head:
            node.drain_energy(tx_energy)  # Cluster heads drain energy
        else:
            node.drain_energy(rx_energy)  # Cluster members drain energy for receiving

# Visualization with Matplotlib and NetworkX
def visualize_network(round_num, cluster_heads, isolated_nodes):
    plt.clf()  # Clear the figure
    G = nx.Graph()

    # Add nodes to the graph
    for node in nodes:
        color = 'green' if node.energy > 0 else 'red'
        G.add_node(node.node_id, pos=(node.x, node.y), node_color=color)

    # Cluster heads in blue, isolated nodes in orange
    for ch in cluster_heads:
        nx.draw_networkx_nodes(G, pos=nx.get_node_attributes(G, 'pos'), nodelist=[ch.node_id], node_size=100, node_color='blue')
    for iso in isolated_nodes:
        nx.draw_networkx_nodes(G, pos=nx.get_node_attributes(G, 'pos'), nodelist=[iso.node_id], node_size=100, node_color='orange')

    # Regular nodes in green
    for node in nodes:
        if not node.is_cluster_head and node not in isolated_nodes:
            nx.draw_networkx_nodes(G, pos=nx.get_node_attributes(G, 'pos'), nodelist=[node.node_id], node_size=50, node_color='green')

    # Draw circular ranges for cluster heads
    for ch in cluster_heads:
        circle = plt.Circle((ch.x, ch.y), cluster_range, color='blue', fill=False, lw=1.5)  # Thinner lines for circles
        plt.gca().add_patch(circle)

    plt.title(f"WSN Simulation - Round {round_num}")
    plt.xlim(0, area_size)
    plt.ylim(0, area_size)
    plt.gca().set_aspect('equal', adjustable='box')  # Ensure equal scaling of x and y axes

# Tooltip hover function
def on_hover(event):
    if event.inaxes == plt.gca():
        for node in nodes:
            # Check for hover over a node (sensor or cluster head)
            if (node.x - event.xdata)**2 + (node.y - event.ydata)**2 < 4:  # Adjust sensitivity
                state = "Cluster Head" if node.is_cluster_head else "Isolated" if node.is_isolated else "Active"
                hover_text.set(f"Node ID: {node.node_id}\nEnergy: {node.energy:.2f}\nPosition: ({node.x:.2f}, {node.y:.2f})\nState: {state}")
                return
        
        for ch in cluster_heads:
            # Check for hover over a cluster head circle
            distance = np.sqrt((ch.x - event.xdata)**2 + (ch.y - event.ydata)**2)
            if abs(distance - cluster_range) < 1.5:  # Adjust sensitivity for circle boundary
                hover_text.set(f"Cluster Head Circle\nCenter: ({ch.x:.2f}, {ch.y:.2f})\nRadius: {cluster_range}")
                return

        hover_text.set("")  # Clear hover text if not hovering over a node or circle

# Step time handler
def update_time_label():
    time_label.config(text=f"Step Time: {round_num.get()}")

# Control Functions
def play_simulation():
    global is_paused
    is_paused = False
    root.after(round_duration, run_simulation)

def pause_simulation():
    global is_paused
    is_paused = True

def forward_simulation():
    global round_num
    if round_num.get() < max_rounds:
        round_num.set(round_num.get() + 1)
        simulate_and_render()

def backward_simulation():
    global round_num
    if round_num.get() > 1:
        round_num.set(round_num.get() - 1)
        simulate_and_render()

# Main simulation loop
def run_simulation():
    global is_paused

    if is_paused:
        return

    # Check if the maximum number of rounds has been reached
    if round_num.get() > max_rounds:
        pause_simulation()  # Pause the simulation if the limit is reached
        return

    simulate_and_render()

    round_num.set(round_num.get() + 1)  # Increment the round
    root.after(round_duration, run_simulation)  # Schedule next step

# Separate function to simulate and render a single round
def simulate_and_render():
    global cluster_heads
    cluster_heads = form_clusters(nodes, round_num.get())
    isolated_nodes = find_isolated_nodes(nodes, cluster_heads)
    simulate_communication(nodes, cluster_heads)
    visualize_network(round_num.get(), cluster_heads, isolated_nodes)
    canvas.draw()  # Redraw the canvas
    update_time_label()

# GUI setup
root = Tk()
root.title("WSN Simulation")

# Create a frame for the matplotlib figure
frame = Frame(root)
frame.pack(side=TOP)

# Initialize figure for Matplotlib
fig = plt.figure(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().pack()

# Initialize round number and control variables
round_num = IntVar(value=1)
is_paused = True

# Time step display
time_label = Label(root, text=f"Step Time: {round_num.get()}")
time_label.pack()

# Hover text display
hover_text = StringVar()
hover_label = Label(root, textvariable=hover_text)
hover_label.pack()

# Play, Pause, Forward, Backward Buttons
controls_frame = Frame(root)
controls_frame.pack(side=BOTTOM)

play_button = Button(controls_frame, text="Play", command=play_simulation)
play_button.pack(side=LEFT)

pause_button = Button(controls_frame, text="Pause", command=pause_simulation)
pause_button.pack(side=LEFT)

forward_button = Button(controls_frame, text="Forward", command=forward_simulation)
forward_button.pack(side=LEFT)

backward_button = Button(controls_frame, text="Backward", command=backward_simulation)
backward_button.pack(side=LEFT)

# Hover functionality
canvas.mpl_connect("motion_notify_event", on_hover)

# Start the Tkinter main loop
root.mainloop()
