"""
CR3BP Mu Calculator
This script calculates the characteristic mass parameter (mu) for various systems.
It demonstrates Phase 1.1 of the roadmap: Normalization.
"""

def calculate_mu(m1, m2):
    """
    Calculate the non-dimensional mass parameter mu.
    
    Args:
        m1 (float): Mass of the primary body (the larger one) in kg.
        m2 (float): Mass of the secondary body (the smaller one) in kg.
        
    Returns:
        float: mu = m2 / (m1 + m2)
    """
    return m2 / (m1 + m2)

def main():
    # Constants (approximate values in kg)
    # Source: NASA Planetary Fact Sheet
    MASS_SUN = 1.989e30
    MASS_EARTH = 5.972e24
    MASS_MOON = 7.348e22
    MASS_JUPITER = 1.898e27
    
    # System 1: Earth-Moon
    mu_earth_moon = calculate_mu(MASS_EARTH, MASS_MOON)
    
    # System 2: Sun-Earth
    mu_sun_earth = calculate_mu(MASS_SUN, MASS_EARTH)
    
    # System 3: Sun-Jupiter
    mu_sun_jupiter = calculate_mu(MASS_SUN, MASS_JUPITER)

    print("--- CR3BP Mass Parameter (mu) Calculator ---")
    print(f"System: Earth-Moon")
    print(f"  Primary (Earth): {MASS_EARTH:.2e} kg")
    print(f"  Secondary (Moon): {MASS_MOON:.2e} kg")
    print(f"  Mu: {mu_earth_moon:.6f}")
    print()
    
    print(f"System: Sun-Earth")
    print(f"  Primary (Sun):   {MASS_SUN:.2e} kg")
    print(f"  Secondary (Earth): {MASS_EARTH:.2e} kg")
    print(f"  Mu: {mu_sun_earth:.8f}")
    print()
    
    print(f"System: Sun-Jupiter")
    print(f"  Primary (Sun):   {MASS_SUN:.2e} kg")
    print(f"  Secondary (Jupiter): {MASS_JUPITER:.2e} kg")
    print(f"  Mu: {mu_sun_jupiter:.6f}")
    
    # Verification check
    # For Sun-Earth, mu is roughly 3e-6
    # For Earth-Moon, mu is roughly 0.01215
    
if __name__ == "__main__":
    main()
