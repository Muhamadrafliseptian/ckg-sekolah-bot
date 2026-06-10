import os
import sys
import json
import auth 
import getpass

pd = None
webdriver = None
By = None
Keys = None
WebDriverWait = None
EC = None
Service = None
datetime = None

def muat_library_berat():
    """Memuat library besar hanya jika user sudah sukses melewati login"""
    global pd, webdriver, By, Keys, WebDriverWait, EC, Service, datetime
    print("🔄 Memverifikasi modul sistem, mohon tunggu...")
    
    import pandas as pd
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    from datetime import datetime
    
    from pertanyaan_mandiri_umum import jawab_semua_tidak
    from pertanyaan_nakes import jawab_pertanyaan_nakes
    
def get_password_hidden(prompt="Masukkan Password        : "):
    """Membaca input password secara aman tanpa menampilkan karakter di terminal (Bisa Windows & Mac)"""
    password = getpass.getpass(prompt=prompt)
    return password

def jalankan_bot():
    current_hwid = auth.get_hwid()
   
    if os.path.exists(auth.SESSION_FILE) and os.path.getsize(auth.SESSION_FILE) > 0:
        try:
            with open(auth.SESSION_FILE, "r") as f:
                sesi = json.load(f)
            
            if auth.check_auto_login(sesi.get("local_id"), current_hwid):
                print(" Sesi valid. Login otomatis berhasil!")
            else:
                print(" Sesi tidak valid atau HWID berubah. Silakan login ulang.")
                if os.path.exists(auth.SESSION_FILE):
                    os.remove(auth.SESSION_FILE)
                os.system("pause") if sys.platform.startswith('win') else input()
                sys.exit()
        except json.JSONDecodeError:
            print("⚠️ File sesi rusak. Mengatur ulang sesi...")
            os.remove(auth.SESSION_FILE)
            auto_login_failed = True
    else:
        auto_login_failed = True

    if os.path.exists(auth.SESSION_FILE) == False or 'auto_login_failed' in locals():
        print("==================================================")
        print("             BOT CKG SEKOLAH SEDANG PEMERIKSAAN               ")
        print("==================================================")
        raw_username = input("Masukkan Email : ").strip()
        password = get_password_hidden("Masukkan Password        : ").strip()
        email = f"{raw_username}@bot.com" if "@" not in raw_username else raw_username
        
        sukses, pesan, kode, local_id = auth.login_with_approval(email, password, current_hwid)
        
        if not sukses:
            print(f"\ {pesan}")
            os.system("pause") if sys.platform.startswith('win') else input()
            sys.exit()
            
        with open(auth.SESSION_FILE, "w") as f:
            json.dump({"local_id": local_id}, f)
        print(f"\n {pesan}")

    muat_library_berat()

def main():
    jalankan_bot()
    import time

    nama_file = 'data.xlsx' 
    file_log_gagal = 'nik_gagal_sedang.txt' 
    
    try:
        df = pd.read_excel(nama_file)
        df['Sekolah'] = df['Sekolah'].astype(str)
        df['kelas'] = df['kelas'].astype(str)
        df['BB'] = df['BB'].astype(str)
        df['TB'] = df['TB'].astype(str)
        df['Sistol'] = df['Sistol'].astype(str)
        df['Diastol'] = df['Diastol'].astype(str)
        df['Jumlah Karies'] = df['Jumlah Karies'].astype(str)
        df['KACAMATA'] = df['KACAMATA'].astype(str)
        df['NIK'] = df['NIK'].astype(str).str.replace('.0', '', regex=False)
        df['Jenis Kelamin'] = df['Jenis Kelamin'].astype(str).str.strip()
        if 'Kesehatan Reproduksi Putri - Anak Sekolah' in df.columns:
            df['Kesehatan Reproduksi Putri - Anak Sekolah'] = df['Kesehatan Reproduksi Putri - Anak Sekolah'].astype(str).str.strip()
    except Exception as e:
        print(f" Gagal membaca file {nama_file}")
        return

    print(f" Berhasil membaca {len(df)} data dari spreadsheet.")
    print("\n--- PENGATURAN DATA ---")
    try:
        baris_awal = int(input(f"Masukkan nomor baris awal (1 - {len(df)}): "))
        baris_akhir = int(input(f"Masukkan nomor baris akhir ({baris_awal} - {len(df)}): "))
        if baris_awal < 1 or baris_akhir > len(df) or baris_awal > baris_akhir:
            print(" Rentang baris data tidak valid! Program dihentikan.")
            return
    except ValueError:
        print(" Input harus berupa angka! Program dihentikan.")
        return

    total_proses = (baris_akhir - baris_awal) + 1
    sukses_count = 0
    gagal_count = 0
    total_durasi_sukses = 0.0

    with open(file_log_gagal, 'w') as f:
        f.write("=== DAFTAR NIK GAGAL ===\n")

    print("🔄 Sedang mencoba membuka Google Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=./ChromeProfile") 
    # path_profile = os.path.join(user_profile, "AppData", "Local", "Google", "Chrome", "User Data", "BotKemenkesProfile")
    # options.add_argument(f"--user-data-dir={path_profile}") 
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3")

    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
    except Exception as e:
        print(f" Gagal membuka Google Chrome")
        return

    try:
        driver.get("https://sehatindonesiaku.kemkes.go.id/auth/login") 
        print("\n--- DETEKSI LOGIN ---")
        print("Silakan login manual pada browser jika diperlukan.")
        print("Tekan ENTER di Terminal jika sudah stand-by di halaman utama...")
        input()

        wait = WebDriverWait(driver, 8) 

        try:
            try:
                short_wait = WebDriverWait(driver, 2.0)
                short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
            except Exception:
                pass
            
            ckg_sekolah = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='CKG Sekolah']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ckg_sekolah)
            ckg_sekolah.click()
            time.sleep(0.5)
            
            pelayanan = wait.until(EC.element_to_be_clickable((By.ID, "menu_pelayanan")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pelayanan)
            pelayanan.click()
            time.sleep(1.0) 
        except Exception as e:
            print(f" Gagal membuka menu navigasi awal")
            driver.quit()
            return

        from pertanyaan_mandiri_umum import jawab_semua_tidak
        from pertanyaan_nakes import jawab_pertanyaan_nakes

        for index, row in df.iloc[baris_awal-1:baris_akhir].iterrows():
            waktu_mulai_data = time.time()
            
            sekolah_sekarang = row['Sekolah']
            kelas_sekarang = row['kelas'] 
            nik_sekarang = row['NIK']
            jk_sekarang = row['Jenis Kelamin']
            
            menstruasi_sekarang = "Belum"
            if 'Kesehatan Reproduksi Putri - Anak Sekolah' in row:
                menstruasi_sekarang = row['Kesehatan Reproduksi Putri - Anak Sekolah']
                
            print(f"\n🔍 [{index+1}/{len(df)}] Memproses NIK: {nik_sekarang} ({jk_sekarang})")
            
            try:
                pilih_sekolah = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Pilih sekolah')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pilih_sekolah)
                pilih_sekolah.click()
                time.sleep(0.5)
                
                input_sekolah = wait.until(EC.presence_of_element_located((By.ID, "sekolah")))
                input_sekolah.clear()
                input_sekolah.send_keys(sekolah_sekarang)
                time.sleep(0.5)
                
                opsi_sekolah = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{sekolah_sekarang}') or translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')=translate('{sekolah_sekarang}', 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opsi_sekolah)
                opsi_sekolah.click()
                time.sleep(0.5)
                
                pilih_kelas = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Pilih kelas')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pilih_kelas)
                pilih_kelas.click()
                time.sleep(0.5)
                
                opsi_kelas = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{kelas_sekarang}')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opsi_kelas)
                opsi_kelas.click()
                time.sleep(0.5)
                
                tampilkan_pencarian = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-outline-primary')]//div[contains(text(), 'Tampilkan Pencarian')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tampilkan_pencarian)
                tampilkan_pencarian.click()
                time.sleep(0.5)
                
                dropdown_tipe = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Nomor Tiket')]")))
                dropdown_tipe.click()
                time.sleep(0.5)
                
                opsi_nik = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'hover:bg-gray-1')]//div[text()='NIK']")))
                opsi_nik.click()
                time.sleep(0.5)
                
                input_nik_field = wait.until(EC.presence_of_element_located((By.ID, "nik")))
                input_nik_field.clear()
                input_nik_field.send_keys(nik_sekarang)
                input_nik_field.send_keys(Keys.ENTER)
                time.sleep(1.0)
                
                tab_sedang = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'cursor-pointer') and contains(text(), 'Sedang Pemeriksaan')]")))
                tab_sedang.click()
                time.sleep(0.5)
                
                tombol_mulai = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-outline-primary')]//div[contains(text(), 'Mulai') or contains(text(), 'Lanjutkan')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol_mulai)
                tombol_mulai.click()
                time.sleep(1.2)

                targets = [
                    "Faktor Risiko Gula Darah Anak", "Faktor Risiko Malaria", "Gejala Cemas Remaja",
                    "Gejala Depresi Remaja", "Gejala Depresi Anak", "Gejala Cemas Anak",
                    "Kelayakan Tes Kebugaran", "Perilaku Merokok - Anak Sekolah", "Faktor Risiko Hepatitis SD",
                    "Faktor Risiko TB - Anak Kelas 4-12", "Faktor Risiko TB - Anak Kelas 1-3",
                    "Riwayat Imunisasi Rutin Anak Sekolah", "Kuesioner Tingkat Aktivitas Fisik - Tingkat Aktivitas Fisik"
                ]

                if "perempuan" in jk_sekarang.lower():
                    targets.append("Kesehatan Reproduksi Putri - Anak Sekolah")
                elif "laki" in jk_sekarang.lower():
                    targets.append("Kesehatan Reproduksi Putra - Anak Sekolah")

                quick_wait = WebDriverWait(driver, 2.5)
                
                for target in targets:
                    try:
                        btn_input = quick_wait.until(EC.element_to_be_clickable((By.XPATH, f"//tr[td[contains(text(), '{target}')]]//button[contains(., 'Input Data')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_input)
                        btn_input.click()
                        time.sleep(0.5) 
                        
                        jawab_semua_tidak(driver, wait, target, status_menstruasi=menstruasi_sekarang)
                        time.sleep(0.5)
                        
                        tombol_kirim = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='Kirim' and contains(@class, 'sd-navigation__complete-btn')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol_kirim)
                        tombol_kirim.click()
                        
                        wait.until(EC.invisibility_of_element_located((By.XPATH, "//input[@type='button' and @value='Kirim']")))
                        time.sleep(0.5)
                    except Exception:
                        continue

                targets_nakes = [
                    "Gizi Anak Sekolah", "Tekanan Darah Anak dan Remaja",
                    "Pemeriksaan Penyakit Frambusia Anak Sekolah (untuk daerah endemis atau berisiko frambusia)",
                    "Pemeriksaan Penyakit Kusta Anak Sekolah", "Pemeriksaan Penyakit Skabies",
                    "Pemeriksaan Gigi - Anak", "Hasil Pemeriksaan Kebugaran Jasmani Anak", "Skrining Telinga dan Mata - Anak Sekolah"
                ]

                for target_nakes in targets_nakes:
                    try:
                        xpath_btn_nakes = f"//*[contains(text(), '{target_nakes}')]//ancestor::div[contains(@class, 'grid-cols-5') or local-name()='tr']//button[contains(., 'Input Data')]"
                        btn_input_nakes = quick_wait.until(EC.element_to_be_clickable((By.XPATH, xpath_btn_nakes)))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_input_nakes)
                        btn_input_nakes.click()
                        time.sleep(0.5)
                        
                        # Pastikan fungsi ini menerima parameter row dengan benar
                        jawab_pertanyaan_nakes(driver, wait, target_nakes, row_data=row)
                        time.sleep(0.5)
                        
                        tombol_kirim_nakes = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='Kirim' and contains(@class, 'sd-navigation__complete-btn')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol_kirim_nakes)
                        tombol_kirim_nakes.click()
                        
                        wait.until(EC.invisibility_of_element_located((By.XPATH, "//input[@type='button' and @value='Kirim']")))
                        time.sleep(0.5)
                    except Exception:
                        continue

                btn_selesai = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Selesaikan Layanan')]//ancestor::button")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_selesai)
                btn_selesai.click()
                time.sleep(1.0)
                
                btn_konfirmasi = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Konfirmasi')]//ancestor::button")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_konfirmasi)
                btn_konfirmasi.click()
                time.sleep(2.0)
                
                driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pelayanan-sekolah")
                time.sleep(1.0)
                    
                waktu_selesai_data = time.time()
                durasi_data = waktu_selesai_data - waktu_mulai_data
                total_durasi_sukses += durasi_data
                sukses_count += 1
                print(f" Selesai! Waktu input data ini: {durasi_data:.2f} detik")
                    
            except Exception as e:
                print(f" Gagal memproses baris input ini! Error: {type(e).__name__}")
                with open(file_log_gagal, 'a') as f:
                    f.write(f"Baris {index+1} - NIK: {nik_sekarang} (Error: {type(e).__name__})\n")
                
                try:
                    driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pelayanan-sekolah")
                    time.sleep(2)
                except:
                    pass
                driver.refresh()
                time.sleep(2.5)
                gagal_count += 1
                continue

    except Exception as main_err:
        print(f"⚠️ Terjadi interupsi sistem utama: {main_err}")

    rata_rata_waktu = (total_durasi_sukses / sukses_count) if sukses_count > 0 else 0

    print("\n==================================================")
    print("       SEMUA DATA DALAM RENTANG SELESAI PROSES      ")
    print("==================================================")
    print(f" Total Target Data : {total_proses} data")
    print(f" Berhasil Diproses : {sukses_count} data")
    print(f" Gagal/Dilewati    : {gagal_count} data")
    print(f" Rata-rata Waktu   : {rata_rata_waktu:.2f} detik / data")
    print("==================================================")

    print("\nGoogle Chrome ditahan agar tetap terbuka.")
    print("Tekan CTRL+C di Terminal jika ingin menutup program...")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nBot dimatikan oleh pengguna. Menutup browser...")
            try:
                driver.quit()
            except:
                pass
            break

if __name__ == "__main__":
    main()