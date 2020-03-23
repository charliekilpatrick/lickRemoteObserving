import logging
import getpass
from lick_vnc_launcher import create_logger, LickVncLauncher, create_parser
import pytest


# create lvl object
create_logger()
lvl = LickVncLauncher()
lvl.log = logging.getLogger('KRO')
lvl.log_system_info()
lvl.args = create_parser()
lvl.get_config()
lvl.check_config()
if lvl.config.get('nosshkey', False) is True:
    vnc_account = lvl.args.account
    lvl.vnc_password = getpass.getpass(f"\nPassword for user {vnc_account}: ")

servers_and_results = [('shimmy', 'shimmy.ucolick.org'),
                       ('noir', 'noir.ucolick.org')
                           ]

def test_firewall_authentication():
    lvl.is_authenticated = False
    if lvl.do_authenticate:
        lvl.firewall_pass = getpass.getpass(f"\nPassword for firewall authentication: ")
        lvl.is_authenticated = lvl.authenticate(lvl.firewall_pass)
        assert lvl.is_authenticated is True


def test_ssh_key():
    if lvl.config.get('nosshkey', False) is not True:
        lvl.validate_ssh_key()
        assert lvl.ssh_key_valid is True


@pytest.mark.parametrize("server,result", servers_and_results)
def test_connection_to_servers(server, result):

    vnc_account = lvl.ssh_account
    vnc_password = None

    lvl.log.info(f'Testing SSH to {vnc_account}@{server}.ucolick.org')
    output = lvl.do_ssh_cmd('hostname', f'{server}.ucolick.org',
                            vnc_account, vnc_password)
    assert output is not None
    assert output != ''
    assert output.strip() in [server, result]
    lvl.log.info(f' Passed')
