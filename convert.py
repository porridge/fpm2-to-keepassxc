#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import logging
import sys


log = logging.getLogger(__name__)


def convert(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    if root.tag != 'FPM':
        raise Exception('Unexpected root element %s' % root.tag)
    for child in root:
        if child.tag in ['KeyInfo', 'LauncherList']:
            if child:
                log.warning('Skipping element %s', child.tag)
        elif child.tag == 'PasswordList':
            pwlist = ET.Element('pwlist')
            convert_passwords(child, pwlist)
            ET.ElementTree(pwlist).write(sys.stdout, encoding='unicode', xml_declaration=True)
        else:
            log.fatal('Unexpected element %s', child.tag)


TAG_MAP = dict(
    title='title',
    user='username',
    url='url',
    password='password',
    notes='notes',
    category='group',
    launcher=None,
)


def convert_passwords(input_list, output_list):
    for input_element in input_list:
        output_element = ET.SubElement(output_list, 'pwentry')
        for attribute in input_element:
            if attribute.tag not in TAG_MAP:
                log.fatal('Unknown tag %s', attribute.tag)
            output_attribute = ET.SubElement(output_element, TAG_MAP[attribute.tag])
            if attribute.text:
                output_attribute.text = attribute.text


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname).1s%(asctime)s.%(msecs)03d] %(message)s',
        datefmt='%m%d %H:%M:%S'
    )
    convert(sys.argv[1])
