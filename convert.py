#!/usr/bin/env python3
"""
Quick and dirty script to convert passwords exported from FPM2 in XML
(unencrypted) format into the keepassxc database format.

Copyright 2021 Marcin Owsiany <marcin@owsiany.pl>

Requires https://github.com/libkeepass/pykeepass to work.

Usage: ./convert.py file-exported-from-fpm2.xml new-keepassxc-database-to-be-created.kdbx

The script interactively asks for a password for the new password database.
Please remember to securely remove your old unencrypted export file afterwards
with some tool like `shred`!



Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of the University nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
"""

import xml.etree.ElementTree as ET
import logging
import sys

from pykeepass import create_database


log = logging.getLogger(__name__)


def convert(in_filename, out_filename):
    tree = ET.parse(in_filename)
    root = tree.getroot()
    if root.tag != 'FPM':
        raise Exception('Unexpected root element %s' % root.tag)
    for child in root:
        if child.tag in ['KeyInfo', 'LauncherList']:
            if child:
                log.warning('Skipping element %s', child.tag)
        elif child.tag == 'PasswordList':
            kp = create_database(out_filename, input('Enter db password:'))
            convert_passwords(child, kp)
            logging.info('Saving database...')
            kp.save()
            logging.info('All done.')
        else:
            log.fatal('Unexpected element %s', child.tag)


TAG_MAP = dict(
    title='title',
    user='username',
    url='url',
    password='password',
    notes='notes',
    category=None,
    launcher=None,
)


def convert_passwords(input_list, output_db):
    for input_element in input_list:
        entry = {}
        for attribute in input_element:
            tag = attribute.tag
            logging.debug('read attribute %s of %s', tag, input_element)
            if tag not in TAG_MAP:
                log.fatal('Unknown tag %s', tag)
            if attribute.text:
                if TAG_MAP[tag]:
                    entry[TAG_MAP[tag]] = attribute.text
                else:
                    logging.info('ignoring attribute %s of element %s', tag, entry.get('title', entry.get('url', 'unknown')))
        if 'title' not in entry:
            entry['title'] = entry['url']
        if 'username' not in entry:
            entry['username'] = '(no username)'
        if 'password' not in entry:
            entry['password'] = '(no password)'

        title = entry['title']
        username = entry['username']
        password = entry['password']
        del entry['title']
        del entry['username']
        del entry['password']
        output_db.add_entry(output_db.root_group, title, username, password, **entry)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname).1s%(asctime)s.%(msecs)03d] %(message)s',
        datefmt='%m%d %H:%M:%S'
    )
    convert(sys.argv[1], sys.argv[2])
