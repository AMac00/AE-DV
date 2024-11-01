import camelot
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger, CamelotError

log = camlogger.getLogger(__name__)


class CamelotCasOperation(v.CamelotVapiUtils):

    '''Camelot Cas operations'''

    def __init__(self):
        pass

    def get_cas_call_time_statistics(self, call_ref):
        ''' This API applicable only for CAS endpoint.  This will display the
        CAS call time statisticts.Time stats are based on Diva call states.

        :parameter call_ref: valid call reference.

        :returns: dictionary of call time statistics or error string.\n
                    Possible error values are:\n
                    * bad call reference
                    * endpoint does not support this feature.
                    * no data available.

        :states: Please refer Diva SDK guide for more information on
                 Diva call states.\n
                    * DivaCallStateDialingTime: (Calling party)
                    Time captured in DivaCallStateDialing.\n
                    * DivaCallStateProceedingTime: (Calling Party)
                    Time captured in DivaCallStateProceeding.\n
                    * DivaCallStateRingingTime: (Calling party)
                    Time captured in DivaCallStateRinging.\n
                    * DivaCallStateOfferingTime: (Called Party)
                    Time captured in DivaCallStateOffering.\n
                    * DivaCallStateAnsweredTime: (Called Party)
                    Time captured in DivaCallStateAnswered.\n
                    * DivaCallStateConnectedTime: (Calling and Called Party)
                    Time captured in DivaCallStateConnected.\n
                    * DivaCallStateDisconnectingTime: (Calling and Called
                    Party) Time cptured in DivaCallStateDisconnecting.\n
                    * DivaCallStateDisconnectedTime: (Calling and Called Party)
                    Time captured in DivaCallStateDisconnected.

        >>> ep1.vapi.get_cas_call_time_statistics('0xf5722cac')
        >>> {'answered time': '1501781535823',
            'connected time': '1501781536250',
            'disconnected time': '1501781546944',
            'offering time': '1501781535191',
            'proceeding time': '0',
            'disconnecting time': '1501781546926',
            'dialing time': '0',
            'ringing time': '0'}

        :Note: The captured times are in Milliseconds. Example to
               convert into printable format is as below.\n

        >>> In [1]: import datetime
        >>> In [2]: s = 1501781546926 / 1000.0
        >>> In [3]: t = datetime.datetime.fromtimestamp(s)
        >>> In [4]: t.strftime('%Y-%m-%d %H:%M:%S.%f')
        >>> Out[4]: '2017-08-03 23:02:26.926000'
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('call reference not valid')
            return
        log.debug('Entering get_cas_call_time_statistics function')
        return self._query_camelot(camelot.GET_CAS_CALL_TIME_STATISTICS,
                                   call_ref)

    def start_detect_silence(self, call_ref, silence_dur):
        ''' Currently this API applicable only for CAS endpoint. This enables
        user to start detecting silence on a particular call (on received audio
        media).Once the silence is detected for the duration as provided in
        this API as argument Camelot will notify user with a station-event
        called "silence_detected" with duration and time-stamp.

        :parameter call_ref: valid call reference
        :parameter silence_dur: silence duration (in seconds)

        :returns: True or False

        >>> ep1.vapi.start_detect_silence('0xf5722cac',2)
        >>> True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('start_detect_silence: call reference not valid')
            return

        if silence_dur <= 0:
            log.error('start_detect_silence:: invalid duration provided')
            return
        log.debug('Entering start_detect_silence function')
        return self._query_camelot(
            camelot.START_DETECT_SILENCE, call_ref, silence_dur)

    def send_voice(self, call_ref, file_path, is_continuous=True,
                   sampling_rate=camelot.
                   DivaSamplingRate.DivaSamplingRateNormal):
        ''' Currently this API applicable only for CAS endpoint. This enables
        user to playing voice file on a particular call.

        :parameter call_ref: valid call reference
        :parameter file_path: the voice file name with absolute path
        :parameter is_continuous: It is optional param. If it is True the voice
         file will be played continuously untill stop_sending API is called.
         If set to False then the file will be played only for the duration
         of the file.
         Default value will be True.
        :parameter sampling_rate: optional parameter. It is sampling rate
         used for playing voice file.
         For more reference on use of API please check
         'https://wiki.cisco.com/display/CAMELOT/Analog+ATA-190+Voice+Support'

        :returns: True or False

        >>> ep1.vapi.send_voice('0xf5722cac',"/tmp/Greeting.wav",False,
        camelot.DivaSamplingRate.DivaSamplingRateNormal)
        >>> True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('send_voice: call reference not valid')
            return
        if not file_path:
            log.error('send_voice: file path missing')
            return
        if is_continuous is True:
            msg = '{}'.format('yes')
        else:
            msg = '{}'.format('no')
        if not sampling_rate:
            log.error('send_voice: sampling_rate missing')
        else:
            sample = '{}'.format(sampling_rate.value)
        log.debug('Entering send_voice function')
        return self._query_camelot(
            camelot.SEND_VOICE, call_ref, file_path, msg, sample)

    def stop_sending(self, call_ref):
        ''' Currently this API applicable only for CAS endpoint. This enables
        user to stop streaming media which is being streamed currently.

        :parameter call_ref: valid call reference

        :returns: True or False

        >>> ep1.vapi.stop_sending('0xf5722cac')
        >>> True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('send_voice: call reference not valid')
            return
        log.debug('Entering stop_sending function')
        return self._query_camelot(
            camelot.STOP_SENDING, call_ref)

    def record_voice(self, call_ref, file_name,
                     audio_format=camelot.DivaAudioFormat.
                     DivaAudioFormat_Raw_aLaw8K8BitMono):
        ''' Currently this API applicable only for CAS endpoint. This enables
        user to record voice in a particular call by calling
        DivaRecordVoiceFile.
        Please refer to following wiki:
        'https://wiki.cisco.com/display/CAMELOT/Analog+ATA-190+Voice+Support'

        :parameter call_ref: valid call reference
        :parameter file_name: absolute path based filename where recording
         to be stored.
        :parameter audio_format: optional para for audio format to be used

        :returns: True or False

        >>> ep1.vapi.record_voice('0xf5722cac','/tmp/myrecord.wav'
            audio_format=
            camelot.DivaAudioFormat.DivaAudioFormat_Raw_aLaw8K8BitMono)
        >>> True
        '''
        if not call_ref or not self._is_valid_call_ref(call_ref):
            log.error('record_voice: call reference not valid')
            return

        if not file_name:
            log.error('record_voice: file name missing')
            return

        if not audio_format:
            log.error('record_voice: audio_format missing')
        else:
            audioformat = '{}'.format(audio_format.value)

        log.debug('Entering record_voice function')
        return self._query_camelot(
            camelot.RECORD_VOICE, call_ref, file_name, audioformat)
