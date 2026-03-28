import random

class OrbitPopulasyon:
    def __init__(self, size):
        self.bireyler = [self.rastgele_birey() for _ in range(size)]

    def rastgele_birey(self):
        return {"alt": random.randint(300, 2000), "inc": random.uniform(0, 98), "esc": random.uniform(0, 0.1)}

    def fitness(self, birey):
        risk = 0
        if birey["alt"] < 400: risk += 500
        return 1000 - (risk + (birey["inc"] * 2))

    def evrimlestir(self):
        sorted_pop = sorted(self.bireyler, key=lambda x: self.fitness(x), reverse=True)
        return sorted_pop[:5]

if __name__ == "__main__":
    pop = OrbitPopulasyon(20)
    en_iyiler = pop.evrimlestir()
    print(f"En Verimli Yorungeler: {en_iyiler}")
