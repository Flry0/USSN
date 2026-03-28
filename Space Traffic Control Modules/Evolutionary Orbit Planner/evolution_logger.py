def log_nesil_verisi(nesil_no, e_score, n_birey):
    log_line = f"NESIL: {nesil_no} | AVG_FITNESS: {e_score} | TOP_IND: {n_birey}\n"
    with open("evolution_log.txt", "a") as l_file:
        l_file.write(log_line)
    return True

if __name__ == "__main__":
    log_nesil_verisi(1, 950.4, {"alt": 500, "inc": 10})
    print("Evrim Logu Kaydedildi.")
