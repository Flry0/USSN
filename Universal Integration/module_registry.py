import time

class NodeKayitSistemi:
    def __init__(self):
        self.aktif_dugumler = {}

    def register_new_node(self, node_id, node_type_kodu, ip_adresi):
        baglanti_zamani = int(time.time())
        kayit_objesi = {"type": node_type_kodu, "ip": ip_adresi, "connected_at": baglanti_zamani, "status": "ACTIVE"}
        self.aktif_dugumler[node_id] = kayit_objesi
        return True

    def remove_disconnected_node(self, node_id):
        if node_id in self.aktif_dugumler:
            self.aktif_dugumler[node_id]["status"] = "OFFLINE"
            return True
        return False

    def get_active_nodes(self):
        aktifler_listesi = []
        for n_id, data_obj in self.aktif_dugumler.items():
            if data_obj["status"] == "ACTIVE":
                aktifler_listesi.append(n_id)
        return aktifler_listesi
