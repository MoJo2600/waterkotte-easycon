"""
Module
"""
import logging
import math
from http import HTTPStatus
from typing import Any
import async_timeout
from aiohttp import ClientError, ClientSession, BasicAuth
from xml.dom import minidom
import xml.etree.ElementTree as ET

HTTP_HEADERS: dict[str, str] = {"Content-Encoding": "gzip"}

log = logging.getLogger(__name__)

class EasyCon:
    """ Main class to perform EasyCon API requests."""

    def __init__(self, url: str, user: str = 'waterkotte', password: str = 'waterkotte', session: ClientSession = None) -> None:
        self._url = url
        self._timeout = 5
        self._session = session
        self._xml_data_root = None
        self._aI105_series = None
        self._aI110_id = None

        log.debug('init')

        self._auth = BasicAuth(user, password)

        # http://192.168.158.203/http/easycon/hpType.csv

    def set_data(self, xml_data, id_series):
        """Set data"""
        self._xml_data_root = xml_data
        self._aI105_series = id_series['aI105_series']
        self._aI110_id = id_series['aI110_id']
    # def __init__(self, xml_data_root):
    #     self._xml_data_root = xml_data_root

    def async_get_basic_information(self):
        """Get basic information from heatpump"""
        if self._xml_data_root is None:
            raise Exception('No data fetched, please fetch data first!')
        # data = minidom.parseString(xml_content)
        # log.info(f'{data.=}')
        # await self._async_get_data()

        firmware_raw = self.get_integer_value(1)
        major = math.floor(firmware_raw / 1e4)
        minor = math.floor((firmware_raw - 1e4 * major) / 100)
        patch = math.floor(firmware_raw - 1e4 * major - 100 * minor)
        firmware = f"{major:02}.{minor:02}.{patch:02}"

        series = self._aI105_series[self.get_integer_value(105)]
        id = self._aI110_id[self.get_integer_value(110)]
        # i_build = +integers[2],
        # i_build > 415 && integers[3] < 643 && (i_minor -= 1, i_patch += 100),

        return {
            'firmware': firmware,   # I1
            'series': series,       # I105
            'id': id,               # I110
        }
        # log.info(f"bios bersion: {bios_version=}")

        # log.info(f"series: {self.get_integer_value(105)}")

    def get_digital_value(self, index: int) -> bool:
        xpath = f".//DIGITAL/VARIABLE[INDEX='{index}')]/VALUE"
        data = self._xml_data_root.findall(xpath)
        log.trace(f"{data=}")
        return data[0]

    def get_analog_value(self, index: int) -> float:
        xpath = f".//ANALOG/VARIABLE[INDEX='{index}')]/VALUE"
        return 0.0

    def get_integer_value(self, index: int) -> int:
        xpath = f".//INTEGER/VARIABLE[INDEX='{index}']/VALUE"
        data = self._xml_data_root.findall(xpath)

        return int(data[0].text)

    async def _async_get_data(self):
        """Retrieve data from API."""
        url = f'{self._url}config/xml.cgi?D%7C1%7C1350%7CA%7C1%7C1700%7CI%7C1%7C3100'
        async with self._session.get(url, auth=self._auth, headers=HTTP_HEADERS) as resp:
            if resp.status == HTTPStatus.UNAUTHORIZED.value:
                raise ApiError("Authentication failed")
            if resp.status != HTTPStatus.OK.value:
                # pylint: disable=no-member
                # error_text = orjson.loads(await resp.text())
                # if error_text["Message"] == REQUESTS_EXCEEDED:
                #     raise RequestsExceededError(
                #         "The allowed number of requests has been exceeded"
                #     )
                raise ApiError(f"Invalid response from EasyCon API: {resp.status}")
            log.debug("Data retrieved from %s, status: %s", url, resp.status)
            data = await resp.text()

        self._xml_data_root = ET.ElementTree(ET.fromstring(data))
            # data = await resp.json(loads=orjson.loads)  # pylint: disable=no-member
        # if resp.headers["RateLimit-Remaining"].isdigit():
        #     self._requests_remaining = int(resp.headers["RateLimit-Remaining"])

        # if "hourly" in url:
        #     return data

        # return data if isinstance(data, dict) else data[0]

class ApiError(Exception):
    """Raised when API request ended in error."""

    def __init__(self, status: str) -> None:
        """Initialize."""
        super().__init__(status)
        self.status = status