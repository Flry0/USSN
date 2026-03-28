import random

class YorungePlani:
    def __init__(self, altitude, inclination, phase):
        self.yukseklik = altitude
        self.egim = inclination
        self.faz = phase
        self.fitness_skoru = 0.0

    def mutate_plan(self):
        self.yukseklik += random.uniform(-10, 10)
        self.egim += random.uniform(-1, 1)
        self.faz += random.uniform(-5, 5)

def fitness_hesapla(plan_listesi):
    for plan in plan_listesi:
        risk = 0.0
        if plan.yukseklik < 200: risk += 100
        plan.fitness_skoru = 1000 - (risk + abs(plan.egim * 10))
    return sorted(plan_listesi, key=lambda x: x.fitness_skoru, reverse=True)

def nesil_uret(populasyon):
    en_iyiler = populasyon[:10]
    yeni_nesil = []
    for _ in range(50):
        parent = random.choice(en_iyiler)
        cocuk = YorungePlani(parent.yukseklik, parent.egim, parent.faz)
        cocuk.mutate_plan()
        yeni_nesil.append(cocuk)
    return yeni_nesil

if __name__ == "__main__":
    pop = [YorungePlani(random.randint(300, 1000), random.uniform(0, 90), random.uniform(0, 360)) for _ in range(50)]
    for i in range(5):
        pop = fitness_hesapla(pop)
        print(f"Nesil {i+1} En Iyi Fitness: {pop[0].fitness_skoru}")
        pop = nesil_uret(pop)
