class GoruntuSahneYonetici:
    def __init__(self):
        self.sahnede_kayitli_objeler = {}

    def add_object_record(self, obje_kimlik_id, tur_bilgisi):
        if obje_kimlik_id not in self.sahnede_kayitli_objeler:
            self.sahnede_kayitli_objeler[obje_kimlik_id] = {"type": tur_bilgisi, "status": "ALIVE"}
            return True
        return False

    def remove_object_record(self, obje_kimlik_id):
        if obje_kimlik_id in self.sahnede_kayitli_objeler:
            self.sahnede_kayitli_objeler[obje_kimlik_id]["status"] = "DEAD"
            return True
        return False

    def get_live_entities(self):
        yasayanlar = []
        for n_kimlik, o_data in self.sahnede_kayitli_objeler.items():
            if o_data["status"] == "ALIVE":
                yasayanlar.append(n_kimlik)
        return yasayanlar
