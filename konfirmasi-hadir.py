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
    """Membaca input password secara aman tanpa menampilkan karakter di terminal (Bisa Windows & Mac)"""
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
        print("         BOT CKG SEKOLAH KONFIRMASI HADIR         ")
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

    nama_file = 'data.csv' 

    try:
        df = pd.read_csv(nama_file)
        df['Sekolah'] = df['Sekolah'].astype(str)
        df['kelas'] = df['kelas'].astype(str)
        df['NIK'] = df['NIK'].astype(str).str.replace('.0', '', regex=False)
    except Exception as e:
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

    print("🔄 Sedang mencoba membuka Google Chrome...")
    
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
        print("\n💡 SOLUSI: Jalankan 'taskkill /f /im chrome.exe' di CMD lalu coba lagi.")
        return

    try:
        driver.get("https://sehatindonesiaku.kemkes.go.id/auth/login") 

        print("\n--- DETEKSI LOGIN ---")
        print("Jika ini pertama kali, silakan login manual pada browser.")
        print("Pastikan Anda sudah stand-by di halaman utama, lalu tekan ENTER di Terminal...")
        input()

        wait = WebDriverWait(driver, 5) 

        try:
            print("Menunggu loading overlay hilang...")
            try:
                short_wait = WebDriverWait(driver, 2)
                short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
            except Exception:
                pass
                
            time.sleep(0.5)
            
            ckg_sekolah = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='CKG Sekolah']")))
            driver.execute_script("arguments[0].scrollIntoView(true);", ckg_sekolah)
            time.sleep(0.5)
            ckg_sekolah.click()
            print("-> Berhasil klik CKG Sekolah")
            
            time.sleep(0.5)
            
            pelayanan = wait.until(EC.element_to_be_clickable((By.ID, "menu_cari/daftarkan_individu")))
            driver.execute_script("arguments[0].scrollIntoView(true);", pelayanan)
            time.sleep(0.5)
            pelayanan.click()
            print("-> Berhasil klik Pelayanan")
            time.sleep(1) 
            
        except Exception as e:
            driver.quit()
            return

        for index, row in df.iloc[baris_awal-1:baris_akhir].iterrows():
            sekolah_sekarang = row['Sekolah']
            kelas_sekarang = row['kelas'] 
            nik_sekarang = row['NIK']
            print(f"\n[{index+1}/{len(df)}] Memproses NIK: {nik_sekarang} ({sekolah_sekarang} - Kelas {kelas_sekarang})")
            
            try:
                print("Menunggu tombol Pilih Sekolah muncul...")
                pilih_sekolah = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Pilih sekolah')]")))
                driver.execute_script("arguments[0].scrollIntoView(true);", pilih_sekolah)
                time.sleep(0.5)
                pilih_sekolah.click()
                print("-> Berhasil klik Pilih Sekolah")
                
                time.sleep(0.5)
                
                print(f"Mengetikkan nama sekolah: {sekolah_sekarang}")
                input_sekolah = wait.until(EC.presence_of_element_located((By.ID, "sekolah")))
                input_sekolah.clear()
                time.sleep(0.5)
                input_sekolah.send_keys(sekolah_sekarang)
                print("Berhasil input nama sekolah ke dalam field.")
                print("Menunggu dropdown hasil pencarian muncul...")
                time.sleep(0.8) 
                
                opsi_sekolah = wait.until(EC.element_to_be_clickable((
                    By.XPATH, f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{sekolah_sekarang}') or translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')=translate('{sekolah_sekarang}', 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')]"
                )))
                driver.execute_script("arguments[0].scrollIntoView(true);", opsi_sekolah)
                time.sleep(0.5)
                opsi_sekolah.click()
                print(f"-> Berhasil otomatis klik: {sekolah_sekarang}")
                
                time.sleep(0.5) 
                
                print("Menunggu tombol Pilih Kelas muncul...")
                pilih_kelas = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Pilih kelas')]")))
                driver.execute_script("arguments[0].scrollIntoView(true);", pilih_kelas)
                time.sleep(0.5)
                pilih_kelas.click()
                print("-> Berhasil klik Pilih Kelas")
                
                time.sleep(0.5)
                
                opsi_kelas = wait.until(EC.element_to_be_clickable((
                    By.XPATH, f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{kelas_sekarang}')]"
                )))
                driver.execute_script("arguments[0].scrollIntoView(true);", opsi_kelas)
                time.sleep(0.5)
                opsi_kelas.click()
                print(f"-> Berhasil otomatis klik opsi kelas: Kelas {kelas_sekarang}")
                
                time.sleep(0.5)
                
                print("Mengubah tipe pencarian ke NIK...")
                dropdown_tipe = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Nomor Tiket')]")))
                dropdown_tipe.click()
                time.sleep(0.5)
                
                opsi_nik = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'hover:bg-gray-1')]//div[text()='NIK']")))
                opsi_nik.click()
                print("-> Berhasil ganti kategori menjadi NIK")
                
                time.sleep(0.8) 
                
                print("Mencari dan memfokuskan kursor ke field input NIK...")
                input_nik_field = wait.until(EC.presence_of_element_located((By.ID, "nik")))
                
                driver.execute_script("arguments[0].focus();", input_nik_field)
                input_nik_field.click()
                time.sleep(0.3)
                
                input_nik_field.send_keys(Keys.ENTER)
                print("-> Menekan ENTER Pertama...")
                time.sleep(0.5)
                
                print(f"Memasukkan NIK dari CSV: {nik_sekarang}")
                input_nik_field.clear()
                time.sleep(0.3)
                input_nik_field.send_keys(nik_sekarang)
                print("Berhasil mengisi NIK.")
                time.sleep(0.5)
                
                input_nik_field.send_keys(Keys.ENTER)
                print("-> Menekan ENTER Kedua (Mencari pasien...)")
                
                print("Memeriksa apakah data NIK ditemukan...")
                try:
                    cek_hadir = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(@class, 'btn-fill-primary')]//div[contains(text(), 'Konfirmasi Hadir')]"
                    )))
                    driver.execute_script("arguments[0].scrollIntoView(true);", cek_hadir)
                    time.sleep(0.5)
                    cek_hadir.click()
                    print("-> Data DITEMUKAN! Klik 'Konfirmasi Hadir'.")
                    
                    time.sleep(1.0) 
                    
                    print("Mencentang checkbox otomatis...")
                    checkbox_div = wait.until(EC.visibility_of_element_located((
                        By.XPATH, "//div[@id='verify' and contains(@class, 'check')]"
                    )))
                    driver.execute_script("arguments[0].click();", checkbox_div)
                    print("Checkbox berhasil dicentang otomatis.")
                    
                    time.sleep(0.3)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.5)

                    print("Mengklik tombol 'Hadir' secara otomatis...")
                    tombol_hadir = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(@class, 'btn-fill-primary')]//div[text()='Hadir ']|//button[contains(@class, 'btn-fill-primary')]//div[normalize-space(text())='Hadir']"
                    )))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol_hadir)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", tombol_hadir)
                    print("-> Berhasil klik 'Hadir' secara otomatis!")
                    time.sleep(1.0)

                    print("Mencari tombol 'Tutup'...")
                    tombol_tutup = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(@class, 'btn-fill-primary')]//div[contains(text(), 'Tutup')]"
                    )))
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol_tutup)
                    time.sleep(0.5)
                    
                    tombol_tutup.click()
                    print("-> Berhasil otomatis klik 'Tutup'!")
                    
                    print("Menyegarkan halaman (Refresh) agar form kembali bersih...")
                    driver.refresh()
                    time.sleep(1.0) 
                    
                    try:
                        short_wait = WebDriverWait(driver, 2)
                        short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
                    except Exception:
                        pass
                        
                except Exception as e:
                    print(f"Data TIDAK ADA / Terjadi kendala interaksi. Otomatis skip...")
                    print("Menyegarkan halaman darurat demi keamanan data...")
                    driver.refresh()
                    time.sleep(1.0)
                    continue
                
            except Exception as e:
                print(f" Gagal memproses baris input ini")
                print("Otomatis lanjut ke data baris berikutnya...")
                continue
               
        print("\n🎉 Semua data dalam rentang selesai diproses!")
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
        print(f"\n CRITICAL ERROR")
    finally:
        print("\n==================================================")
        print("BOT BERHENTI. Jendela ditahan agar Anda bisa copy errornya.")
        os.system("pause")