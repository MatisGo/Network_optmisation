"""
Espoo District Heating Network Optimization
"""

import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import dhnx
import os

# Setup paths
base_dir = os.path.dirname(os.path.abspath(__file__))
twn_data_path = os.path.join(base_dir, "DHNx_files", "Espoo", "twn_data")
invest_data_path = os.path.join(base_dir, "DHNx_files", "Espoo", "invest_data")
os.makedirs('Outputs', exist_ok=True)

print('='*60)
print('ESPOO DHN - INVESTMENT OPTIMIZATION')
print('='*60)

# Load network
print('\n[1/3] Loading network...')
network = dhnx.network.ThermalNetwork()
network = network.from_csv_folder(twn_data_path)
invest_opt = dhnx.input_output.load_invest_options(invest_data_path)

print(f'  - Producers: {len(network.components.producers)}')
print(f'  - Consumers: {len(network.components.consumers)}')
print(f'  - Pipe segments: {len(network.components.pipes)}')

# Plot initial network topology
print('\nPlotting initial network...')
plt.figure(figsize=(10, 8))
static_map_initial = dhnx.plotting.StaticMap(network)
static_map_initial.draw(background_map=False)
plt.scatter(network.components.producers['lon'], network.components.producers['lat'],
            color='red', label='CHP Plants', s=150, zorder=3)
plt.scatter(network.components.consumers['lon'], network.components.consumers['lat'],
            color='green', label='Consumers', s=100, zorder=3)
plt.scatter(network.components.forks['lon'], network.components.forks['lat'],
            color='gray', label='Forks', s=50, zorder=2, alpha=0.6)
plt.title('Espoo DHN - Initial Network Topology', fontsize=14, fontweight='bold')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Outputs/network_initial.png', dpi=150, bbox_inches='tight')
plt.close()


# Run optimization
print('\n[2/3] Running optimization...')
network.optimize_investment(invest_options=invest_opt, solver='glpk')


# Get results
results = network.results.optimization['components']['pipes']
results.to_csv("Outputs/optimization_results.csv")

# Summary
print('\n[3/3] Results:')
print('-'*60)
objective = network.results.optimization['oemof_meta']['objective']
print(f'Total Cost: {objective:,.0f} EUR')

# Pipe types used
active_pipes = results[results['capacity'] > 0.001]
pipe_counts = active_pipes['hp_type'].value_counts()
print(f'\nPipes installed:')
for pipe_type, count in pipe_counts.items():
    total_cap = active_pipes[active_pipes['hp_type'] == pipe_type]['capacity'].sum()
    print(f'  {pipe_type}: {count} segments ({total_cap:.1f} kW)')

# Plot optimized network
print('\nCreating network plot...')
twn_plot = network
twn_plot.components['pipes'] = active_pipes

plt.figure(figsize=(10, 8))
static_map = dhnx.plotting.StaticMap(twn_plot)
static_map.draw(background_map=False)

# Add markers
plt.scatter(network.components.producers['lon'], network.components.producers['lat'],
            color='red', label='CHP Plants', s=150, zorder=3)
plt.scatter(network.components.consumers['lon'], network.components.consumers['lat'],
            color='green', label='Consumers', s=100, zorder=3)

plt.title('Espoo DHN - Optimized Network', fontsize=14, fontweight='bold')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Outputs/network_optimized.png', dpi=150, bbox_inches='tight')
plt.close()

print('\nGenerated files:')
print('  - Outputs/network_initial.png')
print('  - Outputs/network_optimized.png')
print('  - Outputs/optimization_results.csv')
