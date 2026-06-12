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

def catat_ke_excel_rekap(nama, nik, status, sekolah, kelas, file_target="rekap-konfirmasi-hadir.xlsx"):
    """Mencatat log hasil konfirmasi hadir ke file Excel secara real-time"""
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
        print(f"   ⚠️ Gagal mencatat rekap Excel: {e}")

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

    nama_file = 'data.xlsx' 
    file_log_xlsx = 'rekap-konfirmasi-hadir.xlsx'

    try:
        df = pd.read_excel(nama_file)
        df['Sekolah'] = df['Sekolah'].astype(str).str.strip()
        df['Nama'] = df['Nama'].astype(str).str.strip()
        df['kelas'] = df['kelas'].astype(str).str.strip()
        df['NIK'] = df['NIK'].astype(str).str.replace('.0', '', regex=False).str.strip()
    except Exception as e:
        print(f" Gagal membaca file {nama_file}. Error: {e}")
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

    print("🔄 Sedang membuka Google Chrome dengan mode optimasi perangkat berat...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=./ChromeProfile") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-gpu-rasterization")
    options.add_argument("--disable-extensions")
    options.add_argument("--mute-audio")
    options.add_argument("--log-level=3")

    sistem_os = platform.system().lower()
    if "windows" in sistem_os:
        options.add_argument("--remote-debugging-port=9222")

    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
    except Exception as e:
        if "windows" in sistem_os:
            print("\n💡 SOLUSI WINDOWS: Jalankan 'taskkill /f /im chrome.exe' di CMD lalu coba lagi.")
        else:
            print("\n💡 SOLUSI MAC: Tutup semua jendela Google Chrome yang masih aktif, lalu coba lagi.")
        print(f"Error: {e}")
        return

    def tunggu_halaman_siap(timeout=10):
        """Membantu PC berat memastikan DOM web sudah selesai dirender secara internal"""
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except:
            pass

    def klik_aman_smooth(selector_xpath, waktu_tunggu=6.0):
        """Menunggu elemen stabil, scroll ke tengah agar tidak tertutup navbar, lalu klik"""
        try:
            elemen = WebDriverWait(driver, waktu_tunggu).until(
                EC.element_to_be_clickable((By.XPATH, selector_xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemen)
            time.sleep(0.3) 
            elemen.click()
            return True
        except:
            return False

    try:
        driver.get("https://sehatindonesiaku.kemkes.go.id/auth/login") 

        print("\n--- DETEKSI LOGIN ---")
        print("Jika ini pertama kali, silakan login manual pada browser.")
        print("Pastikan Anda sudah stand-by di halaman utama, lalu tekan ENTER di Terminal...")
        input()

        wait = WebDriverWait(driver, 10) 

        try:
            print("Menunggu loading overlay hilang...")
            tunggu_halaman_siap()
            try:
                short_wait = WebDriverWait(driver, 3)
                short_wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'fixed inset-0 bg-')]")))
            except Exception:
                pass
                
            klik_aman_smooth("//span[text()='CKG Sekolah']")
            print("-> Berhasil klik CKG Sekolah")
            time.sleep(0.4)
            
            klik_aman_smooth("//*[@id='menu_cari/daftarkan_individu']|//span[contains(text(), 'Cari/Daftarkan Individu')]")
            print("-> Berhasil klik Pelayanan / Cari Individu")
            time.sleep(0.8) 
            
        except Exception as e:
            print(f" Gagal inisialisasi menu awal. Error: {e}")
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
                
                wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Pilih sekolah')]")))
                klik_aman_smooth("//span[contains(text(), 'Pilih sekolah')]")
                
                input_sekolah = wait.until(EC.presence_of_element_located((By.ID, "sekolah")))
                input_sekolah.clear()
                time.sleep(0.2)
                input_sekolah.send_keys(sekolah_sekarang)
                time.sleep(0.8) 
                
                klik_aman_smooth(f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{sekolah_sekarang}') or translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')=translate('{sekolah_sekarang}', 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')]")
                time.sleep(0.3)
                
                klik_aman_smooth("//span[contains(text(), 'Pilih kelas')]")
                time.sleep(0.3)
                
                klik_aman_smooth(f"//div[contains(@class, 'hover:bg-gray-1')]//div[contains(text(), '{kelas_sekarang}')]")
                time.sleep(0.4)
                
                klik_aman_smooth("//span[contains(text(), 'Nomor Tiket')]")
                time.sleep(0.3)
                
                klik_aman_smooth("//div[contains(@class, 'hover:bg-gray-1')]//div[text()='NIK']")
                time.sleep(0.4)
                
                input_nik_field = wait.until(EC.presence_of_element_located((By.ID, "nik")))
                driver.execute_script("arguments[0].focus();", input_nik_field)
                input_nik_field.click()
                
                input_nik_field.send_keys(Keys.ENTER)
                time.sleep(0.3)
                
                input_nik_field.clear()
                time.sleep(0.2)
                input_nik_field.send_keys(nik_sekarang)
                time.sleep(0.3)
                input_nik_field.send_keys(Keys.ENTER)
                print("   Sistem sedang mencari data NIK...")
                
                try:
                    cek_hadir = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(@class, 'btn-fill-primary')]//div[contains(text(), 'Konfirmasi Hadir')]"
                    )))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cek_hadir)
                    time.sleep(0.3)
                    cek_hadir.click()
                    print("   [Kondisi] Data DITEMUKAN! Memproses persetujuan...")
                    
                    time.sleep(0.6) 
                    
                    checkbox_div = wait.until(EC.visibility_of_element_located((
                        By.XPATH, "//div[@id='verify' and contains(@class, 'check')]"
                    )))
                    driver.execute_script("arguments[0].click();", checkbox_div)
                    time.space = time.sleep(0.3)

                    tombol_hadir = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(@class, 'btn-fill-primary')]//div[text()='Hadir ']|//button[contains(@class, 'btn-fill-primary')]//div[normalize-space(text())='Hadir']"
                    )))
                    driver.execute_script("arguments[0].click();", tombol_hadir)
                    time.sleep(0.8)

                    tombol_tutup = wait.until(EC.element_to_be_clickable((
                        By.XPATH, "//button[contains(@class, 'btn-fill-primary')]//div[contains(text(), 'Tutup')]"
                    )))
                    driver.execute_script("arguments[0].click();", tombol_tutup)
                    print("   -> Berhasil melakukan Konfirmasi Hadir!")
                    
                    catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="Berhasil Konfirmasi Hadir", sekolah=sekolah_sekarang, kelas=kelas_sekarang, file_target=file_log_xlsx)
                    
                    driver.refresh()
                    time.sleep(1.0)
                        
                except Exception:
                    print("   [Kondisi] Data TIDAK ADA. Otomatis Lewati.")
                    catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="", sekolah=sekolah_sekarang, kelas=kelas_sekarang, file_target=file_log_xlsx)
                    
                    driver.refresh()
                    time.sleep(1.0)
                    continue
                
            except Exception as e:
                print(f"   ⚠️ Gagal memproses baris input ini")
                catat_ke_excel_rekap(nama=nama_sekarang, nik=nik_sekarang, status="Error Terhenti (System Lag)", sekolah=sekolah_sekarang, kelas=kelas_sekarang, file_target=file_log_xlsx)
                try:
                    driver.get("https://sehatindonesiaku.kemkes.go.id/ckg-pelayanan-sekolah")
                    time.sleep(1.5)
                except:
                    pass
                continue
               
        print(" Semua data dalam rentang target selesai diproses!")
        print(f" Excel rekap berhasil diupdate: {file_log_xlsx}")
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
        print(f"\n CRITICAL ERROR: {e}")
    finally:
        print("\n==================================================")
        print("BOT BERHENTI BERJALAN.")
        if sys.platform.startswith('win'):
            os.system("pause")
        else:
            print("Tekan ENTER untuk keluar dari terminal...")
            input()