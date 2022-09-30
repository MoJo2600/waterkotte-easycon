"""Tests"""
import os
import sys
import csv
sys.path.insert(0 , os.path.abspath('src'))

import pytest
import xml.etree.ElementTree as ET
from waterkotte_easycon import EasyCon


@pytest.fixture
def xml_data_file():
    """Get sample XML"""
    return f"{os.path.dirname(os.path.abspath(__file__))}/fixtures/testdata.xml"

# @pytest.fixture
# def hp_types_file():
#     """Get device types"""
#     return f"{os.path.dirname(os.path.abspath(__file__))}/fixtures/hpTypes.csv"


def test_read_xml(xml_data_file):
    easycon = EasyCon('foo')
    easycon.parse_xml_data(xml_data_file)


# @pytest.mark.asyncio
# def test_read_basic_info(xml_content, hp_types_file, xml_data_file):
#     """Test basic info"""
#     easycon = EasyCon('foo',
#                       hp_types_file=hp_types_file,
#                       xml_data_file=xml_data_file)

#     # easycon.load_data() # would download data
#     # easycon.set_data(xml_content, id_series)

#     basic_info = easycon.async_get_basic_information()
#     print(f"{basic_info=}")

#     assert basic_info['firmware'] == '01.08.96'
