"""
Espoo District Heating Network Optimization
This script runs the investment optimization for the Espoo DHN project
with 2 CHP producers, 5 consumers, 7 forks, and 2 pipe types (DN30, DN50)
"""

import matplotlib.pyplot as plt
import dhnx
import pandas as pd
import os

print('='*70)
print('ESPOO DISTRICT HEATING NETWORK - INVESTMENT OPTIMIZATION')
print('='*70)
print()

# Create output directory if it doesn't exist
os.makedirs('Outputs', exist_ok=True)

# Initialize thermal network
print('[1/5] Initializing thermal network...')
network = dhnx.network.ThermalNetwork()

# Load town parameters (topology, consumers, producers, forks)
print('[2/5] Loading network topology and demand data...')
network = network.from_csv_folder(r"DHNx_files/Example_1/twn_data")

# Load investment parameters (pipe types, costs, capacities)
print('[3/5] Loading investment options (DN30 and DN50 pipes)...')
invest_opt = dhnx.input_output.load_invest_options(r"DHNx_files/Example_1/invest_data")

print()
print('Network Configuration:')
print(f'  Producers: {len(network.components.producers)} (Suomenoja & Kivenlahti CHP)')
print(f'  Consumers: {len(network.components.consumers)}')
print(f'  Forks: {len(network.components.forks)}')
print(f'  Pipe segments: {len(network.components.pipes)}')
print(f'  Pipe types available: DN30, DN50')
print()

# Plot initial network
print('[4/5] Plotting initial network topology...')
fig, ax = plt.subplots(figsize=(12, 8))
static_map = dhnx.plotting.StaticMap(network)
static_map.draw(background_map=False)
plt.scatter(network.components.consumers['lon'], network.components.consumers['lat'],
            color='tab:green', label='Consumers', zorder=2.5, s=100)
plt.scatter(network.components.producers['lon'], network.components.producers['lat'],
            color='tab:red', label='CHP Producers', zorder=2.5, s=150)
plt.scatter(network.components.forks['lon'], network.components.forks['lat'],
            color='tab:grey', label='Forks', zorder=2.5, s=80, alpha=0.6)
plt.title('Espoo District Heating Network - Initial Topology', fontsize=14)
plt.xlabel('Longitude', fontsize=12)
plt.ylabel('Latitude', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Outputs/Espoo_initial_network.png', dpi=150)
print('  → Saved: Outputs/Espoo_initial_network.png')
plt.show()

# Run optimization
print()
print('[5/5] Running investment optimization...')
print('  Solver: GLPK (GNU Linear Programming Kit)')
print('  Optimizing pipe types, capacities, and routing...')
print()

network.optimize_investment(invest_options=invest_opt, solver='glpk')

print()
print('='*70)
print('OPTIMIZATION COMPLETE!')
print('='*70)
print()

# Extract results
results_edges = network.results.optimization['components']['pipes']

# Save detailed results
results_edges.to_csv("Outputs/Espoo_optimization_results_detailed.csv", index=True)
print('Results saved to: Outputs/Espoo_optimization_results_detailed.csv')
print()

# Display results summary
print('='*70)
print('OPTIMIZATION RESULTS SUMMARY')
print('='*70)
print()
print('Pipe Investment Results:')
print('-'*70)
results_summary = results_edges[['from_node', 'to_node', 'hp_type', 'capacity',
                                  'direction', 'costs', 'losses']]
print(results_summary.to_string())
print()

# Objective value
objective = network.results.optimization['oemof_meta']['objective']
print(f'Total Investment Cost (Objective Value): {objective:.2f} €')
print()

# Count pipe types used
pipe_type_counts = results_edges[results_edges['capacity'] > 0.001]['hp_type'].value_counts()
print('Pipe Types Used:')
for pipe_type, count in pipe_type_counts.items():
    print(f'  {pipe_type}: {count} segments')
print()

# Check if both pipe types are used
if len(pipe_type_counts) >= 2:
    print('✓ SUCCESS: Both DN30 and DN50 pipe types are utilized!')
else:
    print('⚠ WARNING: Only one pipe type was selected. Consider adjusting parameters.')
print()

# Total capacity and losses
total_capacity = results_edges[results_edges['capacity'] > 0.001]['capacity'].sum()
total_losses = results_edges[results_edges['capacity'] > 0.001]['losses'].sum()
print(f'Total Installed Capacity: {total_capacity:.2f} kW')
print(f'Total Heat Losses: {total_losses:.2f} kW')
print()

# Plot optimized network
print('Plotting optimized network...')
twn_results = network
twn_results.components['pipes'] = results_edges[results_edges['capacity'] > 0.001]

fig, ax = plt.subplots(figsize=(14, 10))
static_map_2 = dhnx.plotting.StaticMap(twn_results)
static_map_2.draw(background_map=False)

# Color code by pipe type
dn30_pipes = results_edges[results_edges['hp_type'] == 'DN30']
dn50_pipes = results_edges[results_edges['hp_type'] == 'DN50']

plt.scatter(network.components.consumers['lon'], network.components.consumers['lat'],
            color='tab:green', label='Consumers', zorder=2.5, s=100)
plt.scatter(network.components.producers['lon'], network.components.producers['lat'],
            color='tab:red', label='CHP Producers', zorder=2.5, s=150)
plt.scatter(network.components.forks['lon'], network.components.forks['lat'],
            color='tab:grey', label='Forks', zorder=2.5, s=80, alpha=0.6)

plt.title('Espoo District Heating Network - Optimized Investment', fontsize=14)
plt.xlabel('Longitude', fontsize=12)
plt.ylabel('Latitude', fontsize=12)
plt.legend(fontsize=10, loc='best')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Outputs/Espoo_optimized_network.png', dpi=150)
print('  → Saved: Outputs/Espoo_optimized_network.png')
plt.show()

print()
print('='*70)
print('ANALYSIS COMPLETE!')
print('='*70)
print()
print('Generated files:')
print('  1. Outputs/Espoo_initial_network.png')
print('  2. Outputs/Espoo_optimized_network.png')
print('  3. Outputs/Espoo_optimization_results_detailed.csv')
print()
