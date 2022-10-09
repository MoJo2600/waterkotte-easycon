# Standard library imports
import asyncio
import sys
import argparse
import logging
from aiohttp import ClientError, ClientSession
from easycon import ApiError, EasyCon

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

async def main(ip: str, login: str, password: str) -> None:
    """Main"""
    logging.info(f'{ip=}, {login=}, {password=}')
    async with ClientSession() as websession:
        try:
            easycon = EasyCon(
                ip, login, password, websession
            )
            data = await easycon.get_data()

        except (ApiError, ClientError) as error:
            logging.error(error)
        else:
            print(f'data: {data=}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Retrieve information from Waterkotte EasyCon web interface')
    parser.add_argument('--ip', help='The IP address of your heat pump', required=True)
    parser.add_argument('--login', help='The login (defaults to waterkotte)', default='waterkotte')
    parser.add_argument('--password', help='The password (defaults to waterkotte)', default='waterkotte')
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(args.ip, args.login, args.password))
    loop.close()