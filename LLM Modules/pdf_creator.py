import os
import datetime
from fpdf import FPDF
import llm_config

class OlayRaporuPDF(FPDF):
    def header(self):
        self.set_font('Arial-Turkish', 'B', 15)
        self.cell(0, 10, 'USSN AI ACİL DURUM RAPORU', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font('Arial-Turkish', 'I', 8)
        self.cell(0, 10, 'USSN (Universal Satellite Safety Network)', 0, 1, 'C')
        self.cell(0, 10, f'Sayfa {self.page_no()}', 0, 0, 'C')

def create_event_pdf(rapor_metni, olay_etiketi):
    rapor_klasoru = llm_config.REPORT_OUTPUT_DIR
    if not os.path.exists(rapor_klasoru):
        os.makedirs(rapor_klasoru, exist_ok=True)
        
    pdf_document = OlayRaporuPDF()
    
    font_path_win = r"C:\Windows\Fonts\arial.ttf"
    font_path_win_bold = r"C:\Windows\Fonts\arialbd.ttf"
    font_path_win_italic = r"C:\Windows\Fonts\ariali.ttf"
    
    if os.path.exists(font_path_win):
        pdf_document.add_font("Arial-Turkish", "", font_path_win)
    if os.path.exists(font_path_win_bold):
        pdf_document.add_font("Arial-Turkish", "B", font_path_win_bold)
    if os.path.exists(font_path_win_italic):
        pdf_document.add_font("Arial-Turkish", "I", font_path_win_italic)
        
    pdf_document.add_page()
    pdf_document.set_font('Arial-Turkish', '', 12)
        
    tarih_metni = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    pdf_document.multi_cell(0, 10, txt=rapor_metni, markdown=True)
    
    dosya_kayit_yolu = os.path.join(rapor_klasoru, f"Event_Report_{olay_etiketi}_{tarih_metni}.pdf")
    pdf_document.output(dosya_kayit_yolu)
    
    return dosya_kayit_yolu
