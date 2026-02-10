"""
Simple script to scan for Muse devices via Bluetooth.
Use this to verify your Muse headbands are visible to the computer.
"""
import asyncio
from bleak import BleakScanner

async def scan():
    print("Scanning for Bluetooth LE devices (10 seconds)...")
    devices = await BleakScanner.discover(timeout=10.0)
    
    muse_devices = []
    print("\nFound Devices:")
    for d in devices:
        name = d.name or "Unknown"
        print(f"  - {d.address}: {name}")
        if "muse" in name.lower():
            muse_devices.append(d)
            
    print("\n" + "="*40)
    if muse_devices:
        print(f"SUCCESS: Found {len(muse_devices)} Muse device(s)!")
        for m in muse_devices:
            print(f"  -> {m.name} ({m.address})")
    else:
        print("WARNING: No Muse devices found.")
        print("Tips:")
        print("  1. Ensure Muse is charged and powered on.")
        print("  2. Ensure not connected to another device (phone/tablet).")
        print("  3. Bring them closer to the computer.")

if __name__ == "__main__":
    try:
        asyncio.run(scan())
    except Exception as e:
        print(f"Error during scan: {e}")
