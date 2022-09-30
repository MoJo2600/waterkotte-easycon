# Standard library imports
import asyncio
import sys
import argparse
import logging
from aiohttp import ClientError, ClientSession
from waterkotte_easycon import ApiError, EasyCon

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

async def main(url: str, login: str, password: str) -> None:
    """Main"""
    logging.info(f'{url=}, {login=}, {password=}')
    async with ClientSession() as websession:
        try:
            easycon = EasyCon(
                url, login, password, websession
            )
            basic_information = await easycon.async_get_basic_information()

        except (ApiError, ClientError) as error:
            logging.error(error)
        else:
            print(f'basic information: {basic_information=}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Retrieve information from Waterkotte EasyCon web interface')
    parser.add_argument('--url', help='The url of your heat pump', required=True)
    parser.add_argument('--login', help='The login (defaults to waterkotte)', default='waterkotte')
    parser.add_argument('--password', help='The password (defaults to waterkotte)', default='waterkotte')
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(args.url, args.login, args.password))
    loop.close()