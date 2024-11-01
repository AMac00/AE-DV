import camelot
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger, CamelotError

log = camlogger.getLogger(__name__)


class CamelotButtonOperation(v.CamelotVapiUtils):

    '''Camelot Button operations'''

    def __init__(self):
        pass

    def press_button(self, button_number, callref=None):
        '''presses the button number.callref is optional.
        if callref is provided, the button function will be applied to
        the given callref. If no callref is
        provided, the button function will be applied to
        the current active (i.e. connected) callref.
        For DPARK,
        if phone is in connected state, call will be parked to the
        park number configured on button.
        if phone is in idle state(ie. disconnected or no calls), retrieve
        operation will be performed.

        :parameter button_number: button number which needs to be pressed.
                                  this is a mandatory parameter.

        :parameter callref: callref of an active call.Default value is None.

        :returns: if successful, true will be returned.
                  in case of dpark, if successful true is returned. if failure
                  following exceptions are raised:\n
                  * feature DN not implemented for press_button.
                  * feature privacy BLF not implemented for press_button.
                  * feature not implemented for press_button - any other
                    feature.
                  * blf call park failed on dpark button- phone is not
                    connected/idle.
                  * invalid button number - if the button number is not
                    configured.

        >>> ep1.press_button(2)
            True
        >>> ep1.press_button(1)
            CamelotError: feature DN not implemented for press_button.
        >>> ep1.press_button(188)
            CamelotError: invalid button number.
        '''
        if not button_number:
            raise camelot.CamelotError('Invalid button number')
        try:
            button_number = int(button_number)
        except Exception:
            raise camelot.CamelotError('Invalid button number')
        kwargs = {'button_id': 'button',
                  'button_val': button_number,
                  'callref': callref}
        return self._query_camelot(camelot.PRESS_BUTTON, **kwargs)

    def get_button(self, button_number=0):
        ''' returns a dictionary of button info for the line associated with
        the button_number.

        :parameter button_number: button_number of the phone as configured on
                                  CUCM.Default value is 0.

        :returns:  returns a dictionary for the line associated with the
                   button_number. If button number=0, a list of all button
                   info dictionaries configured for that end point is returned.
                   In case of invalid button number, invalid button number
                   exception will be thrown.\n
                   button information provided is as follows:\n
                   * button_number: the number parsed from "button"
                     e.g. <line  button="1" lineIndex="1">
                   * feature_id: number parsed from <featureID> tag.
                   * feature_label: parsed from <featureLabel> tag.
                   * speed_dial_number: parsed from
                     <speedDialNumber> tag.
                   * contact: parsed from <contact> tag.
                     pkid of the number. This value is used for multiple
                     purposes. For BLF directed call park, the endpoint will
                     register for presence for this contact id.
                   * retrieval_prefix: parsed from <retrievalPrefix> tag.
                   * name: parsed from <name> tag.This is legacy dpark code for
                     older phones. Either speed_dial_number or name must
                     be present to represent the park code.

        >>> ep1.get_button(2)
            {
            'button_number': '2',
            'feature_id': '22',
            'feature_label': 'dpark',
            'speed_dial_number': '2222',
            'contact': '348138d6-d468-eefb-e731-734ae2c4ec9b',
            'retrieval_prefix': '#',
            'name': '',
            }
        >>> ep1.get_button()
            [{
             'button_number': '1',
             'feature_id': '9',
             'feature_label': 'DN',
             'speed_dial_number': '',
             'contact': '182d7b7b-eb93-26c2-1df9-2881950db6cf',
             'retrieval_prefix': '',
             'name': '725011',
            },
             {
             'button_number': '2',
             'feature_id': '22',
             'feature_label': 'dpark',
             'speed_dial_number': '2222',
             'contact': '348138d6-d468-eefb-e731-734ae2c4ec9b',
             'retrieval_prefix': '#',
             'name': '',
            }]
        >>> ep1.get_button(188)
            CamelotError: invalid button number.
        '''
        log.debug('Entering get_button function')
        try:
            button_number = int(button_number)
        except Exception:
            raise camelot.CamelotError('Invalid button number')
        kwargs = {'button_id': 'button',
                  'button_val': button_number}
        return self._query_camelot(camelot.GET_BUTTON, **kwargs)

    def get_button_blf(self, button_number=0):
        '''
        get the status of the blf button.

        :parameter button_number: button number for getting the status
                                  This takes integer value.
                                  Default value is 0.

        :returns: returns a dictionary containing the status of the buttons
                  if button_number is None, then all buttons and their
                  status is returned as a list of dictionaries.
                  if button_number is provided, only that button's status
                  is returned as a list of a single dictionary. In case of
                  invalid button number, invalid button number exception
                  will be thrown.
                  button info returned is as follows:\n
                  * button_number: this is the button number.
                  * feature_label: feature label mapped to the button.
                  * line_blf:  presence status (or call status) of the
                    line.  For BLF directed call park, this will be
                    retrieved from NOTIFY messages for the presence updates
                    for the BLF park code assigned to the button. status
                    for CUCM are busy, idle and for CMS are busy, alerting
                    and idle.

        >>> ep1.get_button_blf()
            [{
             'button_number': '1',
             'feature_label': 'DN',
             'line_blf': '',
             },
             {
             'button_number': '2',
             'feature_label': 'dpark',
             'line_blf': 'idle',
             }]
        >>> ep1.get_button_blf(2)
            {
            'button_number': '2',
            'feature_label': 'dpark',
            'line_blf': 'idle',
            }
        >>> ep1.get_button_blf(188)
            CamelotError: invalid button number.
        '''
        log.debug('Entering get_button_blf function')
        try:
            button_number = int(button_number)
        except Exception:
            raise camelot.CamelotError('Invalid button number')
        kwargs = {'button_id': 'buttonblf',
                  'button_val': button_number}
        return self._query_camelot(camelot.GET_BUTTON, **kwargs)

    def get_single_button_barge(self):
        '''
        returns an interger value found in the phone's downloaded
        config for the element <singleButtonBarge>.

        :returns: In success scenario,
                  following integer values are returned -\n
                  * 0 - if single button barge is disabled.
                  * 1 - if barge is enabled.
                  * 2 - if cbarge is enabled.
                  In failure scenario, if tag not present
                  None is returned, else if tag present but no tag
                  value 255 will be returned.

        >>> ep1.get_single_button_barge()
            1
        >>> ep1.get_single_button_barge()
            255
        >>> ep1.get_single_button_barge()
        '''
        log.debug('Entering get_single_button_barge function')
        return self._query_camelot(camelot.GET_SINGLE_BUTTON_BARGE)
