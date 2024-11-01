'''
Created on 20-March-2020
@author: shihashi
'''
from cryptography.fernet import Fernet
from camelot import VAPIEIUtils
from camelot import camlogger
from camelot import CamelotError

log = camlogger.getLogger(__name__)


class CamelotCrypto:
    def __init__(self, vapi_version_file='vapi_ei_utils.py'):
        # key = Fernet.generate_key()
        self.key = 'PkK0Sdg7FKlAOY_6XiZbZIvxeiPaCs1bXUhurPuiFjM='
        self.vapi_version_file = vapi_version_file

    def encrypt_version(self):
        '''
        This method is used to encrypt version string
        '''
        try:
            data = None
            encrypted_ver = {}
            if not VAPIEIUtils.CV_BASE or not VAPIEIUtils.CV_PAD:
                raise (CamelotError(
                    'VAPIEIUtils.CLIENT_VERSION_ENC is wrong'))
            cipher_suite = Fernet(self.key)
            encrypted_str = cipher_suite.encrypt(
                VAPIEIUtils.CLIENT_VERSION.encode()).decode()
            encrypted_ver['base'] = encrypted_str[0:60]
            encrypted_ver['pad'] = encrypted_str[60::]
            with open(self.vapi_version_file, 'r') as f:
                data = f.read()
                f.close()
            if not data:
                raise (CamelotError(
                    'cannot read.. data is None'))
            data = data.replace(
                VAPIEIUtils.CV_BASE, encrypted_ver['base'])
            data = data.replace(
                VAPIEIUtils.CV_PAD, encrypted_ver['pad'])
            with open(self.vapi_version_file, 'w') as f:
                f.write(data)
                f.close()
        except Exception as e:
            log.warning("ERROR:ENCRYPTION: {}".format(e))

    def decrypt_version(self):
        try:
            data = None
            if not VAPIEIUtils.CV_BASE or not VAPIEIUtils.CV_PAD:
                raise (CamelotError(
                    'CV_BASE and CV_PAD are not set'))
            cipher_suite = Fernet(self.key)
            encry_data = "{}{}".format(
                VAPIEIUtils.CV_BASE, VAPIEIUtils.CV_PAD)
            decrypted_ver = cipher_suite.decrypt(encry_data.encode())
            return decrypted_ver.decode()
        except Exception as e:
            log.warning("ERROR:DECRYPTION: {}".format(e))

    def validate_version(self):
        decrypted_ver = self.decrypt_version()
        if decrypted_ver != VAPIEIUtils.CLIENT_VERSION:
            log.warning("Version Mismatch package_version:[{}]"
                        " altered_version:[{}]".format(
                            decrypted_ver,
                            VAPIEIUtils.CLIENT_VERSION))
            log.warning("!!!! Camelot does not support this change,"
                        " USE: git checkout <version> !!!!!")
            return False
        log.debug("encrypted version has matched!!")
        return True
# call this to encrypt version
# e = CamelotCrypto()
# e.encrypt_version()
