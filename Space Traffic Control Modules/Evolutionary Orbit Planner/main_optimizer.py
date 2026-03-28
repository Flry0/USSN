from genetic_optimizer import YorungePlani, fitness_hesapla, nesil_uret
import random

def run_orbit_cycle(n_iter):
    pop = [YorungePlani(random.randint(400, 2000), random.uniform(0, 98), random.uniform(0, 360)) for _ in range(30)]
    for i in range(n_iter):
        pop = fitness_hesapla(pop)
        print(f"EVOLUTION_STEP_{i+1}: BEST_FIT: {pop[0].fitness_skoru}")
        pop = nesil_uret(pop)
    return pop[0]

if __name__ == "__main__":
    b_plan = run_orbit_cycle(5)
    print(f"Final Optimize Yorunge: {vars(b_plan)}")
