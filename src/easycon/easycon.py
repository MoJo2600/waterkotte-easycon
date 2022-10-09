"""
Module
"""
import logging
import os
import math
from http import HTTPStatus
from typing import Any
import async_timeout
from aiohttp import ClientError, ClientSession, BasicAuth
from xml.dom import minidom
import xml.etree.ElementTree as ET
import csv

HTTP_HEADERS: dict[str, str] = {"Content-Encoding": "gzip"}

# logging.basicConfig(level=logging.DEBIG)
log = logging.getLogger(__name__)

class EasyCon:

    async def get_data(self):
        # Load types file if given
        if self._hp_types_file is not None:
            EasyCon._load_hp_types(self._hp_types_file, self._data)

        if self._xml_data_file is not None:
            self._parse_xml_data(self._xml_data_file)
        else:
            try:
                await self._async_get_data()
            except:
                log.exception('')
                
        # http://192.168.158.203/http/easycon/hpType.csv

        return self._data['values']

    """ Main class to perform EasyCon API requests."""
    @classmethod
    def set_value(cls, idx, value, data):
        if not idx in data['values']:
            data['values'][idx] = {
                'value': None
            }
        data['values'][idx]['value'] = value

    @classmethod
    def _parse_i1_firmware(cls, idx, value, data):
        firmware_raw = int(value)
        major = math.floor(firmware_raw / 1e4)
        minor = math.floor((firmware_raw - 1e4 * major) / 100)
        patch = math.floor(firmware_raw - 1e4 * major - 100 * minor)
        cls.set_value(idx, f"{major:02}.{minor:02}.{patch:02}", data)

    def __init__(self, ip: str, user: str = 'waterkotte', password: str = 'waterkotte', session: ClientSession | None = None, hp_types_file: str | None = None, xml_data_file: str | None = None) -> None:
        self._url = f"http://{ip}/"
        self._timeout = 5
        self._session = session
        self._hp_types_file = hp_types_file
        self._xml_data_file = xml_data_file

        self._data = {
            'aI105_series': [],
            'aI110_series': [],
            'values': {}
        }

        with open(f"{os.path.dirname(os.path.abspath(__file__))}/variables.csv", mode='r', encoding='UTF8') as file:
            csvFile = csv.reader(file, delimiter=';')
            for lines in csvFile:
                self._data['values'][lines[0]] = {
                    'unit': lines[1],
                    'description': lines[2]
                }

        # Special parse method for given index
        self._parse_methods = {
            # 'A25': EasyCon.set_analog_value,
            'I1': EasyCon._parse_i1_firmware,
            # 'aI105_series = id_series['aI105_series']
            # self._aI110_id = id_series['aI110_id']
            # '26': set_analog_value,
            # '27': set_analog_value,
        }

        log.debug('init')

        self._auth = BasicAuth(user, password)


    def _parse_xml_data(self, xml_data_file):
        """
        Load XML data from file
        """
        with open(xml_data_file, 'r', encoding='UTF8') as xml_file:
            section: str = None
            for event, elem in ET.iterparse(xml_file, events=['start', 'end']):
                if event == 'start':
                    if elem.tag in ['ANALOG', 'INTEGER', 'DIGITAL']:
                        section = elem.tag[:1]

                if event == 'end':
                    index = None
                    value = None
                    if elem.tag == 'VARIABLE':
                        for child in elem:
                            if child.tag == 'INDEX':
                                index = f"{section}{child.text}"
                            if child.tag == 'VALUE':
                                value = child.text

                        if index in self._parse_methods:
                            # special parse methods
                            self._parse_methods[index](
                                index, value, self._data)
                        elif section == 'A':
                            # default for analog
                            EasyCon.set_value(index, float(value), self._data)
                        elif section == 'D':
                            # default for digital
                            EasyCon.set_value(index, bool(value), self._data)
                        elif section == 'I':
                            # default for integer
                            EasyCon.set_value(index, int(value), self._data)

        # for key in self._analog_variables.keys():
        #     print(f"{key=} : {self._analog_variables[key]['value']}")

    @classmethod
    def _load_hp_types(cls, hp_types_file, data):
        """
        Load hp types from file and store them in data
        """
        # self._aI110_ids = []
        # self._aI105_series = []
        with open(hp_types_file, mode='r') as file:
            csvFile = csv.reader(file, delimiter=';')
            for lines in csvFile:
                data['aI105_series'].append(lines[2])
                data['aI105_ids'].append(lines[1])

    async def _async_get_data(self):
        """Retrieve data from API."""
        filename = f"{os.path.dirname(os.path.abspath(__file__))}/data.xml"
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
                raise ApiError(
                    f"Invalid response from EasyCon API: {resp.status}")
            log.debug("Data retrieved from %s, status: %s", url, resp.status)

            with open(filename, 'wb') as fd:
                async for chunk in resp.content.iter_chunked(1024):
                    fd.write(chunk)

        self._parse_xml_data(filename)
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
