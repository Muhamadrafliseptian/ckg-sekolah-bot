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

    if not os.path.exists(auth.SESSION_FILE) or 'auto_login_failed' in locals():
        print("==================================================")
        print("             BOT CKG SEKOLAH SELESAI PEMERIKSAAN               ")
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
    # Menghapus duplikasi jalankan_bot() di sini agar tidak berjalan dua kali
    import time
    import platform
    from selenium.common.exceptions import TimeoutException
    
    nama_file = 'data.xlsx' 
    file_log_rekap = 'rekap-posisi-pemeriksaan.txt'  

    try:
        df = pd.read_excel(nama_file)
        df['Sekolah'] = df['Sekolah'].astype(str)
        df['kelas'] = df['kelas'].astype(str)
        df['NIK'] = df['NIK'].astype(str).str.replace('.0', '', regex=False)
        df['Jenis Kelamin'] = df['Jenis Kelamin'].astype(str).str.strip()
    except Exception as e:
        print(f" ❌ Gagal membaca file {nama_file}. Error: {e}")
        return

    print(f"✅ Berhasil membaca {len(df)} data dari spreadsheet.")
    print("\n--- PENGATURAN DATA MULTI-TAB CHECKER ---")
    try:
        baris_awal = int(input(f"Masukkan nomor baris awal (1 - {len(df)}): "))
        baris_akhir = int(input(f"Masukkan nomor baris akhir ({baris_awal} - {len(df)}): "))
        if baris_awal < 1 or baris_akhir > len(df) or baris_awal > baris_akhir:
            print(" ❌ Rentang baris data tidak valid! Program dihentikan.")
            return
    except ValueError:
        print(" ❌ Input harus berupa angka! Program dihentikan.")
        return

    total_proses = (baris_akhir - baris_awal) + 1
    count_belum = 0
    count_sedang = 0
    count_selesai = 0
    count_tidak_ada = 0
    gagal_system_count = 0

    with open(file_log_rekap, 'w') as f:
        f.write("=== REKAP POSISI STATUS PEMERIKSAAN NIK ===\n")

    print("🔄 Sedang mencoba membuka Google Chrome...")
    
    # ================= CROSS-PLATFORM CHROME CONFIGURATION =================
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
        print(f" ❌ Gagal membuka Google Chrome. Error: {e}")
        return

    # ================= FUNGSI NAVIGASI SMOOTH & AMAN =================
    def klik_aman_smooth(selector_xpath, waktu_tunggu=4.0):
        """Menunggu elemen stabil, scroll dengan smooth, beri jeda mikro, lalu klik"""
        try:
            elemen = WebDriverWait(driver, waktu_tunggu).until(
                EC.element_to_be_clickable((By.XPATH, selector_xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elemen)
            time.sleep(0.3) 
            elemen.click()
            return True
        except Exception:
            return False

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
            
            klik_aman_smooth("//span[text()='CKG Sekolah']")
            time.sleep(0.4)
            klik_aman_smooth("//*[@id='menu_pelayanan']")
            time.sleep(0.8) 
        except Exception as e:
            print(f" ❌ Gagal membuka menu navigasi awal. Error: {e}")
            driver.quit()
            return

        # ================= LOOPING UTAMA DATA AUDIT =================
        for index, row in df.iloc[baris_awal-1:baris_akhir].iterrows():
            sekolah_sekarang = row['Sekolah']
            kelas_sekarang = row['kelas'] 
            nik_sekarang = row['NIK']
            jk_sekarang = row['Jenis Kelamin']
                
            print(f"\n🔍 [{index+1}/{len(df)}] Menelusuri NIK: {nik_sekarang}")
            
            try:
                klik_aman_smooth("//span[contains(text(), 'Pilih sekolah')]")
                
                input_sekolah = wait.until(EC.presence_of_element_located((By.ID, "sekolah")))
                input_sekolah.clear()
                input_sekolah.send_keys(sekolah_sekarang)
                time.sleep(0.4)
                
                klik_aman_smooth(f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{sekolah_sekarang}') or translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')=translate('{sekolah_sekarang}', 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')]")
                time.sleep(0.4)
                
                klik_aman_smooth("//span[contains(text(), 'Pilih kelas')]")
                time.sleep(0.3)
                
                klik_aman_smooth(f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{kelas_sekarang}')]")
                time.sleep(0.4)
                
                klik_aman_smooth("//button[contains(@class, 'btn-outline-primary')]//div[contains(text(), 'Tampilkan Pencarian')]")
                time.sleep(0.4)
                
                klik_aman_smooth("//span[contains(text(), 'Nomor Tiket')]")
                time.sleep(0.3)
                
                klik_aman_smooth("//div[contains(@class, 'hover:bg-gray-1')]//div[text()='NIK']")
                time.sleep(0.3)
                
                input_nik_field = wait.until(EC.presence_of_element_located((By.ID, "nik")))
                input_nik_field.clear()
                input_nik_field.send_keys(nik_sekarang)
                input_nik_field.send_keys(Keys.ENTER)
                time.sleep(0.8)
                
                status_ditemukan = "Tidak Ditemukan"
                quick_check = WebDriverWait(driver, 1.5)

                # --- 1. CEK TAB BELUM PEMERIKSAAN ---
                if klik_aman_smooth("//div[contains(@class, 'cursor-pointer') and contains(text(), 'Belum Pemeriksaan')]", waktu_tunggu=2.0):
                    time.sleep(0.4) 
                    try:
                        badge_belum = quick_check.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Belum Pemeriksaan')]/span")))
                        if badge_belum.text.strip() and int(badge_belum.text.strip()) > 0:
                            status_ditemukan = "Belum Pemeriksaan"
                    except Exception:
                        pass

                # --- 2. CEK TAB SEDANG PEMERIKSAAN ---
                if status_ditemukan == "Tidak Ditemukan":
                    if klik_aman_smooth("//div[contains(@class, 'cursor-pointer') and contains(text(), 'Sedang Pemeriksaan')]", waktu_tunggu=2.0):
                        time.sleep(0.4)
                        try:
                            badge_sedang = quick_check.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Sedang Pemeriksaan')]/span")))
                            if badge_sedang.text.strip() and int(badge_sedang.text.strip()) > 0:
                                status_ditemukan = "Sedang Pemeriksaan"
                        except Exception:
                            pass

                # --- 3. CEK TAB SELESAI PEMERIKSAAN ---
                if status_ditemukan == "Tidak Ditemukan":
                    if klik_aman_smooth("//div[contains(@class, 'cursor-pointer') and contains(text(), 'Selesai Pemeriksaan')]", waktu_tunggu=2.0):
                        time.sleep(0.4)
                        try:
                            badge_selesai = quick_check.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Selesai Pemeriksaan')]/span")))
                            if badge_selesai.text.strip() and int(badge_selesai.text.strip()) > 0:
                                status_ditemukan = "Selesai Pemeriksaan"
                        except Exception:
                            pass

                # Rekapitulasi status baris data saat ini
                if status_ditemukan == "Belum Pemeriksaan":
                    print(f"   STATUS -> [Belum Pemeriksaan]")
                    count_belum += 1
                elif status_ditemukan == "Sedang Pemeriksaan":
                    print(f"   STATUS -> [Sedang Pemeriksaan]")
                    count_sedang += 1
                elif status_ditemukan == "Selesai Pemeriksaan":
                    print(f"   STATUS -> [Selesai Pemeriksaan]")
                    count_selesai += 1
                else:
                    status_ditemukan = "Belum Daftar / Konfirmasi Hadir"
                    print(f"   STATUS -> [{status_ditemukan}]")
                    count_tidak_ada += 1

                with open(file_log_rekap, 'a') as f:
                    f.write(f"NIK: {nik_sekarang} | Posisi: {status_ditemukan} | Sekolah: {sekolah_sekarang} ({kelas_sekarang})\n")

                driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pelayanan-sekolah")
                time.sleep(0.8)
                    
            except Exception as e:
                print(f" ❌ Terjadi gangguan saat memproses NIK {nik_sekarang}. Me-refresh halaman...")
                gagal_system_count += 1
                try:
                    driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pelayanan-sekolah")
                    time.sleep(1.5)
                except:
                    pass
                driver.refresh()
                time.sleep(2.0)
                continue
               
    except Exception as main_err:
        print(f"⚠️ Terjadi interupsi sistem: {main_err}")
        
    print("\n==================================================")
    print("         HASIL AUDIT MULTI-TAB SELESAI            ")
    print("==================================================")
    print(f" Total Target Dicek   : {total_proses} data")
    print(f" Belum Pemeriksaan : {count_belum} data")
    print(f" Sedang Pemeriksaan: {count_sedang} data")
    print(f" Selesai Pemeriksaan: {count_selesai} data")
    print(f" Tidak Ditemukan   : {count_tidak_ada} data")
    print(f" Gagal Scan (Error): {gagal_system_count} data")
    print(f" Hasil lengkap disimpan di: {file_log_rekap}")
    print("==================================================")

    print("\nGoogle Chrome ditahan agar tetap terbuka.")
    print("Tekan CTRL+C di Terminal/Prompt ini jika kamu ingin menutup program dan browser...")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nChecker dimatikan oleh pengguna. Menutup browser...")
            try:
                driver.quit()
            except:
                pass
            break

if __name__ == "__main__":
    try:
        # Jalankan alur login secara tunggal di awal
        jalankan_bot()
        # Jika login sukses, langsung alihkan ke fungsi utama pengolah data
        main()
    except Exception as e:
        print(f"Terjadi error fatal pada eksekusi runtime: {e}")
    finally:
        print("\n==================================================")
        print("PROGRAM SELESAI BERJALAN.")
        if sys.platform.startswith('win'):
            os.system("pause")
        else:
            print("Tekan ENTER untuk menutup jendela ini...")
            input()