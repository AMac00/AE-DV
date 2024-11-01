from camelot.encoder import encoder


class CamelotVapiUtils(object):

    def __init__(self):
        pass

    def _binary_to_boolean(self, result):
        if result == '0':
            return False
        if result == '1':
            return True
        return result

    def _convert_hex_to_int(self, hex_str):
        int_val = int(hex_str, 16)
        if int_val > 0x7FFFFFFF:
            int_val -= 0x100000000
        return int_val

    def _is_valid_call_ref(self, call_ref_str):
        try:
            int(call_ref_str, 16)
            return True
        except ValueError:
            return False

    def _is_valid_integer(self, int_str):
        try:
            int(int_str)
            return True
        except ValueError:
            return False

    def _is_valid_decimal(self, dec_str):
        try:
            float(dec_str)
            return True
        except ValueError:
            return False

    def _query_camelot(self, request, *args, **kwargs):
        self._is_valid_object()
        encoded_msg = encoder.encode(
            request, self.ep_id, *args, **kwargs)
        res = self._get_server_conn().execute_camelot_command(
            request, encoded_msg, request_type='ep')
        return res
