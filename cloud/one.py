import xmlrpclib
import xml.etree.cElementTree as etree
from settings import CLOUD_ENDPOINT, CLOUD_AUTH


class OpenNebula(object):

    tpl = '''
CPU = 1
VCPU = 1
MEMORY = 2048
RANK = "- RUNNING_VMS"
DISK = [
source   = "%(image)s",
target   = "hda",
save     = no,
readonly = "no",
driver = "raw"
]
DISK = [
type     = swap,
size     = 2048,
target   = "hdb",
readonly = "no"
]
NIC = [ network_uname=oneadmin,network = "public" ]
GRAPHICS = [
port = "-1",
type = "vnc"
]
CONTEXT = [
public_key = "%(ssh_key)s",
%(params)s
target = "hdd"
]
''''

    @property
    def rpc(self):
        if not hasattr(self, '_rpc'):
            self._rpc = xmlrpclib.ServerProxy(CLOUD_ENDPOINT)
        return self._rpc

    def start(self, image, ssh_key, params=None):
        params = params or []
        expanded_params = ''
        for key, value in params.items():
            expanded_params += '%s = "%s",\n' % (key, value)
        success, vm_id, _ = self.rpc.one.vm.allocate(CLOUD_AUTH, tpl %
                                                     {'image': image,
                                                      'ssh_key': ssh_key,
                                                      'params':
                                                      expanded_params})
        if not success:
            raise Exception(vm_id)
        return vm_id

    def stop(self, vm_id):
        results = self.rpc.one.vm.action(CLOUD_AUTH, 'finalize', vm_id)
        if not results[0]:
            raise Exception(len(results) > 1 and results[1] or 'No details available')

    def state(self, vm_id):
        info = self._info(vm_id)
        # TODO: Parse XML state

    def ip(self, vm_id):
        return self._info(vm_id).find('TEMPLATE/NIC').find('IP').text

    def _info(self, vm_id, xml=True):
        success, info, _ = self.rpc.one.vm.info(CLOUD_AUTH, vm_id)
        return xml and etree.fromstring(info.encode('utf-8')) or info
