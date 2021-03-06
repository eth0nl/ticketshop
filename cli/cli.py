#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import readline
import requests
import sys
import traceback
from datetime import datetime

from colorama import Fore
from dateutil.parser import parse

formatter = logging.Formatter('%(asctime)s %(message)s')
handler = logging.FileHandler(os.path.expanduser("~/.ticketscan.log"))
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class Completer(object):
    def __init__(self, accountsfile):
        self.input_state = 'ticket'
        self.accountsfile = accountsfile

    def complete(self, text, state):
        if self.input_state != 'baruser':
            return None

        if state == 0:
            self.matches = [account['name'] for account in get_accounts(self.accountsfile)
                            if account['name'].startswith(text)]

        try:
            return self.matches[state]
        except IndexError:
            return None


def get_accounts(accountsfile):
    accounts = []
    with open(accountsfile) as f:
        for line in f.readlines():
            l = line.strip().split()
            accounts.append({'name': l[0],
                             'balance': float(l[1]),
                             'timestamp': parse(l[2].replace('_', ' '))})

    return accounts


def account_add(accountsfile, name, amount):
    outfile = '.revbank.%s' % os.getpid()
    with open(accountsfile) as in_fd, open(outfile, 'w') as out_fd:
        found = False

        for line in in_fd.readlines():
            l = line.strip().split()
            if l[0] == name:
                found = True
                new_balance = float(l[1]) + amount
                out_fd.write("%-16s %+9.2f %s\n" % (l[0], new_balance, datetime.now().strftime("%Y-%m-%d_%H:%M:%S")))
                message = "Adding %.2f to %s, old balance was %.2f, new balance is %.2f" % (amount, name, float(l[1]), new_balance)
                logger.info(message)
                print(message)
            else:
                out_fd.write(line)

        if not found:
            out_fd.write("%-16s %+9.2f %s\n" % (name, amount, datetime.now().strftime("%Y-%m-%d_%H:%M:%S")))
            message = "Creating a%s with balance %.2f" % (name, amount)
            logger.info(message)
            print(message)

    os.rename(outfile, accountsfile)


def do_ticket(accountsfile, url, apikey):
    ticket_id = raw_input('Enter ticket code >>> ')
    r = requests.post(url, data={'api_key': apikey, 'ticket_id': ticket_id})
    result = r.json()
    if result['result'] == 'valid':
        logger.info('valid ticket from %s with id %s' % (result['username'], ticket_id))
        print(Fore.GREEN + 'Valid ticket from ' + result['username'])
        for ticket in result['tickets']:
            print("{count}x {name}".format(**ticket))
        if result['bar_credits']:
            print("€ {} bar credits".format(result['bar_credits']))
            completer.input_state = 'baruser'
            print(Fore.RESET, end='')
            baruser = raw_input('Enter baruser >>> ')
            account_add(accountsfile, baruser, result['bar_credits'])
    elif result['result'] == 'used':
        print(Fore.RED + "Ticket already used")
    else:
        print(Fore.RED + "Ticket not found")


if __name__ == "__main__":
    # Clear screen
    print('\x1b[H\x1b[2J')
    logger.info("Starting up")

    url = sys.argv[1]
    accountsfile = sys.argv[2]

    completer = Completer(accountsfile)
    readline.parse_and_bind('tab: complete')
    readline.set_completer(completer.complete)

    with open(os.path.expanduser("~/.api_key")) as f:
        apikey = f.read().strip()

    while True:
        try:
            do_ticket(accountsfile, url, apikey)
        except KeyboardInterrupt:
            print()
        except:
            print(Fore.YELLOW)
            print(traceback.format_exc())
        finally:
            print(Fore.RESET, end='')
