"""
Gesture Hero — Script Python
BLE (Nano 33) → Simulation clavier (Beach Buggy Racing)
Arduino Days 2026 — Cotonou
"""

import asyncio
from bleak import BleakScanner, BleakClient
import pyautogui
import time

# ===== Configuration =====
DEVICE_NAME = "Sunnypulse"
CHARACTERISTIC_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"
KEY_PRESS_DURATION = 0.3
COOLDOWN = 0.5

# ===== Mapping gestes → touches =====
# HACK : si right ne marche pas, change "right": "right" → "right": "left"
GESTURE_MAP = {
    "forward":  "up",
    "backward": "down",
    "left":     "left",
    "right":    "right",
    "idle":     None
}

last_gesture_time = 0

def press_key(key):
    pyautogui.keyDown(key)
    time.sleep(KEY_PRESS_DURATION)
    pyautogui.keyUp(key)
    print(f"Touche simulée : {key}")

def notification_handler(sender, data):
    global last_gesture_time
    gesture = data.decode("utf-8").strip().lower()

    if gesture == "idle":
        print("État : Repos (IDLE)")
        return

    now = time.time()
    if now - last_gesture_time < COOLDOWN:
        return
    last_gesture_time = now

    if gesture in GESTURE_MAP and GESTURE_MAP[gesture] is not None:
        print(f"Geste détecté : {gesture}")
        press_key(GESTURE_MAP[gesture])
    else:
        print(f"Donnée ignorée : {gesture}")

async def connect_and_run():
    print("Recherche du dispositif BLE...")

    device = None
    while device is None:
        devices = await BleakScanner.discover(timeout=5.0)
        for d in devices:
            if d.name == DEVICE_NAME:
                device = d
                break
        if device is None:
            print("Dispositif non trouvé, nouvelle tentative...")

    print(f"Trouvé : {device.name} ({device.address})")
    await asyncio.sleep(2.0)

    async with BleakClient(
        device.address,
        timeout=30.0,
        winrt={"use_cached_services": False}
    ) as client:
        print("Connecté ! En attente de gestes...")
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

        while client.is_connected:
            await asyncio.sleep(0.1)

        print("Connexion perdue.")

if __name__ == "__main__":
    print("=== Gesture Hero — Arduino Days 2026 ===")
    print("Commandes :")
    for gesture, key in GESTURE_MAP.items():
        print(f"  {gesture} → {key}")
    print()

    try:
        asyncio.run(connect_and_run())
    except KeyboardInterrupt:
        print("\nArrêt du programme.")