class UniversalMessageBus:
    def __init__(self):
        self.abone_haritasi = {}
        self.bekleyen_mesajlar = []

    def subscribe_to_topic(self, topic_ismi, callback_fonksiyonu):
        if topic_ismi not in self.abone_haritasi:
            self.abone_haritasi[topic_ismi] = []
        self.abone_haritasi[topic_ismi].append(callback_fonksiyonu)

    def publish_event(self, topic_ismi, event_verisi):
        self.bekleyen_mesajlar.append({"topic": topic_ismi, "data": event_verisi})
        
    def process_message_queue(self):
        islenen_sayisi = 0
        for mesaj_obj in self.bekleyen_mesajlar:
            t_name = mesaj_obj["topic"]
            if t_name in self.abone_haritasi:
                for c_fonksiyon in self.abone_haritasi[t_name]:
                    c_fonksiyon(mesaj_obj["data"])
                    islenen_sayisi += 1
        self.bekleyen_mesajlar = []
        return islenen_sayisi
