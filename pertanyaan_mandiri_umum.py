import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DATABASE_PERTANYAAN = {
    "Faktor Risiko Gula Darah Anak": [
        "Apakah Anak Anda pernah dinyatakan diabetes",
        "sering merasa sangat lapar dan makan lebih banyak",
        "sering merasa haus meskipun sudah banyak minum",
        "tetap mengalami penurunan berat badan meskipun nafsu makan",
        "anggota keluarga lainnya (saudara kandung) yang pernah di diagnosis"
    ],
    "Faktor Risiko Malaria": [
        "Apakah terdapat salah satu atau lebih gejala seperti; demam, sakit kepala, dan menggigil?",
        "Apakah pernah sakit malaria dan obat tidak habis diminum?",
        "Apakah ada orang sakit malaria di wilayah tempat tinggal (di rumah atau tetangga sekitar rumah)?",
        "Apakah anda tinggal atau ada riwayat kedatangan dari daerah berisiko tinggi malaria selama 1 bulan terakhir?"
    ],
    "Gejala Cemas Remaja": [
        "Dalam 2 minggu terakhir, saya sering merasa khawatir atau tidak tenang, tegang, deg-degan dan gelisah terutama terhadap hal-hal negatif atau yang belum tentu terjadi.",
        "Dalam 2 minggu terakhir, Saya berpikir berlebihan dan tidak bisa mengendalikan diri, terutama terhadap hal-hal negatif atau yang belum tentu terjadi",
        "Dalam 2 minggu terakhir, Saya sulit tidur dan berkonsentrasi terutama saat memikirkan hal-hal negatif yang belum tentu terjadi"
    ],
     "Gejala Cemas Anak": [
        "Dalam 2 minggu terakhir, anak sering merasa khawatir atau tidak tenang, tegang, deg-degan dan gelisah terutama terhadap hal-hal negatif atau yang belum tentu terjadi.",
        "Dalam 2 minggu terakhir, anak berpikir berlebihan dan tidak bisa mengendalikan diri, terutama terhadap hal-hal negatif atau yang belum tentu terjadi.",
        "Dalam 2 minggu terakhir, anak sulit tidur dan berkonsentrasi terutama saat memikirkan hal-hal negatif yang belum tentu terjadi."
    ],
    "Gejala Depresi Remaja": [
        "Dalam 2 minggu terakhir, saya sering merasa sedih atau tertekan padahal tidak ada penyebab yang jelas.",
        "Dalam 2 minggu terakhir, saya tidak tertarik lagi dengan kegiatan atau hal-hal yang biasanya saya suka.",
        "Dalam 2 minggu terakhir, saya merasa sering capek, sulit tidur, dan sulit fokus saat belajar atau melakukan kegiatan."
    ],
    "Gejala Depresi Anak": [
        "Dalam 2 minggu terakhir, anak sering merasa sedih atau tertekan padahal tidak ada penyebab yang jelas.",
        "Dalam 2 minggu terakhir, anak tidak tertarik lagi dengan kegiatan atau hal-hal yang biasanya dia suka",
        "Dalam 2 minggu terakhir, anak merasa sering capek, sulit tidur, dan sulit fokus saat belajar atau melakukan kegiatan."
    ],
    "Kelayakan Tes Kebugaran": [
        "Apakah dokter pernah menyatakan bahwa Anda memiliki masalah pada tulang dan sendi seperti arthritis?",
        "Apakah dokter pernah menyatakan bahwa Anda memiliki masalah pada jantung dan bahwa anda hanya bisa melakukan aktivitas fisik sesuai anjuran dokter?",
        "Apakah  Anda menderita asma atau pernah terserang asma saat melakukan latihan fisik?",
        "Apakah  Anda pernah kehilangan kesadaran, sakit kepala parah, atau pingsan?"
    ],
    "Perilaku Merokok - Anak Sekolah": [
        "Apakah Anda merokok dalam setahun terakhir ini?",
        "Apakah Anda terpapar asap rokok atau menghirup asap rokok dari orang lain dalam sebulan terakhir?"
    ],
    "Faktor Risiko Hepatitis SD": [
        "Apakah Anda pernah menjalani tes untuk Hepatitis B dan mendapatkan hasil positif?",
        "Apakah Anda memiliki ibu kandung/saudara sekandung yang menderita Hepatitis B?",
        "Apakah Anda pernah menerima transfusi darah sebelumnya?",
        "Apakah Anda pernah menjalani cuci darah atau hemodialisis?"
    ],
    "Faktor Risiko TB - Anak Kelas 4-12": [
        "Apakah Anda pernah atau sedang mengalami batuk yang tidak sembuh-sembuh?",
        "Apakah berat badan Anda turun tanpa penyebab jelas/ BB tidak naik/ nafsu makan turun?",
        "Apakah Anda mengalami demam hilang timbul tanpa sebab yang jelas?",
        "Apakah Anda mengalami berkeringat di malam hari tanpa kegiatan?"
    ],
    "Faktor Risiko TB - Anak Kelas 1-3": [
        "Apakah anak Anda pernah atau sedang mengalami batuk yang tidak sembuh-sembuh?",
        "Apakah berat badan anak Anda turun tanpa penyebab jelas/ BB tidak naik dalam 2 bulan sebelumnya/ nafsu makan turun?",
        "Apakah anak anda mengalami demam hilang timbul tanpa sebab yang jelas lebih dari 2 minggu?",
        "Apakah anak Anda mengalami lesu atau malaise, anak kurang aktif bermain?"
    ],
    "Kuesioner Tingkat Aktivitas Fisik - Tingkat Aktivitas Fisik": [
        "Dalam 7 hari terakhir, berapa hari Anda aktif  secara  fisik  dalam  waktu  total selama  minimal  60  menit  sehari?",
        "Biasanya dalam satu minggu, berapa hari Anda aktif secara fisik dalam waktu total selama minimal 60 menit sehari?"
    ],
    "Kesehatan Reproduksi Putra - Anak Sekolah": [
        "Apakah mengalami gatal-gatal di kemaluan (alat kelamin) atau pernah kencing berwarna kuning kental seperti susu/nanah?",
        "Apakah mengalami nyeri/ tidak nyaman saat Buang Air Kecil (BAK) atau Buang Air Besar (BAB)?",
        "Apakah mengalami luka di anus atau dubur?"
    ],
    "Kesehatan Reproduksi Putri - Anak Sekolah": [
        "Apakah sudah mengalami menstruasi?",
        "Apakah pernah mengalami keputihan?",
        "Apakah pernah mengalami gatal-gatal di kemaluan?"
    ],
    "Riwayat Imunisasi Rutin Anak Sekolah": [
        "Apakah anak pernah memperoleh imunisasi polio tetes dan atau campak rubela saat usia 0 sd 24 bulan?"
    ]
}

def jawab_semua_tidak(driver, wait, jenis_pemeriksaan, status_menstruasi=None):
    daftar_pertanyaan = DATABASE_PERTANYAAN.get(jenis_pemeriksaan, [])
    if not daftar_pertanyaan:
        return
        
    for i, teks_soal in enumerate(daftar_pertanyaan, start=1):
        # ── CASE 1: KUESIONER ANGKA (AKTIVITAS FISIK) ──────────────────────
        if jenis_pemeriksaan == "Kuesioner Tingkat Aktivitas Fisik - Tingkat Aktivitas Fisik":
            xpath_input = (
                f"//div[contains(@class, 'sd-question')]//span[contains(text(), '{teks_soal}')]"
                f"//ancestor::div[contains(@class, 'sd-question')]//input[@type='number']"
            )
            field_angka = wait.until(EC.presence_of_element_located((By.XPATH, xpath_input)))
            field_angka.clear()
            field_angka.send_keys("6")
            
        elif jenis_pemeriksaan == "Riwayat Imunisasi Rutin Anak Sekolah":
            xpath_dropdown = (
                f"//div[contains(@class, 'sd-question')]//span[contains(text(), '{teks_soal}')]"
                f"//ancestor::div[contains(@class, 'sd-question')]//div[contains(@class, 'sd-dropdown')]"
            )
            dropdown_el = wait.until(EC.presence_of_element_located((By.XPATH, xpath_dropdown)))
            driver.execute_script("arguments[0].click();", dropdown_el)
            xpath_opsi_ya = (
                f"//div[contains(@class, 'sd-question')]//span[contains(text(), '{teks_soal}')]"
                f"//ancestor::div[contains(@class, 'sd-question')]//li[@role='option' and .//span[text()='Ya']]"
            )
            opsi_ya = wait.until(EC.presence_of_element_located((By.XPATH, xpath_opsi_ya)))
            driver.execute_script("arguments[0].click();", opsi_ya)
            time.sleep(0.2) 
            
        else:
            teks_tombol = "Tidak"
            if jenis_pemeriksaan == "Faktor Risiko TB - Anak Kelas 4-12" and i == 1:
                teks_tombol = "Tidak batuk"
            elif jenis_pemeriksaan == "Faktor Risiko TB - Anak Kelas 1-3" and i == 1:
                teks_tombol = "Tidak batuk"
            elif jenis_pemeriksaan == "Kesehatan Reproduksi Putri - Anak Sekolah" and i == 1:
                teks_tombol = "Ya" if status_menstruasi == "Sudah" else "Tidak"
                
            xpath_opsi = (
                f"//div[contains(@class, 'sd-question')]//span[contains(text(), '{teks_soal}')]"
                f"//ancestor::div[contains(@class, 'sd-question')]//span[text()='{teks_tombol}']"
            )
            opsi_tidak = wait.until(EC.presence_of_element_located((By.XPATH, xpath_opsi)))
            driver.execute_script("arguments[0].click();", opsi_tidak)