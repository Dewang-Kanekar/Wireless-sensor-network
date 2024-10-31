import numpy as np
import matplotlib.pyplot as plt

# Specific energy data after simulation (in Joules)
leach_energy = [8.0, 7.5, 5.5, 6.0, 9.0, 4.5, 3.0, 2.0, 1.0]  # LEACH
mac_energy = [7.0, 6.5, 4.5, 5.0, 8.0, 3.5, 2.0, 1.5, 0.5]     # MAC
directed_diffusion_energy = [6.0, 5.5, 3.5, 4.0, 7.0, 2.5, 1.0, 0.0]  # Directed Diffusion
ideal_energy = np.linspace(0, 10, 100)  # Ideal WSN energy distribution

# Function to plot CDF
def plot_cdf(data, label, color):
    sorted_data = np.sort(data)
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    plt.plot(sorted_data, cdf, marker='o', linestyle='-', label=label, color=color)

# Plotting
plt.figure(figsize=(10, 6))
plot_cdf(leach_energy, 'LEACH', 'blue')
plot_cdf(mac_energy, 'MAC', 'orange')
plot_cdf(directed_diffusion_energy, 'Directed Diffusion', 'green')

# Ideal WSN line (assumed ideal state, completely flat CDF)
ideal_cdf = np.linspace(0, 1, 100)
plt.plot(ideal_energy, ideal_cdf, linestyle='--', color='black', label='Ideal WSN')

# Customizing the plot
plt.title('CDF of Remaining Energy for WSN Protocols')
plt.xlabel('Remaining Energy (Joules)')
plt.ylabel('CDF')
plt.xlim(0, 10)  # Adjust according to the expected range of energy
plt.ylim(0, 1)  # CDF should be between 0 and 1
plt.grid()
plt.legend()
plt.show()
