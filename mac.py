import numpy as np
import random
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *

"""
Green: Active nodes with energy.
Red: Inactive nodes (no energy).
Blue: Cluster heads (which can be designated based on some criteria in a real implementation).
Yellow: Isolated nodes (not in range of any other nodes)
"""

# Parameters
num_nodes = 50  # Number of sensor nodes
area_size = 100  # Size of the simulation area (100x100 grid)
initial_energy = 10.0  # Initial energy in Joules for each node
tx_energy = 0.5  # Transmission energy per message
rx_energy = 0.3  # Reception energy per message
cluster_range = 20  # Communication range for cluster formation
round_duration = 1000  # Duration of each round in milliseconds
max_rounds = 50  # Maximum number of rounds

# Node class
class Node:
    def __init__(self, node_id, x, y, energy):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.energy = energy
        self.is_transmitting = False
        self.state = 'active'  # Possible states: 'active', 'inactive', 'cluster_head', 'isolated'

    def distance_to(self, other_node):
        return np.sqrt((self.x - other_node.x)**2 + (self.y - other_node.y)**2)

    def drain_energy(self, amount):
        self.energy -= amount
        if self.energy < 0:
            self.energy = 0
            self.state = 'inactive'  # Node becomes inactive when energy is depleted

# Create random nodes
nodes = [Node(i, random.uniform(10, area_size-10), random.uniform(10, area_size-10), initial_energy) for i in range(num_nodes)]

# CSMA/CA protocol function
def csma_ca_transmission(nodes):
    for node in nodes:
        if node.energy > 0:
            # Simulating carrier sensing
            if not node.is_transmitting:
                if random.random() < 0.3:  # Probability of medium being busy
                    node.is_transmitting = True
                    node.drain_energy(tx_energy)  # Energy used for transmission
                else:
                    node.is_transmitting = False  # Not transmitting

# Visualization with Matplotlib and NetworkX
def visualize_network(round_num):
    plt.clf()  # Clear the figure
    G = nx.Graph()

    # Add nodes to the graph
    for node in nodes:
        # Determine color based on node state
        if node.state == 'active':
            color = 'green'
        elif node.state == 'inactive':
            color = 'red'
        elif node.state == 'cluster_head':
            color = 'blue'
        else:  # For isolated nodes
            color = 'yellow'

        G.add_node(node.node_id, pos=(node.x, node.y), node_color=color)

    # Draw nodes and circles
    for node in nodes:
        # Draw circles around nodes
        circle = plt.Circle((node.x, node.y), cluster_range, color='blue', fill=False, lw=1, alpha=0.5)
        plt.gca().add_patch(circle)

        # Draw the node itself
        nx.draw_networkx_nodes(G, pos=nx.get_node_attributes(G, 'pos'), nodelist=[node.node_id], node_size=50, node_color=color)

    plt.title(f"MAC Simulation - Round {round_num}")
    plt.xlim(0, area_size)
    plt.ylim(0, area_size)
    plt.gca().set_aspect('equal', adjustable='box')  # Ensure equal scaling of x and y axes

# Hover text functionality
def on_hover(event):
    if event.inaxes == plt.gca():
        for node in nodes:
            # Check for hover over a node (sensor)
            if (node.x - event.xdata)**2 + (node.y - event.ydata)**2 < 4:  # Adjust sensitivity
                hover_text.set(f"Node ID: {node.node_id}\nEnergy: {node.energy:.2f}\nState: {node.state}\nPosition: ({node.x:.2f}, {node.y:.2f})")
                return
            
            # Check for hover over a circle
            if (node.x - event.xdata)**2 + (node.y - event.ydata)**2 < (cluster_range)**2:  # Adjust sensitivity for circles
                hover_text.set(f"Node ID: {node.node_id}\nEnergy: {node.energy:.2f}\nState: {node.state}\nPosition: ({node.x:.2f}, {node.y:.2f})")
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
    csma_ca_transmission(nodes)
    visualize_network(round_num.get())
    canvas.draw()  # Redraw the canvas
    update_time_label()

# GUI setup
root = Tk()
root.title("MAC Simulation")

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

# Control Buttons
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
