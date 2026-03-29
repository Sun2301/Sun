import asyncio
from bleak import BleakScanner, BleakClient

async def inspect():
    devices = await BleakScanner.discover(timeout=5.0)
    device = next((d for d in devices if d.name == "Sunnypulse"), None)
    if not device:
        print("Pas trouvé")
        return
    print(f"Adresse: {device.address}")
    async with BleakClient(device.address, timeout=30.0,
        winrt={"use_cached_services": False}) as client:
        print("Connecté !")
        for service in client.services:
            print(f"Service: {service.uuid}")
            for char in service.characteristics:
                print(f"  Char: {char.uuid} — {char.properties}")

asyncio.run(inspect())
