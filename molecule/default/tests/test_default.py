import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_nginx_is_installed(host):
    nginx = host.package('openresty')

    assert nginx.is_installed


def test_nginx_is_running(host):
    nginx = host.service('openresty')

    assert nginx.is_running


def test_nginx_is_enabled(host):
    nginx = host.service('openresty')

    assert nginx.is_enabled
