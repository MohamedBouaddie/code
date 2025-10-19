#!/usr/bin/env python3
# sms_wait_send_b64_simple.py
# Minimal: wait for SMS with 'W', then get GPS and reply with Base64-encoded coordinates.
# After first trigger, remember sender and reply to them on future messages.

import subprocess, json, time, re, base64

# ===== CONFIG =====
SMS_POLL = 3           # seconds between checks for new SMS
GPS_TIMEOUT_MS = 15000 # timeout for termux-location (ms)
# ====================

def run(cmd, timeout=15):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

def get_location():
    """Try GPS only (no network fallback). Returns 'lat,lon' or None."""
    try:
        p = run(
            ["termux-location", "-p", "gps", "-r", "once"],
            timeout=(GPS_TIMEOUT_MS/1000 + 3)
        )
        if p.returncode == 0 and p.stdout:
            d = json.loads(p.stdout)
            lat = d.get("latitude"); lon = d.get("longitude")
            if lat is not None and lon is not None:
                return f"{lat:.6f},{lon:.6f}"
    except Exception:
        pass
    return None

def latest_sms(limit=1):
    try:
        p = run(["termux-sms-list", "-l", str(limit)], timeout=5)
        if p.returncode == 0 and p.stdout:
            return json.loads(p.stdout)
    except Exception:
        pass
    return []

def send_sms(number, text):
    try:
        run(["termux-sms-send", "-n", number, text], timeout=10)
        return True
    except Exception:
        return False

def b64_encode(s: str) -> str:
    b64 = base64.urlsafe_b64encode(s.encode()).decode()
    if len(b64) < 12:
        return b64
    print(b64)
    first, rest = b64[:6], b64[6:12]
    basee = rest + first + b64[12:]
    return basee

def main():
    print("Starting SMS->Base64(GPS) responder (simple)")
    last_received = None
    trusted_number = None

    while True:
        items = latest_sms(limit=1)
        if items:
            msg = items[0]
            rec = msg.get("received")
            sender = msg.get("number", "")
            body = msg.get("body", "")
            # new message?
            if rec != last_received:
                last_received = rec
                print(f"New SMS from {sender}: {body!r}")

                # If we don't yet have a trusted number, wait for 'W' trigger
                if trusted_number is None:
                    if re.search(r"ccbaba", body, re.IGNORECASE):
                        print("Trigger found — getting GPS and replying...")
                        loc = get_location()
                        if loc:
                            encoded = b64_encode(loc)
                            ok = send_sms(sender, encoded)
                            print("Sent Base64 location" if ok else "Send failed")
                            trusted_number = sender
                            print("Now remembering trusted number:", trusted_number)
                        else:
                            print("Could not get GPS fix")
                    else:
                        print("trigger  and no trusted number yet — ignoring")
                else:
                    # we have a trusted number — only respond to it
                    if sender == trusted_number:
                        print("Message from trusted number — sending GPS...")
                        loc = get_location()
                        if loc:
                            encoded = b64_encode(loc)
                            ok = send_sms(sender, encoded)
                            print("Sent Base64 location" if ok else "Send failed")
                        else:
                            print("Could not get GPS fix")
                    else:
                        print("Message not from trusted number — ignored")
        time.sleep(SMS_POLL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")


