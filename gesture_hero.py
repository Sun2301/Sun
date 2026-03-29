"""
Gesture Hero — Script Python
BLE (Nano 33) → Simulation clavier (Beach Buggy Racing)
Arduino Days 2026 — Cotonou

Installation :
    pip install bleak pynput

Usage :
    python gesture_hero.py
"""

import asyncio
from bleak import BleakScanner, BleakClient
from pynput.keyboard import Key, Controller
import time

# ===== Configuration =====
DEVICE_NAME = "GestureHero"
CHARACTERISTIC_UUID = "00002a56-0000-1000-8000-00805f9b34fb"
KEY_PRESS_DURATION = 0.15  # Durée d'appui de touche en secondes

# ===== Mapping gestes → touches =====
GESTURE_MAP = {
    "forward":    Key.up,      # Accélérer
    "backward":     Key.down,    # Freiner / Reculer
    "left":  Key.left,    # Tourner à gauche
    "right":  Key.right,   # Tourner à droite
    "idle": None  #Ne rien faire
}

keyboard = Controller()

# ===== Simulation de touche =====
def press_key(key):
    keyboard.press(key)
    time.sleep(KEY_PRESS_DURATION)
    keyboard.release(key)
    print(f"Touche simulée : {key}")

# ===== Callback BLE — reçoit les données du Nano =====
def notification_handler(sender, data):
    gesture = data.decode("utf-8").strip().lower() # .lower() par sécurité
    
    if gesture == "idle":
        # Optionnel : on peut forcer le relâchement de toutes les touches ici
        # pour être sûr que la voiture s'arrête bien
        print("État : Repos (IDLE)")
        return

    if gesture in GESTURE_MAP and GESTURE_MAP[gesture] is not None:
        print(f"Geste détecté : {gesture} ")
        press_key(GESTURE_MAP[gesture])
    else:
        print(f"Donnée ignorée ou inconnue : {gesture}")
# ===== Scan et connexion BLE =====
async def connect_and_run():
    print("Recherche du dispositif BLE...")

    # Scanner pour trouver le Nano 33
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

    # Connexion et écoute
    async with BleakClient(device.address) as client:
        print("Connecté ! En attente de gestes...")

        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

        # Garder la connexion active
        while client.is_connected:
            await asyncio.sleep(0.1)

        print("Connexion perdue.")

# ===== Main =====
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
