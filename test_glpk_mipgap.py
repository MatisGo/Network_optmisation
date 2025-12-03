"""
Test GLPK mipgap options with oemof.solph
"""
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Create a simple MIP model
model = pyo.ConcreteModel()
model.x = pyo.Var(within=pyo.Binary)
model.y = pyo.Var(within=pyo.Binary)
model.obj = pyo.Objective(expr=model.x + model.y)
model.con = pyo.Constraint(expr=model.x + 2*model.y >= 1)

# Test GLPK solver with mipgap
solver = SolverFactory('glpk')

print("Testing different ways to set mipgap:")
print("\n1. Using solver.options dictionary:")
try:
    solver.options['mipgap'] = 0.05
    print(f"   solver.options = {dict(solver.options)}")
    result = solver.solve(model, tee=False)
    print("   SUCCESS!")
except Exception as e:
    print(f"   FAILED: {e}")

print("\n2. Using solver.options as assignment:")
try:
    solver2 = SolverFactory('glpk')
    solver2.options = {'mipgap': 0.05}
    print(f"   solver.options = {dict(solver2.options)}")
    result = solver2.solve(model, tee=False)
    print("   SUCCESS!")
except Exception as e:
    print(f"   FAILED: {e}")

print("\n3. Using cmdline options (--mipgap):")
try:
    solver3 = SolverFactory('glpk')
    result = solver3.solve(model, options_string="--mipgap 0.05", tee=False)
    print("   SUCCESS!")
except Exception as e:
    print(f"   FAILED: {e}")

print("\n4. Checking GLPK available command line options:")
try:
    import subprocess
    result = subprocess.run(['glpsol', '--help'], capture_output=True, text=True)
    if '--mipgap' in result.stdout:
        print("   --mipgap is available in GLPK")
        # Find the line with mipgap
        for line in result.stdout.split('\n'):
            if 'mipgap' in line.lower():
                print(f"   {line}")
    else:
        print("   --mipgap NOT found in GLPK help")
except Exception as e:
    print(f"   Could not check GLPK help: {e}")
