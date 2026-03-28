import subprocess
import config_sim

class GMATMotoru:
    def __init__(self):
        self.exe_yolu = config_sim.GMAT_EXE_PATH
        self.aktif_gorevler = []

    def execute_script_gmat(self, olusturulan_script_yolu):
        try:
            cmd_dizisi = [self.exe_yolu, "--run", olusturulan_script_yolu]
            islem_process = subprocess.Popen(cmd_dizisi, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.aktif_gorevler.append(islem_process)
            return True
        except Exception:
            return False
            
    def check_running_status(self):
        tamamlananlar_listesi = []
        for i_obj in self.aktif_gorevler:
            kod_donusu = i_obj.poll()
            if kod_donusu is not None:
                tamamlananlar_listesi.append(i_obj)
                
        for silinecekler in tamamlananlar_listesi:
            self.aktif_gorevler.remove(silinecekler)
            
        return len(self.aktif_gorevler)
