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
    import time

def get_password_hidden(prompt="Masukkan Password        : "):
    """Membaca input password secara aman tanpa menampilkan karakter di terminal"""
    password = getpass.getpass(prompt=prompt)
    return password

def jalankan_bot():
    current_hwid = auth.get_hwid()
    if os.path.exists(auth.SESSION_FILE):
        with open(auth.SESSION_FILE, "r") as f:
            sesi = json.load(f)
        if auth.check_auto_login(sesi.get("local_id"), current_hwid):
            print(" Sesi valid. Login otomatis berhasil!")
        else:
            print("Sesi tidak valid atau HWID berubah. Silakan login ulang.")
            if os.path.exists(auth.SESSION_FILE):
                os.remove(auth.SESSION_FILE)
            os.system("pause")
            sys.exit()
    else:
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
    try:
        df = pd.read_excel(nama_file)
        df['Sekolah'] = df['Sekolah'].astype(str)
        df['kelas'] = df['kelas'].astype(str)
        df['NIK'] = df['NIK'].astype(str).str.replace('.0', '', regex=False)
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

    options = webdriver.ChromeOptions()

    user_profile = os.environ.get("USERPROFILE")
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
        print("\n💡 SOLUSI: Jalankan 'taskkill /f /im chrome.exe' di CMD lalu coba lagi.")
        return

    def klik_cepat(driver, wait, xpath):
        """Klik via JavaScript tanpa nunggu animasi scroll"""
        el = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].click();", el)
        return el

    def isi_field_cepat(wait, xpath, nilai):
        """Isi field input"""
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

        wait = WebDriverWait(driver, 3)
        short_wait = WebDriverWait(driver, 3)

        try:
            try:
                short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
            except Exception:
                pass

            ckg_sekolah = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='CKG Sekolah']")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ckg_sekolah)
            ckg_sekolah.click()
            time.sleep(2.5)

            pelayanan = wait.until(EC.element_to_be_clickable((By.ID, "menu_pelayanan")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pelayanan)
            pelayanan.click()
            time.sleep(2.5)

        except Exception as e:
            print(f" Gagal membuka menu navigasi awal")
            driver.quit()
            return

        for index, row in df.iloc[baris_awal-1:baris_akhir].iterrows():
            sekolah_sekarang = row['Sekolah']
            kelas_sekarang = row['kelas']
            nik_sekarang = row['NIK']
            print(f"\n[{index+1}/{len(df)}] Memproses NIK: {nik_sekarang}")

            try:
                klik_cepat(driver, wait, "//span[contains(text(), 'Pilih sekolah')]")
                time.sleep(1.0)

                isi_field_cepat(wait, "//input[@id='sekolah']", sekolah_sekarang)
                time.sleep(2.5)

                opsi_sekolah = wait.until(EC.presence_of_element_located((
                    By.XPATH, f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{sekolah_sekarang}') or translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')=translate('{sekolah_sekarang}', 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')]"
                )))
                driver.execute_script("arguments[0].click();", opsi_sekolah)
                time.sleep(1.5)

                klik_cepat(driver, wait, "//span[contains(text(), 'Pilih kelas')]")
                time.sleep(1.0)

                opsi_kelas = wait.until(EC.presence_of_element_located((
                    By.XPATH, f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{kelas_sekarang}')]"
                )))
                driver.execute_script("arguments[0].click();", opsi_kelas)
                time.sleep(1.5)

                klik_cepat(driver, wait, "//button[contains(@class, 'btn-outline-primary')]//div[contains(text(), 'Tampilkan Pencarian')]")
                time.sleep(1.5)

                klik_cepat(driver, wait, "//span[contains(text(), 'Nomor Tiket')]")
                time.sleep(1.0)

                klik_cepat(driver, wait, "//div[contains(@class, 'hover:bg-gray-1')]//div[text()='NIK']")
                time.sleep(1.0)

                input_nik_field = wait.until(EC.presence_of_element_located((By.ID, "nik")))
                input_nik_field.clear()
                input_nik_field.send_keys(nik_sekarang)
                time.sleep(0.8)
                input_nik_field.send_keys(Keys.ENTER)
                time.sleep(2.5)

                alert_status_lain = driver.find_elements(By.XPATH, "//div[contains(text(), 'Cek data di status pemeriksaan lain')]")
                if len(alert_status_lain) > 0 and alert_status_lain[0].is_displayed():
                    print("   [ALERT] Terdeteksi status pemeriksaan lain. Skip data ini...")
                    driver.refresh()
                    time.sleep(2.5)
                    gagal_count += 1
                    continue

                klik_cepat(driver, wait, "//button[contains(@class, 'btn-outline-primary')]//div[contains(text(), 'Mulai')]")
                time.sleep(1.5)

                klik_cepat(driver, wait, "//button[contains(@class, 'btn-fill-primary')]//div[contains(text(), 'Mulai Pemeriksaan')]")
                time.sleep(1.5)

                klik_cepat(driver, wait, "//button[contains(@class, 'btn-fill-primary')]//div[contains(text(), 'Simpan')]")
                time.sleep(2.0) 

                driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pelayanan-sekolah")
                try:
                    short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
                except Exception:
                    pass
                time.sleep(1.5)

                sukses_count += 1
                print("    Selesai input data!")

            except Exception as e:
                print(f"    Gagal memproses data ini")
                gagal_count += 1
                driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pelayanan-sekolah")
                time.sleep(2.5)
                continue

        print("\n==================================================")
        print("      SEMUA DATA DALAM RENTANG SELESAI PROSES    ")
        print("==================================================")
        print(f" Total Target Data : {total_proses} data")
        print(f" Berhasil Diproses : {sukses_count} data")
        print(f" Gagal/Dilewati    : {gagal_count} data")
        print("==================================================")

    except Exception as main_err:
        print(f" Terjadi error tak terduga saat bot berjalan: {main_err}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        jalankan_bot()
    except Exception as e:
        print(f"\n CRITICAL ERROR ")
    finally:
        print("\n==================================================")
        print("BOT BERHENTI. Jendela ditahan agar Anda bisa copy errornya.")
        os.system("pause")