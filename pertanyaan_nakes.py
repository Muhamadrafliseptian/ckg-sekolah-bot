import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DATABASE_PERTANYAAN = {
    "Gizi Anak Sekolah": [
        "Berat Badan",
        "Tinggi Badan"
    ],
    "Tekanan Darah Anak dan Remaja": [
        "Tekanan Darah Sistol",
        "Tekanan Darah Diastol"
    ],
    "Pemeriksaan Penyakit Frambusia Anak Sekolah (untuk daerah endemis atau berisiko frambusia)": [
        "Apakah ada papul/nodul/ulkus/krusta papiloma?"
    ],
    "Pemeriksaan Penyakit Kusta Anak Sekolah": [
        "Apakah tubuh anda ada bercak kulit putih atau merah"
    ],
    "Pemeriksaan Penyakit Skabies": [
        "Apakah ada koreng/ruam/bentol/kudis"
    ],
    "Pemeriksaan Gigi - Anak": [
        "Berapa jumlah gigi karies?"
    ],
    "Hasil Pemeriksaan Kebugaran Jasmani Anak": [
        "Hasil pemeriksaan kebugaran jasmani anak"
    ],
    "Skrining Telinga dan Mata - Anak Sekolah": [
        "Apakah ada gangguan pendengaran di telinga kanan?",
        "Apakah ada gangguan pendengaran di telinga kiri?",
        "Apakah ada serumen impaksi di telinga kanan?",
        "Apakah ada serumen impaksi di telinga kiri?",
        "Apakah ada infeksi di telinga kanan?",
        "Apakah ada infeksi di telinga kiri?",
        "Apakah ditemukan selaput mata merah atau kornea keruh atau kelopak mata ada benjolan atau susah berkedip atau posisi bola mata juling atau pupil putih pada mata kanan?",
        "Apakah ditemukan selaput mata merah atau kornea keruh atau kelopak mata ada benjolan atau susah berkedip atau posisi bola mata juling atau pupil putih pada mata kiri?",
        "Hasil skrining tajam penglihatan mata kanan",
        "Hasil skrining tajam penglihatan mata kiri",
        "Apakah menggunakan kacamata atau tidak?"
    ]
}

def jawab_pertanyaan_nakes(driver, wait, jenis_pemeriksaan, row_data=None):
    daftar_pertanyaan = DATABASE_PERTANYAAN.get(jenis_pemeriksaan, [])
    if not daftar_pertanyaan:
        return
        
    for i, teks_soal in enumerate(daftar_pertanyaan, start=1):
        xpath_container_soal = f"//*[contains(text(), '{teks_soal}')]//ancestor::div[contains(@class, 'sd-question')]"
        
        # ── CASE 1: INPUT ANGKA (GIZI & TENSI) ─────────────────────────────
        if jenis_pemeriksaan in ["Gizi Anak Sekolah", "Tekanan Darah Anak dan Remaja"]:
            xpath_input = f"{xpath_container_soal}//input[@type='number']"
            field_angka = wait.until(EC.presence_of_element_located((By.XPATH, xpath_input)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field_angka)
            field_angka.clear()
            
            nilai_input = "0"
            if row_data is not None:
                if jenis_pemeriksaan == "Gizi Anak Sekolah":
                    nilai_input = str(row_data['BB']) if i == 1 else str(row_data['TB'])
                elif jenis_pemeriksaan == "Tekanan Darah Anak dan Remaja":
                    nilai_input = str(row_data['Sistol']) if i == 1 else str(row_data['Diastol'])
                    
            field_angka.send_keys(nilai_input)
            time.sleep(0.2)
            
        # ── CASE 2: KLIK TOMBOL / SPAN RADIO (GIGI, FRAMBUSIA, MATA/TELINGA) ─
        elif jenis_pemeriksaan in [
            "Pemeriksaan Gigi - Anak", 
            "Pemeriksaan Penyakit Frambusia Anak Sekolah (untuk daerah endemis atau berisiko frambusia)",
            "Skrining Telinga dan Mata - Anak Sekolah"
        ]:
            gunakan_pencarian_parsial = False
            teks_tombol = "Tidak ada" # Default aman
            
            if jenis_pemeriksaan == "Pemeriksaan Gigi - Anak":
                val_mentah = str(row_data['Jumlah Karies']).strip().replace('\xa0', '') if row_data is not None else "0"
                if val_mentah in ["", "nan", "-", "tidak ada", "0", "0.0"]:
                    teks_tombol = "Tidak ada"
                else:
                    try:
                        jumlah_karies = int(float(val_mentah))
                        if jumlah_karies == 1:
                            teks_tombol = "1"
                        elif jumlah_karies == 2:
                            teks_tombol = "2"
                        elif jumlah_karies == 3:
                            teks_tombol = "3"
                        elif jumlah_karies > 3:
                            teks_tombol = ">3"
                        else:
                            teks_tombol = "Tidak ada" 
                    except ValueError:
                        teks_tombol = "Tidak ada"
                    
            elif jenis_pemeriksaan == "Skrining Telinga dan Mata - Anak Sekolah":
                if i in [1, 2, 7, 8]:
                    teks_tombol = "Normal"
                elif i in [3, 4]:
                    teks_tombol = "Tidak ada serumen impaksi"
                elif i in [5, 6]:
                    teks_tombol = "Tidak ada infeksi telinga"
                elif i in [9, 10]:
                    teks_tombol = "visus 6/6" 
                    gunakan_pencarian_parsial = True
                elif i == 11:
                    val_kacamata = str(row_data['KACAMATA']).strip().lower() if row_data is not None else "tidak"
                    if val_kacamata in ["ya", "menggunakan", "pakai", "1"]:
                        teks_tombol = "Ya"
                    else:
                        teks_tombol = "Tidak"
            else:
                # Untuk Frambusia dan Skabies (jika pakai tombol span)
                teks_tombol = "Tidak Ada"
            
            # Eksekusi Klik Tombol/Radio Span
            if gunakan_pencarian_parsial:
                xpath_opsi = f"{xpath_container_soal}//span[contains(text(), '{teks_tombol}')]"
            else:
                xpath_opsi = f"{xpath_container_soal}//span[text()='{teks_tombol}']"
                
            opsi_tombol = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opsi)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opsi_tombol)
            opsi_tombol.click()
            time.sleep(0.15)
                
        # ── CASE 3: CUSTOM DROPDOWN (KUSTA, KEBUGARAN, SKABIES DROPDOWN) ───
        else:
            teks_pilihan = "Tidak Ada"
            if jenis_pemeriksaan == "Pemeriksaan Penyakit Kusta Anak Sekolah":
                teks_pilihan = "Tidak Ada"
            elif jenis_pemeriksaan == "Hasil Pemeriksaan Kebugaran Jasmani Anak":
                teks_pilihan = "Baik"

            # Klik Buka Dropdown
            xpath_dropdown_click = f"{xpath_container_soal}//div[contains(@class, 'sd-dropdown') or contains(@class, 'sd-input')]"
            dropdown_el = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_dropdown_click)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_el)
            dropdown_el.click()
            time.sleep(0.3) 

            # Klik Item Opsi dari Dropdown
            xpath_opsi_list = f"{xpath_container_soal}//li[contains(@class, 'sv-list__item')]//*[text()='{teks_pilihan}']"
            opsi_pilihan = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_opsi_list)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opsi_pilihan)
            opsi_pilihan.click()
            time.sleep(0.2)