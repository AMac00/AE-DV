import logging
from tng.protocol.ssh.endpoint import NewConnectionHelper
from tng.plugins.ssh_plugin import SshPlugin
from twisted.internet import reactor
from tng.device_helpers.addresses import create_addrs_from_str_if_required

log = logging.getLogger('CamelotSshPlugin')


class CamelotSshPlugin(SshPlugin):
    def __init__(self, ip, *args, **kwargs):
        super(CamelotSshPlugin, self).__init__(*args, **kwargs)
        self.ssh_ip = ip

    def activate(self, device, *args, **kwargs):
        def encode(val):
            if isinstance(val, bytes):
                return val
            else:
                return val.encode('utf8')
        d = super(SshPlugin, self).activate(device, *args, **kwargs)
        addrs = create_addrs_from_str_if_required(self.ssh_ip)
        self._connection_helper = NewConnectionHelper(
            reactor, addrs, self.port,
            encode(self.credential.username), self.credential.key,
            encode(self.credential.password), self.open_timeout)
        return d
