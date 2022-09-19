"""Tests"""
import os
import sys
sys.path.insert(0 , os.path.abspath('src'))

import pytest
import xml.etree.ElementTree as ET
from easycon import EasyCon

@pytest.fixture
def xml_content():
    """Get sample XML"""
    tree = ET.parse(f"{os.path.dirname(os.path.abspath(__file__))}/fixtures/testdata.xml")
    root = tree.getroot()
    return root

@pytest.mark.asyncio
def test_read_basic_info(xml_content):
    """Test basic info"""
    easycon = EasyCon('foo')
    easycon.set_data(xml_content)

    basic_info = easycon.async_get_basic_information()
    print(f"{basic_info=}")

    assert basic_info['firmware'] == '01.08.96'