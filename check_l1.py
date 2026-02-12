import numpy as np

def get_js_l1():
    mu = 0.01215
    alpha = (mu/3)**(1/3) # Math.cbrt
    guess = (1 - mu) - alpha
    
    # Python equivalent of JS loop
    x = guess
    for i in range(10):
        # function: x - (1-mu)/(x+mu)^2 + mu/(x-(1-mu))^2
        # Note: JS uses (x - (1-mu))**2 in denominator. Correct.
        # But sign?
        # JS: x - (1 - mu) / ((x + mu) ** 2) + mu / ((x - (1 - mu)) ** 2)
        
        f = x - (1 - mu) / ((x + mu) ** 2) + mu / ((x - (1 - mu)) ** 2)
        
        # Derivative (Central Difference in JS code)
        # df = (fn(x + 1e-5) - fn(x - 1e-5)) / 2e-5;
        
        val_plus = (x+1e-5) - (1 - mu) / ((x+1e-5 + mu) ** 2) + mu / ((x+1e-5 - (1 - mu)) ** 2)
        val_minus = (x-1e-5) - (1 - mu) / ((x-1e-5 + mu) ** 2) + mu / ((x-1e-5 - (1 - mu)) ** 2)
        df = (val_plus - val_minus) / 2e-5
        
        if abs(df) < 1e-8: break
        x = x - f / df
        
    return x

js_l1 = get_js_l1()
py_l1 = 0.836915

print(f"JS L1: {js_l1:.10f}")
print(f"Py L1: {py_l1:.10f}")
print(f"Diff:  {js_l1 - py_l1:.10f}")
