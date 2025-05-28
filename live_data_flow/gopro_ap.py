from live_data_flow.camera_control import GoProControl
import asyncio
import logging

logging.basicConfig(level = logging.INFO)

async def main():
    control = GoProControl()
    devices = await GoProControl.search_device()
        
    if devices:
        for device in devices.values():
            await control.connect(device)
            await control.turn_on_ap()
            await control.disconnect()

asyncio.run(main())