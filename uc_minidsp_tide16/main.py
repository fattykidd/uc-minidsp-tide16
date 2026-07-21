# main.py
import asyncio
import logging
from .driver import Tide16Driver

logging.basicConfig(level=logging.INFO)

async def main():
    driver = Tide16Driver()
    await driver.run()

if __name__ == "__main__":
    asyncio.run(main())