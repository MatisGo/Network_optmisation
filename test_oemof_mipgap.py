"""
Test how oemof.solph.Model.solve() accepts mipgap
"""
from oemof import solph
import pyomo.environ as pyo
import pandas as pd

# Create simple energy system
timeindex = pd.date_range('2020-01-01', periods=3, freq='h')
es = solph.EnergySystem(timeindex=timeindex)

# Add a simple bus and source
bus = solph.Bus(label='bus')
source = solph.components.Source(
    label='source',
    outputs={bus: solph.Flow(
        nominal_value=solph.Investment(ep_costs=10, maximum=100),
        variable_costs=1
    )}
)
sink = solph.components.Sink(
    label='sink',
    inputs={bus: solph.Flow(nominal_value=50, fix=[1, 1, 1])}
)

es.add(bus, source, sink)

# Create model
model = solph.Model(es)

print("Test 1: Using solve_kwargs parameter")
try:
    model.solve(solver='glpk', solve_kwargs={'tee': False, 'options': {'mipgap': 0.05}})
    print("   SUCCESS with solve_kwargs={'options': {'mipgap': 0.05}}")
except Exception as e:
    print(f"   FAILED: {type(e).__name__}: {str(e)[:100]}")

# Recreate model for next test
es2 = solph.EnergySystem(timeindex=timeindex)
bus2 = solph.Bus(label='bus')
source2 = solph.components.Source(
    label='source',
    outputs={bus2: solph.Flow(
        nominal_value=solph.Investment(ep_costs=10, maximum=100),
        variable_costs=1
    )}
)
sink2 = solph.components.Sink(
    label='sink',
    inputs={bus2: solph.Flow(nominal_value=50, fix=[1, 1, 1])}
)
es2.add(bus2, source2, sink2)
model2 = solph.Model(es2)

print("\nTest 2: Using cmdline_options parameter")
try:
    model2.solve(solver='glpk', solve_kwargs={'tee': False}, cmdline_options={'mipgap': 0.05})
    print("   SUCCESS with cmdline_options={'mipgap': 0.05}")
except Exception as e:
    print(f"   FAILED: {type(e).__name__}: {str(e)[:100]}")

print("\nTest 3: Check oemof.solph.Model.solve signature")
import inspect
print(inspect.signature(solph.Model.solve))
