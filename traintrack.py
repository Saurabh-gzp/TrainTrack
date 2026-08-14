#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
 TrainTrack — Indian Railways CLI (single file, Python 3, no deps)
=====================================================================
PNR Status, Live Train Status, Passenger Names, Seat Availability
and more — right from your terminal.

FEATURES:
  1. PNR Status (+ names)    -> full booking details + passenger names
  2. Live Train Status       -> current location + per-station delays
  3. Trains Between          -> all trains between two stations
  4. Seat Availability       -> availability by date and quota
  5. PNR Names               -> real masked name ("CHAxxxx xxxxx")
  6. Station Code Helper     -> common station codes
  7. Change Launch Command   -> set your own command name

No pip install needed — just Python 3.

RUN:  python3 traintrack.py
"""

import ssl
import struct
import sys
import base64
import json
import random
import urllib.request
import urllib.parse
from datetime import datetime


# ==================================================================
# Pure-Python AES-256 (CBC) — no dependencies
# ==================================================================
SBOX = [
0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16]

RCON = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36,0x6c,0xd8,0xab,0x4d]
INV_SBOX = [0] * 256
for _i in range(256):
    INV_SBOX[SBOX[_i]] = _i


def _xtime(a):
    a <<= 1
    if a & 0x100:
        a ^= 0x11b
    return a & 0xff


def _mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = _xtime(a)
        b >>= 1
    return r


def _key_expansion(key):
    nk, nb, nr = 8, 4, 14
    w = [0] * (nb * (nr + 1))
    for i in range(nk):
        w[i] = (key[4 * i] << 24) | (key[4 * i + 1] << 16) | \
               (key[4 * i + 2] << 8) | key[4 * i + 3]
    for i in range(nk, nb * (nr + 1)):
        temp = w[i - 1]
        if i % nk == 0:
            temp = ((SBOX[(temp >> 16) & 0xff] << 24) |
                    (SBOX[(temp >> 8) & 0xff] << 16) |
                    (SBOX[temp & 0xff] << 8) |
                    SBOX[(temp >> 24) & 0xff]) ^ (RCON[i // nk - 1] << 24)
        elif i % nk == 4:
            temp = ((SBOX[(temp >> 24) & 0xff] << 24) |
                    (SBOX[(temp >> 16) & 0xff] << 16) |
                    (SBOX[(temp >> 8) & 0xff] << 8) |
                    SBOX[temp & 0xff])
        w[i] = w[i - nk] ^ temp
    return w


def _add_round_key(state, w, rnd):
    for i in range(4):
        state[i] ^= w[rnd * 4 + i]


def _sub_bytes(state, box):
    for i in range(4):
        state[i] = ((box[(state[i] >> 24) & 0xff] << 24) |
                    (box[(state[i] >> 16) & 0xff] << 16) |
                    (box[(state[i] >> 8) & 0xff] << 8) |
                    box[state[i] & 0xff])


def _shift_rows(state):
    t = [0] * 4
    t[0] = (state[0] & 0xff000000) | (state[1] & 0x00ff0000) | \
           (state[2] & 0x0000ff00) | (state[3] & 0x000000ff)
    t[1] = (state[1] & 0xff000000) | (state[2] & 0x00ff0000) | \
           (state[3] & 0x0000ff00) | (state[0] & 0x000000ff)
    t[2] = (state[2] & 0xff000000) | (state[3] & 0x00ff0000) | \
           (state[0] & 0x0000ff00) | (state[1] & 0x000000ff)
    t[3] = (state[3] & 0xff000000) | (state[0] & 0x00ff0000) | \
           (state[1] & 0x0000ff00) | (state[2] & 0x000000ff)
    for i in range(4):
        state[i] = t[i]


def _inv_shift_rows(state):
    t = [0] * 4
    t[0] = (state[0] & 0xff000000) | (state[3] & 0x00ff0000) | \
           (state[2] & 0x0000ff00) | (state[1] & 0x000000ff)
    t[1] = (state[1] & 0xff000000) | (state[0] & 0x00ff0000) | \
           (state[3] & 0x0000ff00) | (state[2] & 0x000000ff)
    t[2] = (state[2] & 0xff000000) | (state[1] & 0x00ff0000) | \
           (state[0] & 0x0000ff00) | (state[3] & 0x000000ff)
    t[3] = (state[3] & 0xff000000) | (state[2] & 0x00ff0000) | \
           (state[1] & 0x0000ff00) | (state[0] & 0x000000ff)
    for i in range(4):
        state[i] = t[i]


def _mix_columns(state):
    for c in range(4):
        w = state[c]
        a0 = (w >> 24) & 0xff
        a1 = (w >> 16) & 0xff
        a2 = (w >> 8) & 0xff
        a3 = w & 0xff
        b0 = _xtime(a0) ^ (_xtime(a1) ^ a1) ^ a2 ^ a3
        b1 = a0 ^ _xtime(a1) ^ (_xtime(a2) ^ a2) ^ a3
        b2 = a0 ^ a1 ^ _xtime(a2) ^ (_xtime(a3) ^ a3)
        b3 = (_xtime(a0) ^ a0) ^ a1 ^ a2 ^ _xtime(a3)
        state[c] = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3


def _inv_mix_columns(state):
    for c in range(4):
        w = state[c]
        a0 = (w >> 24) & 0xff
        a1 = (w >> 16) & 0xff
        a2 = (w >> 8) & 0xff
        a3 = w & 0xff
        b0 = _mul(a0, 14) ^ _mul(a1, 11) ^ _mul(a2, 13) ^ _mul(a3, 9)
        b1 = _mul(a0, 9) ^ _mul(a1, 14) ^ _mul(a2, 11) ^ _mul(a3, 13)
        b2 = _mul(a0, 13) ^ _mul(a1, 9) ^ _mul(a2, 14) ^ _mul(a3, 11)
        b3 = _mul(a0, 11) ^ _mul(a1, 13) ^ _mul(a2, 9) ^ _mul(a3, 14)
        state[c] = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3


def _aes_encrypt_block(block, key):
    w = _key_expansion(key)
    state = [0] * 4
    for i in range(4):
        state[i] = (block[4 * i] << 24) | (block[4 * i + 1] << 16) | \
                   (block[4 * i + 2] << 8) | block[4 * i + 3]
    _add_round_key(state, w, 0)
    for rnd in range(1, 14):
        _sub_bytes(state, SBOX)
        _shift_rows(state)
        _mix_columns(state)
        _add_round_key(state, w, rnd)
    _sub_bytes(state, SBOX)
    _shift_rows(state)
    _add_round_key(state, w, 14)
    out = bytearray(16)
    for i in range(4):
        out[4 * i] = (state[i] >> 24) & 0xff
        out[4 * i + 1] = (state[i] >> 16) & 0xff
        out[4 * i + 2] = (state[i] >> 8) & 0xff
        out[4 * i + 3] = state[i] & 0xff
    return bytes(out)


def _aes_decrypt_block(block, key):
    w = _key_expansion(key)
    state = [0] * 4
    for i in range(4):
        state[i] = (block[4 * i] << 24) | (block[4 * i + 1] << 16) | \
                   (block[4 * i + 2] << 8) | block[4 * i + 3]
    _add_round_key(state, w, 14)
    for rnd in range(13, 0, -1):
        _inv_shift_rows(state)
        _sub_bytes(state, INV_SBOX)
        _add_round_key(state, w, rnd)
        _inv_mix_columns(state)
    _inv_shift_rows(state)
    _sub_bytes(state, INV_SBOX)
    _add_round_key(state, w, 0)
    out = bytearray(16)
    for i in range(4):
        out[4 * i] = (state[i] >> 24) & 0xff
        out[4 * i + 1] = (state[i] >> 16) & 0xff
        out[4 * i + 2] = (state[i] >> 8) & 0xff
        out[4 * i + 3] = state[i] & 0xff
    return bytes(out)


def aes_cbc_encrypt(plaintext, key, iv):
    prev = iv
    out = bytearray()
    for i in range(0, len(plaintext), 16):
        block = plaintext[i:i + 16]
        xored = bytes(a ^ b for a, b in zip(block, prev))
        enc = _aes_encrypt_block(xored, key)
        out += enc
        prev = enc
    return bytes(out)


def aes_cbc_decrypt(ciphertext, key, iv):
    prev = iv
    out = bytearray()
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i + 16]
        dec = _aes_decrypt_block(block, key)
        out += bytes(a ^ b for a, b in zip(dec, prev))
        prev = block
    return bytes(out)


def pkcs7_pad(data, block=16):
    n = block - len(data) % block
    return data + bytes([n]) * n


def pkcs7_unpad(data):
    if not data:
        return data
    n = data[-1]
    if n == 0 or n > 16:
        return data
    return data[:-n]


def aes_encrypt_str(s, key_str, iv_str):
    return base64.b64encode(
        aes_cbc_encrypt(pkcs7_pad(s.encode()), key_str.encode(), iv_str.encode())
    ).decode()


def aes_decrypt_str(b64, key_str, iv_str):
    pt = aes_cbc_decrypt(base64.b64decode(b64), key_str.encode(), iv_str.encode())
    return pkcs7_unpad(pt).decode()


# ==================================================================
# ChaCha20 stream cipher (RFC 7539)
# ==================================================================
_KEY = bytes.fromhex("6954c016d42f66215789e489029b8190241d8b0b7b5686d4d617d36a519cbea8")
_NONCE = bytes.fromhex("c9cde0fa234addac0b3abb73")
_CONST = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]


def _rotl(x, n):
    return ((x << n) | (x >> (32 - n))) & 0xffffffff


def _qr(x, a, b, c, d):
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] = _rotl(x[d] ^ x[a], 16)
    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] = _rotl(x[b] ^ x[c], 12)
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] = _rotl(x[d] ^ x[a], 8)
    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] = _rotl(x[b] ^ x[c], 7)


def _chacha20_block(counter):
    k = list(struct.unpack("<8I", _KEY))
    n = list(struct.unpack("<3I", _NONCE))
    s = _CONST + k + [counter] + n
    x = s[:]
    for _ in range(10):
        _qr(x, 0, 4, 8, 12); _qr(x, 1, 5, 9, 13)
        _qr(x, 2, 6, 10, 14); _qr(x, 3, 7, 11, 15)
        _qr(x, 0, 5, 10, 15); _qr(x, 1, 6, 11, 12)
        _qr(x, 2, 7, 8, 13); _qr(x, 3, 4, 9, 14)
    return struct.pack("<16I", *[(x[i] + s[i]) & 0xffffffff for i in range(16)])


def encrypt(plaintext):
    out = bytearray()
    counter = 1
    for i in range(0, len(plaintext), 64):
        block = plaintext[i:i + 64]
        ks = _chacha20_block(counter)
        out += bytes(b ^ ks[j] for j, b in enumerate(block))
        counter += 1
    return bytes(out)


# ==================================================================
# HTTP helper (stdlib, legacy SSL enabled)
# ==================================================================
def _ctx():
    c = ssl.create_default_context()
    c.check_hostname = False
    c.verify_mode = ssl.CERT_NONE
    try:
        c.options |= ssl.OP_LEGACY_SERVER_CONNECT  # for rr.irctc.co.in
    except Exception:
        pass
    return c


def http_post(url, body, headers, timeout=40):
    req = urllib.request.Request(url, data=body.encode("utf-8"),
                                 method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        return r.read().decode("utf-8", errors="replace")


def http_get(url, headers, timeout=25):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
        return r.read().decode("utf-8", errors="replace")


# ==================================================================
# Train enquiry API (ChaCha20)
# ==================================================================
BACKEND = "https://api.trackmytrain.co.in/android"


def backend_call(body, timeout=30):
    ct = encrypt(body.encode("utf-8")).hex().encode("ascii")
    raw = http_post(BACKEND, ct.decode(), {"User-Agent": "okhttp/4.9.0",
                                           "Content-Type": "text/plain"},
                    timeout=timeout)
    try:
        return json.loads(raw)
    except Exception:
        return {"status": "ERROR", "response": raw, "_raw": True}


# ==================================================================
# ixigo PNR API
# ==================================================================
IXIGO_SIG = ("eyJkIjoiamM3Q1J5Z0ZNRGpFTUVsSjdQTnFUXC9NSDgxVmp4NVdaRzFLdStObHNYVTA9IiwidCI6"
             "MTY1MjI5NDI1NTY4OCwicCI6Imh0dHBzOlwvXC93d3cuaXhpZ28uY29tXC90cmFpbnMtaW5mb1wv"
             "djFcL3BuclwvZW5xdWlyeT9wbnI9MzM2NTk5OTk2NiZtb2RlPU5FV19BRERJVElPTiIsIm0iOiJH"
             "RVQifQ==.K5wMwlgX4ZzyfvJTuVLEsw55tAJ8SH6sAiuCBBkKRrI=")


def ixigo_pnr(pnr):
    url = ("https://www.ixigo.com/trains-info/v1/pnr/enquiry?pnr=%s"
           "&mode=NEW_ADDITION") % pnr
    raw = http_get(url, {
        "Host": "www.ixigo.com",
        "ixisrc": "iximatr",
        "clientid": "iximatr",
        "apikey": "iximatr!2$",
        "appversion": "1823",
        "uuid": "dbds",
        "signature": IXIGO_SIG,
        "User-Agent": "Mozilla/5.0",
    })
    try:
        return json.loads(raw)
    except Exception:
        return None


# ==================================================================
# eRail fallback
# ==================================================================
ERAL = "https://erail.in/rail/getTrains.aspx"
ERAL_UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def erail_trains(frm, to, date=None, quota="GN"):
    params = {"Station_From": frm, "Station_To": to,
              "DataSource": "0", "Language": "0", "Cache": "true"}
    if date:
        params["Date"] = date
        params["Quota"] = quota
    url = ERAL + "?" + urllib.parse.urlencode(params)
    raw = http_get(url, {"User-Agent": ERAL_UA,
                         "X-Requested-With": "XMLHttpRequest",
                         "Referer": "https://erail.in/"})
    if not raw or raw.strip().startswith("<"):
        return []
    trains = []
    TRAIN_TYPES = ("SUPERFAST", "MAIL", "EXPRESS", "PASSENGER", "RAJDHANI",
                   "SHATABDI", "DURONTO", "GARIB RATH", "JAN SHATABDI",
                   "SAMPARK KRANTI", "HUMSAFAR", "VANDE BHARAT", "TEJAS",
                   "ANTYODAYA", "SPECIAL", "INTERCITY")
    for seg in raw.split("^")[1:]:
        f = seg.split("~")
        if len(f) < 15:
            continue
        g = lambda i: f[i].strip() if i < len(f) else ""
        ttype, dist = "", ""
        for i in range(10, len(f)):
            if g(i).upper() in TRAIN_TYPES:
                ttype = g(i)
                for j in range(i + 1, len(f)):
                    if g(j).isdigit() and int(g(j)) > 100:
                        dist = g(j)
                        break
                break
        d = g(13)
        days = "".join(DAYS[i] + " " for i, c in enumerate(d[:7]) if c == "1").strip() \
            if len(d) >= 7 else d
        if g(0).isdigit():
            trains.append({"no": g(0), "name": g(1), "dep": g(10), "arr": g(11),
                           "type": ttype, "dist": dist, "days": days})
    return trains


# ==================================================================
# IRCTC Tourism (real masked name)
# ==================================================================
GUEST_KEY = "16AB5B0488AEC6D551F3649A9903554B"
GUEST_IV = "EDA480701417E5D0"
PNR_KEY = "vqv3EMBB)>)^~}znjZ24'R$-)vMkuFR)"
PNR_IV = "zC+zm3@BDHJ<C::H"


def irctc_get_token():
    rand = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")
                   for _ in range(10))
    login = json.dumps({"email": rand + "@gmail.com",
                        "mobile": "9" + "".join(random.choice("0123456789")
                                                for _ in range(9))})
    tb = aes_encrypt_str(login, GUEST_KEY, GUEST_IV)
    raw = http_post("https://www.irctctourism.com/NewUserlogin/user/guestlogin",
                    json.dumps({"data": tb}),
                    {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json",
                     "Origin": "https://www.rr.irctctourism.com",
                     "Referer": "https://www.rr.irctctourism.com/"})
    return json.loads(raw)["data"]


def irctc_pnr_search(pnr, token):
    pb = json.dumps({"req": aes_encrypt_str(json.dumps({"pnrnumber": pnr}),
                                            PNR_KEY, PNR_IV)})
    raw = http_post("https://www.rr.irctc.co.in/RetServc/rrservice/pnrSearch",
                    pb,
                    {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json",
                     "Authorization": "Bearer " + token,
                     "Origin": "https://www.rr.irctctourism.com",
                     "Referer": "https://www.rr.irctctourism.com/"})
    return json.loads(raw)


def irctc_full_names(pnr):
    """Full flow: token -> search -> decrypt -> passenger names."""
    token = irctc_get_token()
    resp = irctc_pnr_search(pnr, token)
    if resp.get("status") != "SUCCESS":
        return None, resp
    plain = aes_decrypt_str(resp["data"], PNR_KEY, PNR_IV)
    return json.loads(plain), resp


# ==================================================================
# FEATURES
# ==================================================================
def pnr_status():
    pnr = input("10-digit PNR number: ").strip()
    if not (pnr.isdigit() and len(pnr) == 10):
        print("[!] PNR must be 10 digits.")
        return
    print(f"\n[..] Fetching PNR {pnr}...\n")

    # 1. train enquiry API (reliable)
    body = '{\n  "pnr":"%s",\n  "method":"pnr"\n}' % pnr
    try:
        resp = backend_call(body)
    except Exception as e:
        print(f"[X] Backend error: {e}")
        resp = None
    if resp and resp.get("status") == "SUCCESS":
        d = resp["response"]
        print("=" * 60)
        print("  PNR STATUS")
        print("=" * 60)
        print(f"  PNR Number        : {d.get('pnrNumber')}")
        print(f"  Train             : {d.get('trainNumber')} - {d.get('trainName')}")
        print(f"  Journey Date      : {d.get('dateOfJourney')}")
        print(f"  From -> To        : {d.get('sourceStation')} -> {d.get('destinationStation')}")
        print(f"  Boarding Point    : {d.get('boardingPoint')}")
        print(f"  Reservation Upto  : {d.get('reservationUpto')}")
        print(f"  Class             : {d.get('journeyClass')}")
        print(f"  Quota             : {d.get('quota')}")
        print(f"  Chart Status      : {d.get('chartStatus')}")
        print(f"  Booking Fare      : Rs.{d.get('bookingFare')}")
        print(f"  Distance          : {d.get('distance')} km")
        print(f"  Booking Date      : {d.get('bookingDate')}")
        print()
        pl = d.get("passengerList", [])
        if pl:
            print("  PASSENGERS:")
            for p in pl:
                print(f"    #{p.get('passengerSerialNumber')}: "
                      f"{p.get('currentStatusDetails', p.get('bookingStatusDetails'))} "
                      f"({p.get('currentStatus', p.get('bookingStatus'))})")
        print("=" * 60)
    else:
        print("[!] Backend response:", resp.get("response", resp) if resp else "error")

    # 2. IRCTC Tourism — real masked name (e.g. "CHAxxxx xxxxx")
    print("\n[..] Fetching passenger names (IRCTC Tourism)...")
    try:
        obj = None
        for attempt in range(3):
            try:
                obj, _ = irctc_full_names(pnr)
                if obj is not None:
                    break
            except Exception:
                continue
        if obj:
            passengers = obj.get("passengerDetailsDTO", [])
            if passengers:
                print("\n" + "=" * 60)
                print("  PASSENGER NAMES (IRCTC)")
                print("=" * 60)
                for p in passengers:
                    name = p.get("displayName", "?")
                    age = p.get("age", "?")
                    gender = p.get("gender", "?")
                    seat = p.get("seatStts", "?")
                    gmap = {"M": "Male", "F": "Female"}
                    print(f"    #{p.get('serialNo')}: {name}  "
                          f"(age {age}, {gmap.get(gender, gender)})  |  {seat}")
                print("=" * 60)
        else:
            print("    (No name from IRCTC yet — full name appears after chart preparation)")
    except Exception as e:
        print(f"[!] IRCTC error: {e}")

    # 3. ixigo (backup, pre-chart placeholder)
    print("\n[..] Verifying with ixigo...")
    try:
        ix = ixigo_pnr(pnr)
        it = (ix.get("data", {}) or {}).get("itineraries", [{}])
        if it:
            it = it[0]
            names = it.get("passengers", [])
            if names:
                print("  (ixigo data — seat/berth confirmation):")
                for p in names:
                    berth = p.get("berth", "")
                    seat = p.get("seat", "")
                    st = p.get("currentBookingStatus", {}).get("text", p.get("status", ""))
                    print(f"    #{p.get('serialNo')}: {berth}  |  {seat}  |  {st}")
    except Exception as e:
        print(f"[!] ixigo error: {e}")


def pnr_names_irctc():
    """Real masked name (e.g. 'CHAxxxx xxxxx') — IRCTC Tourism API."""
    pnr = input("10-digit PNR number: ").strip()
    if not (pnr.isdigit() and len(pnr) == 10):
        print("[!] PNR must be 10 digits.")
        return
    print(f"\n[..] Fetching names for PNR {pnr} (IRCTC Tourism)...\n")

    # retry loop (network flaky ho sakta hai)
    obj = None
    last_err = None
    for attempt in range(3):
        try:
            obj, resp = irctc_full_names(pnr)
            if obj is not None:
                break
            last_err = resp
        except Exception as e:
            last_err = str(e)
    if obj is None:
        print("[X] IRCTC fail:", last_err)
        return

    passengers = obj.get("passengerDetailsDTO", [])
    print("=" * 60)
    print(f"  PNR {pnr} — {obj.get('trainNum')} {obj.get('trainName')}")
    print(f"  {obj.get('stationFrom')} -> {obj.get('stationTo')} | "
          f"Class {obj.get('journeyClass')} | {obj.get('chartStts')}")
    print("=" * 60)
    print("  PASSENGERS:")
    for p in passengers:
        name = p.get("displayName", "?")
        age = p.get("age", "?")
        gender = p.get("gender", "?")
        seat = p.get("seatStts", "?")
        gmap = {"M": "Male", "F": "Female"}
        print(f"    #{p.get('serialNo')}: {name}  (age {age}, "
              f"{gmap.get(gender, gender)})  |  {seat}")
    print("=" * 60)


def live_status():
    train_no = input("Train number (e.g. 15708): ").strip()
    if not train_no.isdigit():
        print("[!] Please enter a valid train number.")
        return
    date = input("Journey date (YYYYMMDD, Enter = today): ").strip()
    if not date:
        date = datetime.now().strftime("%Y%m%d")
    print(f"\n[..] Train {train_no} live status ({date})...\n")
    body = '{"trno":"%s", "jdate":"%s", "method":"lts", "wdata":""}' % (train_no, date)
    try:
        resp = backend_call(body)
    except Exception as e:
        print(f"[X] Error: {e}")
        return
    if resp.get("status") != "SUCCESS":
        print("[!] Backend response:", resp.get("response", resp))
        return
    d = resp["response"]
    if not d.get("data_available"):
        print("[!] Data not available:", (d.get("error") or {}).get("message", ""))
        return
    sd = d["availableStatusData"]
    print("=" * 60)
    print("  LIVE TRAIN STATUS")
    print("=" * 60)
    print(f"  Train         : {sd.get('trainName')}")
    print(f"  Status        : {sd.get('statusMessage')}")
    print(f"  Last Station  : {sd.get('last_known_stn')} "
          f"({sd.get('last_known_event')})")
    loc = sd.get("locationData")
    if loc:
        print(f"  Location      : lat={loc.get('lat')}, lon={loc.get('lon')}")
    print(f"  Cancellation  : {sd.get('cancellation')}")
    print(f"  Diversion     : {sd.get('diversion')}")
    print(f"  Reschedule    : {sd.get('reschedule')}")
    print()
    dd = sd.get("delayData", [])
    if dd:
        print("  STATION DELAYS:")
        for s in dd:
            stn = s.get("stn", "")
            arr = s.get("arr_delay", "-")
            dep = s.get("dep_delay", "-")
            plat = s.get("ntes_platform", "")
            print(f"    {stn:<8} arr+{arr}  dep+{dep}  (pf {plat})")
    print("=" * 60)


def trains_between():
    frm = input("From station code (e.g. NDLS): ").strip().upper()
    to = input("To station code (e.g. CNB): ").strip().upper()
    if not frm or not to:
        print("[!] Both station codes are required.")
        return
    print(f"\n[..] {frm} -> {to} trains...\n")
    try:
        trains = erail_trains(frm, to)
    except Exception as e:
        print(f"[X] Error: {e}")
        return
    if not trains:
        print("[!] No trains found (wrong code? Use Station Helper).")
        return
    print(f"{'TRAIN':<7} {'NAME':<24} {'DEP':<7} {'ARR':<7} {'TYPE':<13} {'DIST':<6} RUNS")
    print("-" * 95)
    for t in trains[:30]:
        print(f"{t['no']:<7} {t['name'][:23]:<24} {t['dep']:<7} {t['arr']:<7} "
              f"{t['type'][:12]:<13} {t['dist']:<6} {t['days']}")
    print(f"\nTotal: {len(trains)} trains (max 30 shown)")


def seat_availability():
    frm = input("From station code: ").strip().upper()
    to = input("To station code: ").strip().upper()
    date = input("Date (DD-MM-YYYY, Enter = today): ").strip()
    if not date:
        date = datetime.now().strftime("%d-%m-%Y")
    quota = input("Quota (Enter = GN): ").strip().upper() or "GN"
    print(f"\n[..] {frm}->{to} on {date} ({quota})...\n")
    try:
        trains = erail_trains(frm, to, date=date, quota=quota)
    except Exception as e:
        print(f"[X] Error: {e}")
        return
    if not trains:
        print("[!] No trains found.")
        return
    print(f"{'TRAIN':<7} {'NAME':<24} {'DEP':<7} {'ARR':<7} TYPE")
    print("-" * 70)
    for t in trains[:30]:
        print(f"{t['no']:<7} {t['name'][:23]:<24} {t['dep']:<7} {t['arr']:<7} {t['type']}")
    print("\n[!] Class-wise availability (SL/3A/2A) is limited via the free eRail API.")


def station_helper():
    q = input("Station name fragment (e.g. kan): ").strip().lower()
    common = {"NDLS": "New Delhi", "CNB": "Kanpur Central", "BCT": "Mumbai Central",
              "CSTM": "Mumbai CSMT", "HWH": "Howrah", "SDAH": "Sealdah",
              "MAS": "Chennai Central", "BZA": "Vijayawada", "PNBE": "Patna",
              "LKO": "Lucknow", "ALD": "Prayagraj", "BSB": "Varanasi",
              "AGC": "Agra Cantt", "JP": "Jaipur", "ADI": "Ahmedabad",
              "BPL": "Bhopal", "NGP": "Nagpur", "SC": "Secunderabad",
              "HYB": "Hyderabad", "SBC": "Bengaluru", "PUNE": "Pune",
              "ASR": "Amritsar", "JAT": "Jammu Tawi", "GWL": "Gwalior",
              "JHS": "Jhansi", "UMB": "Ambala Cantt", "SV": "Siwan"}
    hits = [(c, n) for c, n in common.items() if q in n.lower()]
    for c, n in hits:
        print(f"  {c:<6} {n}")
    if not hits:
        print("[!] Not found in common list. Common codes:")
        for c, n in common.items():
            print(f"  {c:<6} {n}")


def change_launch_command():
    """Set or change the custom launch command name (e.g. `train`).

    Creates a wrapper script in ~/.traintrack/ with the chosen name.
    Since ~/.traintrack is added to PATH by the installer, typing the
    command name launches TrainTrack from anywhere.
    """
    import os
    install_dir = os.path.expanduser("~/.traintrack")
    script_path = os.path.realpath(__file__)
    cmd_file = os.path.join(install_dir, ".cmdname")

    # read old command name (to clean up)
    old_name = ""
    if os.path.isfile(cmd_file):
        try:
            with open(cmd_file, "r") as f:
                old_name = f.read().strip()
        except Exception:
            old_name = ""

    print()
    print("  Change Launch Command")
    print("  ---------------------")
    print("  Current command: %s" % (old_name if old_name else "none (set your own)"))
    print()
    name = input("  New launch command name (e.g. train): ").strip()

    if not name:
        print("[!] Command name cannot be empty.")
        return
    if name in ("python", "python3", "sh", "bash", "ls", "cd", "rm", "cat", "sudo"):
        print("[!] That name is reserved. Choose a different one.")
        return
    if not name.replace("_", "").replace("-", "").isalnum():
        print("[!] Invalid name. Use letters, numbers, '-' or '_' only.")
        return

    os.makedirs(install_dir, exist_ok=True)

    # remove old wrapper if it exists
    if old_name and old_name != name:
        old_target = os.path.join(install_dir, old_name)
        if os.path.isfile(old_target) or os.path.islink(old_target):
            try:
                os.remove(old_target)
            except Exception:
                pass

    # create new wrapper
    target = os.path.join(install_dir, name)
    wrapper = "#!/bin/sh\nexec python3 \"%s\" \"$@\"\n" % script_path
    try:
        with open(target, "w") as f:
            f.write(wrapper)
        os.chmod(target, 0o755)
    except Exception as e:
        print("[X] Failed to create command: %s" % e)
        return

    # remember the name
    try:
        with open(cmd_file, "w") as f:
            f.write(name)
    except Exception:
        pass

    print()
    print("[+] Launch command set!")
    print("    Now type:  %s" % name)
    print("    (open a NEW terminal if the command is not found yet)")


MENU = [
    ("PNR Status (+ Names)", pnr_status),
    ("Live Train Status", live_status),
    ("Trains Between Stations", trains_between),
    ("Seat Availability", seat_availability),
    ("PNR Names (IRCTC - masked)", pnr_names_irctc),
    ("Station Code Helper", station_helper),
    ("Change Launch Command", change_launch_command),
]


def main():
    print("=" * 60)
    print("  TrainTrack — Indian Railways CLI")
    print("=" * 60)
    print("  PNR + Live Status  -> live enquiry data")
    print("  Names              -> IRCTC Tourism (real masked name)")
    print("  Trains/Seat        -> eRail public API")
    print()
    while True:
        print("\n--- MAIN MENU ---")
        for i, (name, _) in enumerate(MENU, 1):
            print(f"  {i}. {name}")
        print("  0. Exit")
        try:
            ch = input("\nOption: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if ch in ("0", ""):
            print("Goodbye!")
            break
        if ch.isdigit() and 1 <= int(ch) <= len(MENU):
            try:
                MENU[int(ch) - 1][1]()
            except KeyboardInterrupt:
                print("\n[cancelled]")
            except Exception as e:
                print(f"[X] Error: {e}")
        else:
            print("[!] Invalid option.")


if __name__ == "__main__":
    main()
