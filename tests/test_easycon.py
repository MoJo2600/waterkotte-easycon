"""Tests"""
import os
import sys
import csv
# sys.path.insert(0 , os.path.abspath('src'))

import pytest
import xml.etree.ElementTree as ET
from easycon import EasyCon

@pytest.fixture
def xml_content():
    """Get sample XML"""
    tree = ET.parse(f"{os.path.dirname(os.path.abspath(__file__))}/fixtures/testdata.xml")
    root = tree.getroot()
    return root

@pytest.fixture
def id_series():
    """Get device types"""
    
    aI110_id = []
    aI105_series = []
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/fixtures/hpTypes.csv", mode ='r')as file:
        csvFile = csv.reader(file, delimiter=';')
        for lines in csvFile:
            aI105_series.append(lines[2])
            aI110_id.append(lines[1])
    return {
        'aI105_series': aI105_series,
        'aI110_id': aI110_id^^
    }


@pytest.mark.asyncio
def test_read_basic_info(xml_content, id_series):
    """Test basic info"""
    easycon = EasyCon('foo')
    easycon.set_data(xml_content, id_series)

    basic_info = easycon.async_get_basic_information()
    print(f"{basic_info=}")

    assert basic_info['firmware'] == '01.08.96'