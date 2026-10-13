#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GXCF - Multi Tool
Author: DreZainZorLuiston
"""

import os
import sys
import time
import random
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    from pyfiglet import Figlet
except ImportError:
    os.system("pip install pyfiglet --quiet")
    from pyfiglet import Figlet

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama --quiet")
    from colorama import Fore, Style, init
    init(autoreset=True)


# ==================== ASCII BANNER ====================
def banner():
    os.system("cls" if os.name == "nt" else "clear")
    f = Figlet(font="slant")
    art = f.renderText("GXCF")
    print(Fore.CYAN + art)
    print(Fore.MAGENTA + "        === GXCF Multi Tool ===")
    print(Fore.YELLOW + "        Author : DreZainZorLuiston")
    print(Fore.YELLOW + "        Version: 1.0")
    print(Fore.RED + "        [!] Use for educational purposes only\n")


# ==================== MENU ====================
def menu():
    print(Fore.GREEN + "=" * 45)
    print(Fore.CYAN + " [1] Spam OTP")
    print(Fore.CYAN + " [2] Phone Lookup")
    print(Fore.CYAN + " [3] Email Lookup")
    print(Fore.RED + " [0] Exit")
    print(Fore.GREEN + "=" * 45)


# ==================== SPAM OTP ====================
# Daftar endpoint OTP publik (buat testing).
# Ini cuma contoh endpoint; lu bisa nambahin sendiri.
OTP_ENDPOINTS = [
    {
        "name": "Service-A",
        "url": "https://api.example-otp1.com/v1/send",
        "method": "POST",
        "data": lambda phone: {"phone": phone, "type": "sms"},
        "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    },
    {
        "name": "Service-B",
        "url": "https://api.example-otp2.com/otp/request",
        "method": "POST",
        "data": lambda phone: {"msisdn": phone, "service": "register"},
        "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    },
    {
        "name": "Service-C",
        "url": "https://api.example-otp3.com/auth/send-otp",
        "method": "POST",
        "data": lambda phone: {"mobile": phone},
        "headers": {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    },
]


def send_otp(endpoint, phone, timeout=8):
    try:
        payload = endpoint["data"](phone)
        r = requests.request(
            endpoint["method"],
            endpoint["url"],
            json=payload,
            headers=endpoint["headers"],
            timeout=timeout,
        )
        status = r.status_code
        ok = 200 <= status < 300
        tag = Fore.GREEN + "[+]" if ok else Fore.RED + "[-]"
        print(f"{tag} {endpoint['name']:<12} | {phone} | HTTP {status}")
        return ok
    except requests.exceptions.Timeout:
        print(Fore.YELLOW + f"[!] {endpoint['name']:<12} | {phone} | TIMEOUT")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] {endpoint['name']:<12} | {phone} | ERR: {type(e).__name__}")
    return False


def spam_otp():
    print(Fore.CYAN + "\n=== SPAM OTP ===")
    phone = input(Fore.YELLOW + "[?] Masukkan nomor target (contoh: 628123456789): ").strip()
    if not phone:
        print(Fore.RED + "[!] Nomor kosong.")
        return

    try:
        loops = int(input(Fore.YELLOW + "[?] Berapa kali loop per service? (default 5): ").strip() or "5")
    except ValueError:
        loops = 5

    try:
        threads = int(input(Fore.YELLOW + "[?] Threads (default 5): ").strip() or "5")
    except ValueError:
        threads = 5

    print(Fore.MAGENTA + f"\n[*] Target  : {phone}")
    print(Fore.MAGENTA + f"[*] Loops   : {loops}")
    print(Fore.MAGENTA + f"[*] Threads : {threads}\n")

    tasks = []
    for _ in range(loops):
        for ep in OTP_ENDPOINTS:
            tasks.append((ep, phone))

    random.shuffle(tasks)

    success = 0
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(send_otp, ep, ph) for ep, ph in tasks]
        for f in futures:
            if f.result():
                success += 1

    print(Fore.GREEN + f"\n[✓] Selesai. Total request: {len(tasks)} | Sukses: {success}")


# ==================== PHONE LOOKUP ====================
def phone_lookup():
    print(Fore.CYAN + "\n=== PHONE LOOKUP ===")
    phone = input(Fore.YELLOW + "[?] Masukkan nomor (contoh: 628123456789): ").strip()
    if not phone:
        print(Fore.RED + "[!] Nomor kosong.")
        return

    # Lookup sederhana via API publik numverify-like (free tier) & fallback lokal
    print(Fore.MAGENTA + f"\n[*] Mencari info untuk: {phone}\n")

    # 1. Cek format & info dasar
    digits = "".join(filter(str.isdigit, phone))
    info = {
        "Input": phone,
        "Digits": digits,
        "Length": len(digits),
    }

    # 2. Deteksi negara (kode umum)
    country_map = {
        "62": "Indonesia 🇮🇩",
        "60": "Malaysia 🇲🇾",
        "65": "Singapore 🇸🇬",
        "66": "Thailand 🇹🇭",
        "84": "Vietnam 🇻🇳",
        "63": "Philippines 🇵🇭",
        "81": "Japan 🇯🇵",
        "82": "South Korea 🇰🇷",
        "86": "China 🇨🇳",
        "91": "India 🇮🇳",
        "1":  "USA/Canada 🇺🇸",
        "44": "UK 🇬🇧",
        "49": "Germany 🇩🇪",
    }

    cc = None
    for code in sorted(country_map.keys(), key=len, reverse=True):
        if digits.startswith(code):
            cc = code
            break

    info["Country"] = country_map.get(cc, "Unknown")
    info["CountryCode"] = cc or "N/A"

    # 3. Deteksi operator (khusus ID, prefix 4 digit)
    id_ops = {
        "0811": "Telkomsel", "0812": "Telkomsel", "0813": "Telkomsel",
        "0821": "Telkomsel", "0822": "Telkomsel", "0823": "Telkomsel",
        "0851": "Telkomsel", "0852": "Telkomsel", "0853": "Telkomsel",
        "0814": "Indosat", "0815": "Indosat", "0816": "Indosat",
        "0855": "Indosat", "0856": "Indosat", "0857": "Indosat",
        "0858": "Indosat",
        "0817": "XL", "0818": "XL", "0819": "XL",
        "0859": "XL", "0877": "XL", "0878": "XL",
        "0831": "AXIS", "0832": "AXIS", "0833": "AXIS", "0838": "AXIS",
        "0895": "Tri", "0896": "Tri", "0897": "Tri", "0898": "Tri", "0899": "Tri",
        "0881": "Smartfren", "0882": "Smartfren", "0883": "Smartfren",
        "0884": "Smartfren", "0885": "Smartfren", "0886": "Smartfren",
        "0887": "Smartfren", "0888": "Smartfren", "0889": "Smartfren",
    }

    local = digits
    if local.startswith("62"):
        local = "0" + local[2:]

    prefix = local[:4]
    info["Operator"] = id_ops.get(prefix, "Unknown")
    info["LocalFormat"] = local
    info["IntlFormat"] = "+" + digits

    # 4. Lookup via API publik (opsional, butuh API key biasanya)
    # Contoh: https://apilayer.net/api/validate?access_key=KEY&number=...
    # Skip by default biar gak error tanpa key.

    print(Fore.GREEN + "=" * 50)
    for k, v in info.items():
        print(Fore.CYAN + f" {k:<14}: " + Fore.WHITE + f"{v}")
    print(Fore.GREEN + "=" * 50)
    print(Fore.YELLOW + "\n[i] Info tambahan seperti nama pemilik & alamat perlu API berbayar (Numverify, Twilio Lookup, dll).")


# ==================== EMAIL LOOKUP ====================
def email_lookup():
    print(Fore.CYAN + "\n=== EMAIL LOOKUP ===")
    email = input(Fore.YELLOW + "[?] Masukkan email: ").strip()
    if not email or "@" not in email:
        print(Fore.RED + "[!] Email tidak valid.")
        return

    print(Fore.MAGENTA + f"\n[*] Mencari info untuk: {email}\n")

    local, domain = email.split("@", 1)
    info = {
        "Email": email,
        "Local": local,
        "Domain": domain,
        "DomainLower": domain.lower(),
    }

    # 1. MX Record check (pake DNS publik via socket + dnspython opsional)
    try:
        import dns.resolver
        has_dns = True
    except ImportError:
        has_dns = False
        os.system("pip install dnspython --quiet")
        try:
            import dns.resolver
            has_dns = True
        except ImportError:
            has_dns = False

    mx_records = []
    if has_dns:
        try:
            answers = dns.resolver.resolve(domain, "MX")
            for r in answers:
                mx_records.append(f"{r.preference} {r.exchange}")
        except Exception:
            mx_records = []

    info["MXRecords"] = mx_records if mx_records else "None / Not Found"

    # 2. Known provider check
    providers = {
        "gmail.com": "Google Gmail",
        "yahoo.com": "Yahoo Mail",
        "outlook.com": "Microsoft Outlook",
        "hotmail.com": "Microsoft Hotmail",
        "protonmail.com": "ProtonMail",
        "proton.me": "ProtonMail",
        "icloud.com": "Apple iCloud",
        "mail.com": "Mail.com",
        "yandex.com": "Yandex Mail",
        "zoho.com": "Zoho Mail",
    }
    info["Provider"] = providers.get(domain.lower(), "Unknown / Custom")

    # 3. Gravatar check (pake MD5 email)
    import hashlib
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    gravatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
    try:
        r = requests.get(gravatar_url, timeout=6)
        info["Gravatar"] = "Registered ✓" if r.status_code == 200 else "Not found"
    except Exception:
        info["Gravatar"] = "Check failed"

    info["GravatarURL"] = f"https://www.gravatar.com/avatar/{email_hash}"

    # 4. HaveIBeenPwned check (butuh API key, jadi skip)
    info["BreachCheck"] = "Butuh API key (haveibeenpwned.com/API)"

    print(Fore.GREEN + "=" * 50)
    for k, v in info.items():
        if isinstance(v, list):
            print(Fore.CYAN + f" {k:<14}: " + Fore.WHITE + f"{len(v)} record(s)")
            for rec in v:
                print(Fore.WHITE + f"                  - {rec}")
        else:
            print(Fore.CYAN + f" {k:<14}: " + Fore.WHITE + f"{v}")
    print(Fore.GREEN + "=" * 50)


# ==================== MAIN ====================
def main():
    while True:
        banner()
        menu()
        choice = input(Fore.YELLOW + "\n[GXCF] Pilih menu > ").strip()

        if choice == "1":
            spam_otp()
        elif choice == "2":
            phone_lookup()
        elif choice == "3":
            email_lookup()
        elif choice == "0":
            print(Fore.RED + "\n[!] Keluar... bye bos.")
            sys.exit(0)
        else:
            print(Fore.RED + "[!] Pilihan tidak valid.")

        input(Fore.YELLOW + "\n[i] Tekan ENTER untuk lanjut...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Interrupted. Bye.")
        sys.exit(0)
