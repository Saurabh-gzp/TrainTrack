# 🚆 TrainTrack — Indian Railways CLI

> **PNR Status · Live Train Status · Passenger Names · Seat Availability** — sab kuch apne terminal me, ek command se.

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Termux-green.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-None-red.svg)]()

Kya aap **IRCTC website** ya **app kholne** se pareshan ho? TrainTrack aapko **terminal se hi** saari train information deta hai — bina kisi app ke.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎫 **PNR Status** | Train, class, berth, fare, chart status — sab kuch |
| 👤 **Passenger Names** | Asli naam (chart ke baad full, pehle masked) |
| 🚄 **Live Train Status** | Train abhi kahan hai + har station ka delay |
| 🔀 **Trains Between Stations** | Dono stations ke beech saari trains |
| 💺 **Seat Availability** | Date + quota ke hisaab se availability |
| 📍 **Station Code Helper** | Common station codes |

---

## 🚀 Install (ek command)

### Linux / macOS / Termux / WSL — sab me same

```bash
curl -fsSL https://raw.githubusercontent.com/Saurabh-gzp/TrainTrack/main/install.sh | bash
```

Ya manual:

```bash
git clone https://github.com/Saurabh-gzp/TrainTrack.git
cd TrainTrack
python3 traintrack.py
```

> **Requirements:** Sirf **Python 3.6+** chahiye. Koi `pip install` nahi. Koi dependency nahi.

---

## 📖 Usage

```bash
python3 traintrack.py
```

### Menu
```
  1. PNR Status (+ Names)     ← sab ek saath (recommended)
  2. Live Train Status
  3. Trains Between Stations
  4. Seat Availability
  5. PNR Names (IRCTC - masked)
  6. Station Code Helper
  0. Exit
```

### Example — PNR Status
```
Option: 1
10-digit PNR number: 2954982721

  PNR Number        : 2954982721
  Train             : 15708 - ASR KIR EXPRESS
  Class             : 2A
  Booking Fare      : Rs.2015

  PASSENGER NAMES:
    #1: CHAxxxx xxxxx (age 33, Male) | CNF/A1/24/SU
```

### Example — Live Status
```
Option: 2
Train number: 15708
Journey date (YYYYMMDD): 20260814

  Train    : ASR KIR EXPRESS
  Status   : Departed Sabzi Mandi
  Location : lat=29.06, lon=77.01
```

---

## 📊 Data Sources

| Data | Source |
|------|--------|
| PNR + Live Status | `api.trackmytrain.co.in` |
| Passenger Names | `www.rr.irctctourism.com` |
| Seat/Berth | `www.ixigo.com` |
| Trains Between | `erail.in` |

---

## ❓ FAQ

**Q: Passenger name "CHAxxxx xxxxx" kyu dikh raha hai?**
A: Indian Railways **chart preparation se pehle** naam mask karta hai (privacy rule). Chart banne ke baad (~4 ghante pehle departure) **full name** dikhega. Ye har app me same hai.

**Q: Termux me chalega?**
A: Haan, 100%. Bas `pkg install python` karo phir install command chalao.

**Q: Koi API key chahiye?**
A: Nahi. Sab kuch ready hai.

**Q: Galat PNR pe kya hoga?**
A: "Invalid PNR" error dikhega. PNR 10 digits ka hona chahiye.

---

## 🛡️ Security / Privacy

- Tool **sirf public enquiry data** fetch karta hai
- **Koi login/password nahi** bhejta
- **Koi data store nahi** karta (stateless)

---

## 🤝 Contributing

PRs welcome! Issue open karo agar koi feature chahiye.

## 📜 License

[MIT](LICENSE) — free for everyone.

---

⭐ **Repo pasand aaya to star de do!** Star se aur logon ko milega.
