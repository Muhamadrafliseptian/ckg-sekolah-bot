import os
import sys
import json
import auth 
import getpass
import platform

pd = None
webdriver = None
By = None
Keys = None
WebDriverWait = None
EC = None
Service = None
datetime = None

def muat_library_berat():
    global pd, webdriver, By, Keys, WebDriverWait, EC, Service, datetime
    print("Memverifikasi modul sistem, mohon tunggu...")
    import pandas as pd
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from datetime import datetime
    import time

def get_password_hidden(prompt="Masukkan Password        : "):
    password = getpass.getpass(prompt=prompt)
    return password

def catat_ke_excel_rekap(nama, nik, status, sekolah, kelas, file_target="rekap-belum-pemeriksaan.xlsx"):
    import openpyxl
    from openpyxl import Workbook
    from datetime import datetime
    
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    baris_baru = [nama, f"'{nik}", status, sekolah, kelas, waktu_sekarang]

    try:
        if os.path.exists(file_target):
            wb = openpyxl.load_workbook(file_target)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(["Nama", "NIK", "Status", "Sekolah", "Kelas", "Tanggal"])
        
        ws.append(baris_baru)
        wb.save(file_target)
        wb.close()
    except Exception as e:
        print(f"Gagal mencatat rekap Excel: {e}")

def jalankan_bot():
    current_hwid = auth.get_hwid()
    if os.path.exists(auth.SESSION_FILE) and os.path.getsize(auth.SESSION_FILE) > 0:
        try:
            with open(auth.SESSION_FILE, "r") as f:
                sesi = json.load(f)
            if auth.check_auto_login(sesi.get("local_id"), current_hwid):
                print("Sesi valid. Login otomatis berhasil!")
            else:
                print("Sesi tidak valid atau HWID berubah. Silakan login ulang.")
                if os.path.exists(auth.SESSION_FILE):
                    os.remove(auth.SESSION_FILE)
                os.system("pause") if sys.platform.startswith('win') else input()
                sys.exit()
        except json.JSONDecodeError:
            print("File sesi rusak. Mengatur ulang sesi...")
            os.remove(auth.SESSION_FILE)
            auto_login_failed = True
    else:
        auto_login_failed = True

    if not os.path.exists(auth.SESSION_FILE) or 'auto_login_failed' in locals():
        print("==================================================")
        print("        BOT CKG SEKOLAH BELUM PEMERIKSAAN        ")
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
    import time

    nama_file = 'data.xlsx'
    file_log_xlsx = 'rekap-belum-pemeriksaan.xlsx'

    try:
        df = pd.read_excel(nama_file)
        df['Sekolah'] = df['Sekolah'].astype(str).str.strip()
        df['Nama'] = df['Nama'].astype(str).str.strip()
        df['kelas'] = df['kelas'].astype(str).str.strip()
        df['NIK'] = df['NIK'].astype(str).str.replace('.0', '', regex=False).str.strip()
    except Exception as e:
        print(f"Gagal membaca file {nama_file}")
        return

    print(f"Berhasil membaca {len(df)} data dari spreadsheet.")
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

    total_proses = (baris_akhir - baris_awal) + 1
    sukses_count = 0
    gagal_count = 0

    options = webdriver.ChromeOptions()
    sistem_os = platform.system().lower()

    if "windows" in sistem_os:
        user_profile = os.environ.get("USERPROFILE")
        path_profile = os.path.join(user_profile, "AppData", "Local", "Google", "Chrome", "User Data", "BotKemenkesProfile")
        options.add_argument(f"--user-data-dir={path_profile}")
        options.add_argument("--remote-debugging-port=9222")
    else:
        path_profile = os.path.abspath("./ChromeProfile")
        options.add_argument(f"--user-data-dir={path_profile}")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-gpu-rasterization")
    options.add_argument("--disable-extensions")
    options.add_argument("--mute-audio")
    options.add_argument("--log-level=3")

    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
    except Exception as e:
        print("Gagal membuka Google Chrome")
        if "windows" in sistem_os:
            print("SOLUSI: Jalankan 'taskkill /f /im chrome.exe' di CMD lalu coba lagi.")
        else:
            print("SOLUSI: Tutup semua jendela Google Chrome yang aktif lalu coba lagi.")
        return

    def tunggu_halaman_siap(timeout=10):
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except:
            pass

    def klik_cepat(driver, wait, xpath):
        el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        time.sleep(0.1)
        driver.execute_script("arguments[0].click();", el)
        return el

    def isi_field_cepat(wait, xpath, nilai):
        field = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        field.clear()
        field.send_keys(str(nilai))
        return field

    try:
        driver.get("https://sehatindonesiaku.kemkes.go.id/auth/login")
        print("\n--- DETEKSI LOGIN ---")
        print("Jika ini pertama kali, silakan login manual pada browser.")
        print("Pastikan Anda sudah stand-by di halaman utama, lalu tekan ENTER di Terminal...")
        input()

        wait = WebDriverWait(driver, 10)
        short_wait = WebDriverWait(driver, 3)

        try:
            tunggu_halaman_siap()
            try:
                short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
            except Exception:
                pass

            ckg_sekolah = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='CKG Sekolah']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ckg_sekolah)
            time.sleep(0.2)
            ckg_sekolah.click()
            time.sleep(1.5)

            pelayanan = wait.until(EC.element_to_be_clickable((By.ID, "menu_pelayanan")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pelayanan)
            time.sleep(0.2)
            pelayanan.click()
            time.sleep(1.5)

        except Exception as e:
            print("Gagal membuka menu navigasi awal")
            driver.quit()
            return

        for index, row in df.iloc[baris_awal-1:baris_akhir].iterrows():
            nama_sekarang = row['Nama']
            sekolah_sekarang = row['Sekolah']
            kelas_sekarang = row['kelas']
            nik_sekarang = row['NIK']
            print(f"\n[{index+1}/{len(df)}] Memproses NIK: {nik_sekarang}")

            try:
                tunggu_halaman_siap()
                
                klik_cepat(driver, wait, "//span[contains(text(), 'Pilih sekolah')]")
                time.sleep(0.5)

                isi_field_cepat(wait, "//input[@id='sekolah']", sekolah_sekarang)
                time.sleep(1.5)

                opsi_sekolah = wait.until(EC.presence_of_element_located((
                    By.XPATH, f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{sekolah_sekarang}') or translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')=translate('{sekolah_sekarang}', 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')]"
                )))
                driver.execute_script("arguments[0].click();", opsi_sekolah)
                time.sleep(0.5)

                klik_cepat(driver, wait, "//span[contains(text(), 'Pilih kelas')]")
                time.sleep(0.5)

                opsi_kelas = wait.until(EC.presence_of_element_located((
                    By.XPATH, f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{kelas_sekarang}')]"
                )))
                driver.execute_script("arguments[0].click();", opsi_kelas)
                time.sleep(0.5)

                klik_cepat(driver, wait, "//button[contains(@class, 'btn-outline-primary')]//div[contains(text(), 'Tampilkan Pencarian')]")
                time.sleep(0.8)

                klik_cepat(driver, wait, "//span[contains(text(), 'Nomor Tiket')]")
                time.sleep(0.4)

                klik_cepat(driver, wait, "//div[contains(@class, 'hover:bg-gray-1')]//div[text()='NIK']")
                time.sleep(0.4)

                input_nik_field = wait.until(EC.presence_of_element_located((By.ID, "nik")))
                input_nik_field.clear()
                input_nik_field.send_keys(nik_sekarang)
                time.sleep(0.3)
                input_nik_field.send_keys(Keys.ENTER)
                time.sleep(1.5)

                alert_status_lain = driver.find_elements(By.XPATH, "//div[contains(text(), 'Cek data di status pemeriksaan lain')]")
                if len(alert_status_lain) > 0 and alert_status_lain[0].is_displayed():
                    print("Terdeteksi status pemeriksaan lain. Skip data ini...")
                    catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="-", sekolah=sekolah_sekarang, kelas=kelas_sekarang, file_target=file_log_xlsx)
                    driver.refresh()
                    time.sleep(1.5)
                    gagal_count += 1
                    continue

                klik_cepat(driver, wait, "//button[contains(@class, 'btn-outline-primary')]//div[contains(text(), 'Mulai')]")
                time.sleep(0.8)

                klik_cepat(driver, wait, "//button[contains(@class, 'btn-fill-primary')]//div[contains(text(), 'Mulai Pemeriksaan')]")
                time.sleep(0.8)

                klik_cepat(driver, wait, "//button[contains(@class, 'btn-fill-primary')]//div[contains(text(), 'Simpan')]")
                time.sleep(1.2) 

                catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="Berhasil mulai pemeriksaan", sekolah=sekolah_sekarang, kelas=kelas_sekarang, file_target=file_log_xlsx)

                driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pelayanan-sekolah")
                try:
                    short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
                except Exception:
                    pass
                time.sleep(0.5)

                sukses_count += 1
                print("Selesai input data!")

            except Exception as e:
                print("Gagal memproses data ini")
                catat_ke_excel_rekap(nik=nik_sekarang, status="Gagal / Terjadi Error", sekolah=sekolah_sekarang, kelas=kelas_sekarang, file_target=file_log_xlsx)
                gagal_count += 1
                driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pelayanan-sekolah")
                time.sleep(1.5)
                continue

        print("\n==================================================")
        print("      SEMUA DATA DALAM RENTANG SELESAI PROSES    ")
        print("==================================================")
        print(f" Total Target Data : {total_proses} data")
        print(f" Berhasil Diproses : {sukses_count} data")
        print(f" Gagal/Dilewati    : {gagal_count} data")
        print("==================================================")

    except Exception as main_err:
        print(f"Terjadi error tak terduga saat bot berjalan: {main_err}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        jalankan_bot()
    except Exception as e:
        print("\n CRITICAL ERROR ")
    finally:
        print("\n==================================================")
        print("BOT BERHENTI. Jendela ditahan agar Anda bisa copy errornya.")
        if sys.platform.startswith('win'):
            os.system("pause")
        else:
            input()