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
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from datetime import datetime
    
def get_password_hidden(prompt="Masukkan Password        : "):
    """Membaca input password secara aman tanpa menampilkan karakter di terminal (Bisa Windows & Mac)"""
    password = getpass.getpass(prompt=prompt)
    return password

def catat_ke_excel_rekap(nama, nik, status, file_target="rekap-daftarkan.xlsx"):
    """Mencatat data siswa yang diproses langsung ke file Excel secara real-time"""
    import openpyxl
    from openpyxl import Workbook
    from datetime import datetime
    
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    baris_baru = [nama, f"'{nik}", waktu_sekarang, status]

    try:
        if os.path.exists(file_target):
            wb = openpyxl.load_workbook(file_target)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(["Nama", "NIK", "Tanggal Input", "Status"])
        
        ws.append(baris_baru)
        wb.save(file_target)
        wb.close()
        print(f" 📑 [EXCEL LOG] Berhasil mencatat status '{status}' untuk {nama}")
    except Exception as e:
        print(f" ⚠️ Gagal mencatat rekap Excel secara real-time: {e}")

def jalankan_bot():
    """Fungsi otentikasi login dan pemeriksaan HWID keamanan"""
    current_hwid = auth.get_hwid()
   
    if os.path.exists(auth.SESSION_FILE) and os.path.getsize(auth.SESSION_FILE) > 0:
        try:
            with open(auth.SESSION_FILE, "r") as f:
                sesi = json.load(f)
            
            if auth.check_auto_login(sesi.get("local_id"), current_hwid):
                print(" Sesi valid. Login otomatis berhasil!")
            else:
                print("Sesi tidak valid atau HWID berubah. Silakan login ulang.")
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

    if not os.path.exists(auth.SESSION_FILE) or 'auto_login_failed' in locals():
        print("==================================================")
        print("             BOT CKG SEKOLAH DAFTARKAN               ")
        print("==================================================")
        raw_username = input("Masukkan Email : ").strip()
        password = get_password_hidden("Masukkan Password        : ").strip()
        email = f"{raw_username}@bot.com" if "@" not in raw_username else raw_username
        
        sukses, pesan, kode, local_id = auth.login_with_approval(email, password, current_hwid)
        
        if not sukses:
            print(f"\n{pesan}")
            os.system("pause") if sys.platform.startswith('win') else input()
            sys.exit()
            
        with open(auth.SESSION_FILE, "w") as f:
            json.dump({"local_id": local_id}, f)
        print(f"\n {pesan}")

    muat_library_berat()

def main():
    import time
    import platform
    from datetime import datetime

    nama_file = 'data.xlsx' 
    try:
        df = pd.read_excel(nama_file)
        df['NIK'] = df['NIK'].astype(str).str.replace('.0', '', regex=False)
        
        kolom_nama = next((c for c in df.columns if c.lower() == 'nama'), None)
        
        if pd.api.types.is_datetime64_any_dtype(df['Tanggal Lahir']):
            df['Tanggal Lahir'] = df['Tanggal Lahir'].dt.strftime('%d/%m/%Y')
        else:
            df['Tanggal Lahir'] = df['Tanggal Lahir'].astype(str).str.strip()
    except Exception as e:
        print(f" Gagal membaca file {nama_file}. Detail: {e}")
        os.system("pause") if sys.platform.startswith('win') else input()
        return

    print(f" Berhasil membaca {len(df)} data NIK dari spreadsheet.")

    print("\n--- PENGATURAN DATA ---")
    try:
        baris_awal = int(input(f"Masukkan nomor baris awal (1 - {len(df)}): "))
        baris_akhir = int(input(f"Masukkan nomor baris akhir ({baris_awal} - {len(df)}): "))
        
        if baris_awal < 1 or baris_akhir > len(df) or baris_awal > baris_akhir:
            print("Rentang baris data tidak valid! Program dihentikan.")
            return
    except ValueError:
        print("Input harus berupa angka! Program dihentikan.")
        return

    options = webdriver.ChromeOptions()
    path_profile = os.path.abspath("./ChromeProfile")
    options.add_argument(f"--user-data-dir={path_profile}") 
    
    sistem_os = platform.system().lower()
    if "windows" in sistem_os:
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    elif "darwin" in sistem_os:
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
    except Exception as e:
        print(f" Gagal membuka Google Chrome.")
        print("\n💡 SOLUSI: Tutup semua window Google Chrome yang masih aktif berjalan di background.")
        os.system("pause") if sys.platform.startswith('win') else input()
        return

    try:
        driver.get("https://sehatindonesiaku.kemkes.go.id/auth/login") 

        print("\n--- DETEKSI LOGIN ---")
        print("Pastikan Anda sudah stand-by di halaman utama, lalu tekan ENTER di Terminal...")
        input()

        wait = WebDriverWait(driver, 10)

        try:
            print("   Menunggu loading overlay hilang...")
            try:
                short_wait = WebDriverWait(driver, 1)
                short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
            except Exception:
                pass
                
            time.sleep(1.0)
            
            ckg_sekolah = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='CKG Sekolah']")))
            driver.execute_script("arguments[0].scrollIntoView(true);", ckg_sekolah)
            time.sleep(1.0)
            ckg_sekolah.click()
            print("   -> Berhasil klik CKG Sekolah")
            
            time.sleep(1.0)
            cari_individu = wait.until(EC.element_to_be_clickable((By.ID, "menu_cari/daftarkan_individu")))
            driver.execute_script("arguments[0].scrollIntoView(true);", cari_individu)
            time.sleep(1.0)
            cari_individu.click()
            print("   -> Berhasil klik Cari/Daftarkan Individu")
            time.sleep(0.5)
        except Exception as e:
            print(f" Gagal membuka menu navigasi awal. Error: {e}")
            driver.quit()
            return

        for index, row in df.iloc[baris_awal-1:baris_akhir].iterrows():
            nik_sekarang = row['NIK']
            sekolah_sekarang = row['Sekolah']
            kelas_sekarang = row['kelas'] 
            jk_sekarang = row['Jenis Kelamin']
            nama_sekarang = row[kolom_nama] if kolom_nama else row.get('Nama', 'Tidak Ada Nama')
            hp_sekarang = row['Hp']
            tanggal_sekarang = str(row['Tanggal Lahir']).strip()
            alamat_sekarang = row['alamat']
            
            print(f"\n🔍 [{index+1}/{len(df)}] Memproses NIK: {nik_sekarang}")
            
            try:
                print("   Menunggu loading overlay hilang...")
                try:
                    short_wait = WebDriverWait(driver, 1)
                    short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
                except Exception:
                    pass
                    
                time.sleep(1.0)
                
                tombol_daftar_baru = wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//button[descendant::*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'daftar baru')]]"
                )))
                driver.execute_script("arguments[0].scrollIntoView(true);", tombol_daftar_baru)
                time.sleep(1.0)
                tombol_daftar_baru.click()
                print("   -> Berhasil klik tombol Daftar Baru")
                
                time.sleep(1.0)
                field_nik = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='number']")))
                field_nik.clear()             
                time.sleep(1.0)
                field_nik.send_keys(nik_sekarang) 
                print(f"    Berhasil mengisi NIK {nik_sekarang} ke dalam kolom.")
                
                time.sleep(1.0) 
                tombol_cek_nik = wait.until(EC.element_to_be_clickable((
                    By.XPATH, "//button[descendant::*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cek nik')]]"
                )))
                driver.execute_script("arguments[0].scrollIntoView(true);", tombol_cek_nik)
                time.sleep(1.0)
                tombol_cek_nik.click()
                print("   -> Berhasil klik cek nik")
                
                time.sleep(1.0) 
                
                data_ditemukan = False
                try:
                    short_wait = WebDriverWait(driver, 5)
                    tombol_gunakan_data = short_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Gunakan Data')]")))
                    data_ditemukan = True
                except Exception:
                    data_ditemukan = False

                if data_ditemukan:
                    print("   [Kondisi] DATA DITEMUKAN di sistem!")
                    driver.execute_script("arguments[0].scrollIntoView(true);", tombol_gunakan_data)
                    time.sleep(1.0)
                    tombol_gunakan_data.click()
                    
                    time.sleep(1.0)
                    tombol_selanjutnya = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(., 'Selanjutnya')]")))
                    driver.execute_script("arguments[0].scrollIntoView(true);", tombol_selanjutnya)
                    time.sleep(1.0)
                    tombol_selanjutnya.click()
                    
                    try:
                        short_wait = WebDriverWait(driver, 2)
                        sudah_layanan = short_wait.until(EC.presence_of_element_located((
                            By.XPATH, "//div[contains(text(), 'Individu sudah menerima layanan')]"
                        )))
                        if sudah_layanan.is_displayed():
                            catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="Sudah Menerima Layanan")
                            
                            driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pendaftaran-anak-sekolah")
                            time.sleep(1.0)
                            continue
                    except Exception:
                        pass
                    
                    time.sleep(1.0)
                    tombol_lanjutkan = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Lanjutkan')]")))
                    driver.execute_script("arguments[0].scrollIntoView(true);", tombol_lanjutkan)
                    time.sleep(1.0)
                    tombol_lanjutkan.click()
                    
                    time.sleep(1.0)
                    tombol_selanjutnya_dua = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(., 'Selanjutnya')]")))
                    driver.execute_script("arguments[0].scrollIntoView(true);", tombol_selanjutnya_dua)
                    time.sleep(1.0)
                    tombol_selanjutnya_dua.click()
                    
                    time.sleep(1.0)
                    tombol_tutup = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Tutup')]")))
                    driver.execute_script("arguments[0].scrollIntoView(true);", tombol_tutup)
                    time.sleep(1.0)
                    tombol_tutup.click()
                    time.sleep(1.0)
                    
                    catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="Berhasil didaftarkan")
                
                else:
                    try:
                        print("Mencari dan memfokuskan kursor ke field input Nama Lengkap...")
                        input_nama = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@name='Nama' or @placeholder='Masukkan nama lengkap']")))
                        
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_nama)
                        time.sleep(1.0)
                        input_nama.click()
                        input_nama.clear()
                        time.sleep(1.0)
                        
                        print(f"Memasukkan Nama: {nama_sekarang}")
                        input_nama.send_keys(nama_sekarang)
                        time.sleep(1.0)
                        input_nama.send_keys(Keys.ENTER)
                        time.sleep(1.0)
                        
                        tanggal_str_bersih = str(tanggal_sekarang).strip().split(" ")[0]

                        try:
                            if tanggal_str_bersih.isdigit():
                                from datetime import timedelta
                                excel_epoch = datetime(1899, 12, 30)
                                tanggal_obj = excel_epoch + timedelta(days=int(tanggal_str_bersih))
                            elif "-" in tanggal_str_bersih:
                                tanggal_obj = datetime.strptime(tanggal_str_bersih, '%Y-%m-%d')
                            elif "/" in tanggal_str_bersih:
                                tanggal_obj = datetime.strptime(tanggal_str_bersih, '%d/%m/%Y')
                            else:
                                raise ValueError(f"Format tanggal tidak dikenali: {tanggal_str_bersih}")
                        except Exception as parse_err:
                            print(f"       [ERROR] Gagal parsing tanggal '{tanggal_sekarang}': {parse_err}")
                            raise parse_err
                            
                        tanggal_target = tanggal_obj.strftime('%Y-%m-%d')
                        tahun_target = tanggal_obj.year
                        bulan_target = tanggal_obj.month

                        print("Membuka picker tanggal lahir...")
                        picker_tanggal = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'mx-input-wrapper')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", picker_tanggal)
                        time.sleep(0.5)
                        picker_tanggal.click()
                        time.sleep(0.5)

                        print(f"Menyesuaikan tahun ke {tahun_target}...")
                        for _ in range(30):
                            tahun_tampil_text = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'mx-btn-current-year')]"))).text
                            tahun_tampil = int(tahun_tampil_text)
                            
                            if tahun_tampil == tahun_target:
                                break
                            elif tahun_tampil > tahun_target:
                                driver.find_element(By.XPATH, "//button[contains(@class, 'mx-btn-icon-double-left')]").click()
                            else:
                                driver.find_element(By.XPATH, "//button[contains(@class, 'mx-btn-icon-double-right')]").click()
                            time.sleep(1.0)

                        print(f"Menyesuaikan bulan ke {bulan_target}...")
                        bulan_map = {
                            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                            'mei': 5, 'jun': 6, 'jul': 7, 'agt': 8,
                            'sep': 9, 'okt': 10, 'nov': 11, 'des': 12
                        }

                        for _ in range(24): 
                            bulan_tampil_text = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'mx-btn-current-month')]"))).text
                            tahun_tampil_text = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'mx-btn-current-year')]"))).text
                            
                            bulan_tampil = bulan_map.get(bulan_tampil_text.lower().strip(), 0)
                            tahun_tampil = int(tahun_tampil_text)
                            
                            if bulan_tampil == bulan_target and tahun_tampil == tahun_target:
                                break
                                
                            if tahun_tampil > tahun_target:
                                driver.find_element(By.XPATH, "//button[contains(@class, 'mx-btn-icon-double-left')]").click()
                            elif tahun_tampil < tahun_target:
                                driver.find_element(By.XPATH, "//button[contains(@class, 'mx-btn-icon-double-right')]").click()
                            elif bulan_tampil > bulan_target:
                                driver.find_element(By.XPATH, "//button[contains(@class, 'mx-btn-icon-left')]").click()
                            else:
                                driver.find_element(By.XPATH, "//button[contains(@class, 'mx-btn-icon-right')]").click()
                            time.sleep(0.4)

                        print(f"Memilih tanggal: {tanggal_target}")
                        elemen_tanggal = wait.until(EC.element_to_be_clickable((By.XPATH, f"//td[@title='{tanggal_target}']")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemen_tanggal)
                        time.sleep(0.5)
                        elemen_tanggal.click()
                        time.sleep(0.5)
                        
                        print("Membuka dropdown jenis kelamin...")
                        dropdown_jk = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'Pilih jenis kelamin') and @class[contains(., 'cursor-pointer')]]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_jk)
                        time.sleep(1.0)
                        dropdown_jk.click()
                        time.sleep(1.0)

                        target_jk = str(jk_sekarang).strip().lower()
                        opsi_jk = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@data-v-fa819537 and not(contains(@class, 'absolute'))]//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_jk}')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opsi_jk)
                        time.sleep(1.0)
                        opsi_jk.click()
                        time.sleep(1.0)
                        
                        print(f"Mengisi nomor WhatsApp: {hp_sekarang}")
                        input_wa = wait.until(EC.element_to_be_clickable((By.ID, "No Whatsapp")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_wa)
                        time.sleep(1.0)
                        
                        input_wa.click()
                        input_wa.clear()
                        time.sleep(1.0)
                        
                        no_wa = str(hp_sekarang).strip().replace('.0', '')
                        if no_wa.startswith('+62'):
                            no_wa = no_wa[3:]
                        elif no_wa.startswith('62'):
                            no_wa = no_wa[2:]
                        elif no_wa.startswith('0'):
                            no_wa = no_wa[1:]
                            
                        input_wa.send_keys(no_wa)
                        time.sleep(1.0)
                        
                        print("Mengklik tombol Selanjutnya...")
                        tombol_selanjutnya_manual = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(., 'Selanjutnya')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol_selanjutnya_manual)
                        time.sleep(1.0)
                        tombol_selanjutnya_manual.click()
                        time.sleep(1.0)
                        
                        try:
                            pesan_error = WebDriverWait(driver, 2).until(
                                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Data peserta tidak valid')]"))
                            )
                            if pesan_error.is_displayed():
                                catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="Data Tidak Valid")
                                print("⚠️ [Sistem Kemenkes]: Data peserta tidak valid! Melakukan redirect...")
                                driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pendaftaran-anak-sekolah")
                                time.sleep(1.5)
                                continue 
                        except Exception:
                            pass

                        print("Mengklik tombol Lanjutkan...")
                        tombol_lanjutkan_dua = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(., 'Lanjutkan')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol_lanjutkan_dua)
                        time.sleep(1.0)
                        tombol_lanjutkan_dua.click()
                        time.sleep(1.0) 
                        
                        print("Membuka dropdown status pernikahan...")
                        dropdown_status = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'Pilih status pernikahan') and @class[contains(., 'cursor-pointer')]]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_status)
                        time.sleep(1.0)
                        dropdown_status.click()
                        time.sleep(1.0)

                        opsi_belum_menikah = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'belum menikah')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opsi_belum_menikah)
                        time.sleep(1.0)
                        opsi_belum_menikah.click()
                        time.sleep(1.0)
                        
                        print("Membuka dropdown penyandang disabilitas...")
                        dropdown_disabilitas = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'Pilih penyandang disabilitas') and @class[contains(., 'cursor-pointer')]]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_disabilitas)
                        time.sleep(1.0)
                        dropdown_disabilitas.click()
                        time.sleep(1.0)

                        opsi_tidak_disabilitas = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'cursor-pointer')]//div[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='tidak' or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'tidak memiliki')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opsi_tidak_disabilitas)
                        time.sleep(1.0)
                        opsi_tidak_disabilitas.click()
                        time.sleep(1.0)
                        
                        print("Membuka modal pemilihan nama sekolah...")
                        dropdown_sekolah = wait.until(EC.element_to_be_clickable((
                            By.XPATH, "//div[contains(@class, 'min-h-') and contains(@class, 'cursor-pointer') and contains(text(), 'Pilih nama sekolah')]"
                        )))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_sekolah)
                        time.sleep(1.0)
                        driver.execute_script("arguments[0].click();", dropdown_sekolah)
                        time.sleep(1.0)

                        nama_sekolah_target = str(sekolah_sekarang).strip()
                        input_cari_sekolah = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Cari nama sekolah']")))
                        
                        input_cari_sekolah.click()
                        input_cari_sekolah.clear()
                        time.sleep(1.0)
                        
                        for char in nama_sekolah_target:
                            input_cari_sekolah.send_keys(char)
                            time.sleep(0.05)
                        
                        input_cari_sekolah.send_keys(Keys.SPACE)
                        time.sleep(1.0)
                        input_cari_sekolah.send_keys(Keys.BACKSPACE)
                        time.sleep(1.5) 

                        semua_opsi = wait.until(EC.presence_of_all_elements_located((
                            By.XPATH, "//button[contains(@class, 'w-full') and contains(@class, 'text-left')]"
                        )))

                        opsi_sekolah = None
                        for btn in semua_opsi:
                            if nama_sekolah_target.lower() in btn.text.strip().lower():
                                opsi_sekolah = btn
                                break

                        if opsi_sekolah is None:
                            raise Exception(f"Sekolah '{nama_sekolah_target}' tidak ditemukan di daftar!")

                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opsi_sekolah)
                        time.sleep(1.0)
                        driver.execute_script("arguments[0].click();", opsi_sekolah)
                        time.sleep(1.0)
                        
                        print(f"Memilih jenjang kelas: {kelas_sekarang}")
                        kelas_target = f"Kelas {kelas_sekarang}" 

                        driver.execute_script("""
                            const els = document.querySelectorAll('div.cursor-pointer');
                            for (const el of els) {
                                if (el.textContent.trim() === 'Pilih jenjang pendidikan') {
                                    el.click();
                                    break;
                                }
                            }
                        """)
                        time.sleep(1.0)

                        semua_opsi_kelas = wait.until(EC.presence_of_all_elements_located((
                            By.XPATH, "//button[contains(@class, 'w-full') and contains(@class, 'text-left')]"
                        )))

                        opsi_kelas = None
                        for btn in semua_opsi_kelas:
                            if kelas_target.lower() in btn.text.strip().lower():
                                opsi_kelas = btn
                                break

                        if opsi_kelas is None:
                            raise Exception(f"Kelas '{kelas_target}' tidak ditemukan!")

                        driver.execute_script("arguments[0].click();", opsi_kelas)
                        time.sleep(1.0)
                        
                        print("Trigger checkbox alamat...")
                        time.sleep(1.0)

                        custom_check = wait.until(EC.element_to_be_clickable((
                            By.XPATH, "//input[@name='sameAddress']/following-sibling::div[contains(@class,'check')]"
                        )))

                        driver.execute_script("arguments[0].click();", custom_check)
                        time.sleep(1.0)
                        driver.execute_script("arguments[0].click();", custom_check)
                        time.sleep(1.0)
                        driver.execute_script("arguments[0].click();", custom_check)
                        time.sleep(1.0)
                        
                        print(f"Mengisi alamat: {alamat_sekarang}")
                        input_alamat = wait.until(EC.element_to_be_clickable((By.ID, "detail-domisili")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_alamat)
                        time.sleep(1.0)
                        
                        input_alamat.click()
                        input_alamat.clear()
                        time.sleep(1.0)
                        
                        input_alamat.send_keys(str(alamat_sekarang).strip())
                        time.sleep(1.0)
                        
                        print("Mengklik tombol Selanjutnya akhir...")
                        tombol_selanjutnya_akhir = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(., 'Selanjutnya')]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol_selanjutnya_akhir)
                        time.sleep(1.0)
                        driver.execute_script("arguments[0].click();", tombol_selanjutnya_akhir)
                        time.sleep(1.0)
                        
                        catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="Berhasil didaftarkan")
                        
                        driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pendaftaran-anak-sekolah")
                        time.sleep(1.0)
                        
                    except Exception as e:
                        print(f" Gagal mengisi data manual atau sekolah: {e}")
                        catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="Gagal Form Manual")

            except Exception as e:
                print(f" Gagal memproses baris ini. Mengembalikan halaman ke dashboard awal...")
                try:
                    driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pendaftaran-anak-sekolah")
                    time.sleep(1.0)
                except:
                    pass

    except KeyboardInterrupt:
        print("\ Program dihentikan paksa oleh pengguna.")
    finally:
        print("\n==================================================")
        print("Sesi browser dipertahankan agar tidak langsung tutup.")
        print("Gunakan CTRL+C untuk keluar dari program secara bersih.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nMenutup koneksi browser Chrome...")
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    try:
        jalankan_bot()
        main()
    except Exception as fatal_err:
        print(f"Terjadi error fatal luar: {fatal_err}")