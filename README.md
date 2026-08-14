# 🚆 TrainTrack — Indian Railways CLI

> **PNR Status · Live Train Status · Passenger Names · Seat Availability** — all from your terminal, with a single command.

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Termux-green.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-None-red.svg)]()

Tired of opening the IRCTC website or a mobile app just to check your PNR or train status? TrainTrack gives you all the train information you need **right from your terminal** — no app required.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎫 **PNR Status** | Train, class, berth, fare, chart status — everything |
| 👤 **Passenger Names** | Real name (masked before chart, full after) |
| 🚄 **Live Train Status** | Current location + per-station delays |
| 🔀 **Trains Between Stations** | All trains between any two stations |
| 💺 **Seat Availability** | Availability by date and quota |
| 📍 **Station Code Helper** | Quick reference for common station codes |

---

## 🚀 Install (one command)

### Works on Linux / macOS / Termux / WSL — all the same

```bash
curl -fsSL https://raw.githubusercontent.com/Saurabh-gzp/TrainTrack/main/install.sh | bash
```

Or manually:

```bash
git clone https://github.com/Saurabh-gzp/TrainTrack.git
cd TrainTrack
python3 traintrack.py
```

> **Requirements:** Only **Python 3.6+**. No `pip install`. No dependencies.

---

## 📖 Usage

```bash
python3 traintrack.py
```

### Menu
```
  1. PNR Status (+ Names)     ← everything in one place (recommended)
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

**Q: Why does the passenger name show as "CHAxxxx xxxxx"?**
A: Indian Railways **masks the name before chart preparation** (privacy rule). Once the chart is prepared (~4 hours before departure), the **full name** is shown. This is the same across all apps.

**Q: Does it work on Termux?**
A: Yes, 100%. Just run `pkg install python`, then run the install command.

**Q: Do I need an API key?**
A: No. Everything is ready out of the box.

**Q: What happens with an invalid PNR?**
A: You'll see an "Invalid PNR" error. The PNR must be 10 digits.

---

## 🛡️ Security / Privacy

- The tool only fetches **public enquiry data**
- It does **not send any login or password**
- It does **not store any data** (fully stateless)

---

## 🤝 Contributing

PRs welcome! Open an issue if you'd like a new feature.

## 📜 License

[MIT](LICENSE) — free for everyone.

---

⭐ **If you like this repo, please give it a star!** Stars help more people discover it.
