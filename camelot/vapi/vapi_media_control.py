import camelot
from camelot.vapi import vapi_camelot_utils as v
from camelot import camlogger
log = camlogger.getLogger(__name__)


class CamelotMediaControl(v.CamelotVapiUtils):

    """Camelot Media Control representation
    """

    def start_dtmf_detector(self, stream_ref):
        """
        Starts and invount stream's DTMF detector.

        Starts a stream's dtmf detector.  To receive dtmf events, the
        dtmf detector must be running. For RTP streams only RFC 2833 DTMF
        packets can be detected.

        :parameter stream_ref: stream reference

        :returns: True if player start is successfully initiated.
         False if an error occurs

        ep1.start_dtmf_detector()
        True
        """
        if stream_ref and not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(camelot.START_DTMF_DETECTOR, stream_ref)

    def stop_dtmf_detector(self, stream_ref):
        """
        stops stream's DTMF detector.

        stops a stream's dtmf detector.

        :parameter stream_ref: stream reference

        :returns: True if player start is successfully initiated.
         False if an error occurs

        >>> ep1.stop_dtmf_detector()
        True
        """
        return self._query_camelot(camelot.STOP_DTMF_DETECTOR, stream_ref)

    def start_dtmf_player(self, digits, ontime=None, offtime=None,
                          stream_ref=None, call_ref=None, medium='inband'):
        """
        Starts playing dtmf digits

        Starts playing the specified dtmf digits on the specified stream/call.
        For inband, only RFC 2833 DTMF packets can be sent.
        Note: Out of band DTMF is supported only for Skinny.

        :parameter digits: dtmf digit string to play
        :parameter ontime: digit on duration in ms
        :parameter offtime: digit off duration in ms
        :parameter stream_ref: stream reference
        :parameter call_ref: call reference
        :parameter medium: It can be inband or oob for inband and out of band
         DTMF respecitvely, default is inband

        :returns: True if player start is successfully initiated.  If an error
         occurs False is returned. Due to server processing delay, the dtmf
         player may not immediately start upon return of this routine.
         A tonestarted event is generated for inband dtmf once the player
         actually begins running.

        >>> ep1.start_dtmf_player()
        True
        """
        medium_list = ['inband', 'oob']
        if medium not in medium_list:
            log.error('invalid medium %s' % medium)
            return None
        if not len(str(digits)):
            log.error('digits not specified')
            return None
        if medium == 'inband':
            if not stream_ref:
                log.error('stream reference not specified')
                return None
            if not self._is_valid_call_ref(call_ref):
                log.error('invalid call reference')
                return None
            if not ontime:
                log.error('digit on-time not specified')
                return None
            if not offtime:
                log.error('digit off-time not specified')
                return None
            if not offtime:
                log.error('digit off-time not specified')
                return None
        elif medium == 'oob':
            if not call_ref:
                log.error('call reference not specified')
                return None
            if not self._is_valid_call_ref(call_ref):
                log.error('invalid call reference')
                return None
        kwargs = {'medium': medium,
                  'call_ref': call_ref,
                  'ontime': ontime,
                  'offtime': offtime,
                  'digits': digits}
        return self._query_camelot(
            camelot.START_DTMF_PLAYER, stream_ref, **kwargs)

    def stop_dtmf_player(self, stream_ref):
        """Stops an active dtmf player.

        :parameter stream_ref: stream reference

        :returns: True if player stop is successfully initiated.
         If an error occurs, False is returned. Once the player ceases
         operation, a tonedone event is generated.

        >>> ep1.stop_dtmf_player()
        True
        """
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(camelot.STOP_DTMF_PLAYER, stream_ref)

    def start_media_events(self, stream_ref):
        """
        Enable the collection of media events on the specified stream.

        :parameter stream_ref: stream reference

        :returns: True on success, Error message on failure

        >>> ep1.start_media_events()
        True
        """
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        log.debug('Registering for Mediaevent on %s' % stream_ref)
        if not stream_ref:
            log.error('Cant register to media events, No stream_ref provided')
            return
        return self._query_camelot(camelot.START_MEDIA_EVENTS, stream_ref)

    def stop_media_events(self, stream_ref):
        """
        Disable the collection of media events on a stream

        :parameter stream_ref: stream reference

        :returns: True on success, Error message on failure

        >>> ep1.stop_media_events()
        True
        """
        if not stream_ref:
            log.error('Cant un-register media events, No stream_ref provided')
            return
        return self._query_camelot(camelot.STOP_MEDIA_EVENTS, stream_ref)

    def start_media_player(self, stream_ref, url, encoding, mode='continuous'):
        '''Start playing media on an outbound stream.If the media player
        is already running it will be stopped and new one will be started.

        Starts playing the specified media file on the specified stream.
        Repeats playing the same file continuously with default mode value.
        However if mode is passed as playonce the media will be played once
        till the end of the file is reached.

        :parameter stream_ref: stream reference.
        :parameter url: URL of media file to play.
        :parameter encoding: encoding of media file
         Supported encodings are:

             * rtp   :      camelot RTP file
             * g711u :       raw G.711 mulaw
             * g711a :       raw G.711 alaw
             * g729  :       raw G.729
             * g729a :       raw G.729A
             * g729b :       raw G.729B
             * g723  :       raw G.723
             * g726_32:      raw G.726 32kps bit rate
             * g722_64:      raw G.722 64kps bit rate
             * wav   :       wav file
        :parameter mode: continuous or playonce

        :returns: True if player start is successfully initiated.
         If an error occurs False is returned or throws an exeception.

        starts media player and plays media continuously:
        >>> ep1.start_media_player(stream_ref = outstreamref,
                url = 'file://root/traffic-h264-384-15-CIF.rtp',
                encoding = 'rtp')
        True
                    OR
        >>> ep1.start_media_player(stream_ref = outstreamref,
                url = 'file://root/traffic.g729a',
                encoding = 'g729a')
        True
        starts media player and plays media once:
        >>> ep1.start_media_player(stream_ref = outstreamref,
                url = 'file://root/traffic.g711u',
                encoding = 'g711u',mode='playonce)
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        kwargs = {'encoding': encoding,
                  'url': url,
                  'mode': mode
                  }

        return self._query_camelot(
            camelot.START_MEDIA_PLAYER, stream_ref, **kwargs)

    def stop_media_player(self, stream_ref):
        '''Stops an active media player.

        Stops a stream's media player.

        :parameter stream_ref: stream reference

        :returns: True if player stop is successfully initiated.
         If an error occurs False is returned.

        >>> ep1.stop_media_player()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(
            camelot.STOP_MEDIA_PLAYER, stream_ref)

        ret_int = self._execute_command(EncodeHelper.STOP_MEDIA_PLAYER,
                                        stream_ref, send_msg=True)

    def start_media_recorder(self, stream_ref, prefix):
        '''Start a stream's media recorder

        Starts a stream's media recorder.  All inbound media
        traffic will be saved to a file. The format of the saved
        file depends upon the endpoint type.  For VoIP endpoints,
        the actual RTP stream is saved, that is the file actually
        contains the received RTP packets with some additional
        timing meta data.

        :parameter stream_ref: stream reference
        :parameter prefix: Prefix for file name used for media recording.
                           The tool chooses the appropriate suffix.

        :returns: True if media recorder start is successfully initiated,
         False for error cases.

        >>> ep1.start_media_recorder()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        kwargs = {'prefix': prefix
                  }
        return self._query_camelot(
            camelot.START_MEDIA_RECORDER, stream_ref, **kwargs)

    def stop_media_recorder(self, stream_ref):
        '''Stops an inbound stream's media recorder.

        :parameter stream_ref: stream reference

        :returns: True if  recorder stop is successfully initiated.
                  If an error occurs False is returned.

        >>> ep1.stop_media_recorder()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(camelot.STOP_MEDIA_RECORDER, stream_ref)

    def start_prompt_detector(self, stream_ref, prompt_type, cache=None,
                              pattern_list=None):
        '''Starts the prompt detector for specified stream_ref parameter.

        :parameter stream_ref: Stream reference
        :parameter prompt_type: Value is sig for signature based prompt
                                detection. Value is bin for binary based
                                RTP prompt detection.
        :parameter cache: Cache handler. To be used for signature
                          based prompt detection only
        :parameter pattern_list: Maximum number of patterns that can be
                                 specified are ten only. If specified
                                 more, the first ten are considered for
                                 prompt detection. The maximum size of the
                                 blob is 200 bytes. If specified more, the
                                 first 200 bytes is considered as blob. To be
                                 used for binary based RTP prompt detection
                                 only.

        :returns: True if detector start is successfully initiated. If an
         error occurs, False is returned.

        Note: 1) Prompt detector stops automatically when a prompt is detected,
        so on successful prompt detection, no need to call stop_prompt_detector
        , if user calls, it will return false.\n
        2). Signature based prompt detection is not supported right now.

        >>> make a successful call and gets connected
        >>> ep1instream =  ep1.get_streams()[0]['StrmID']
        >>> ep1.start_prompt_detector(stream_ref = ep1instream,
                     prompt_type = 'bin', pattern_list =
                     ['CDC9CAC6CDCACBCFE4CAD6D5DAD9E2D5DEC6',
                      '4E4D46494E494F474D4947473F43554E484C514A',
                      '463F3C444D47494A4A4654494C3E3C3B3A3A3D3E3D3B3A'])
        True
                     OR
        >>> serv = camelot.create_camelot_server(CamServIp, CamServPort)
        >>> cache_h = serv.load_prompt_cache('-fmt g711ulaw
                    -v /tmp/srcprompt /tmp/dstprompt/')
        >>> make a successful call and gets connected
        >>> ep1instream =  ep1.get_streams()[0]['StrmID']
        >>> ep1.start_prompt_detector(stream_ref = ep1instream,
                     prompt_type = 'sig', cache = cache_h)
        True

        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        prompt_types = ['sig', 'bin']
        if prompt_type and prompt_type not in prompt_types:
            log.error('Invalid prompt type, should either be "sig" or "bin"')
            return
        if not prompt_type or prompt_type not in prompt_types:
            log.error('destination directory (cache) not specified')
            return
        if prompt_type == 'sig' and not cache:
            log.error('Cache not specified.')
            return
        if prompt_type == 'bin' and (not pattern_list or not pattern_list[0]):
            log.error('Pattern not specified.')
            return

        kwargs = {'prompt_type': prompt_type,
                  'cache': cache,
                  'pattern_list': pattern_list
                  }

        return self._query_camelot(
            camelot.START_PROMPT_DETECTOR, stream_ref, **kwargs)

    def stop_prompt_detector(self, stream_ref):
        '''Stops prompt detector on an inbound stream

        Stops the prompt detector started for specified stream_ref parameter

        :parameter stream_ref: stream reference

        :returns: True if detector stop is successfully initiated.
         If an error occurs, False is returned.

        >>> ep1.stop_prompt_detector()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(camelot.START_PROMPT_DETECTOR, stream_ref)

    def start_tone_detector(self, stream_ref, tone_id, freq, bw=None,
                            freq2=None, bw2=None):
        '''
        Start a tone detector on an inbound stream.

        Initiates start of a tone detector on an inbound stream. The tone
        detector is identified by an integer, 0 to n, specified via tone_id.
        A tone detector must be running to receive tone events.
        Dual frequency tones can be specified via the freq2 option
        (TDM endpoints only).  For RTP streams only g711u(default),
        g711a, g722-64, g7221-32, g7221-24, g723, g728, g729, g729a,
        g729b, g729ab, ilbc20, ilbc30, isac30, isac60 and gsmamr
        codecs are supported for tone detection.

        :parameter stream_ref: stream reference
        :parameter tone_id: integer id, 0 to n, to identify detector
        :parameter freq:  first frequency (Hz) of tone to detect.
        :parameter bw: bandwidth (Hz) of first frequency
        :parameter freq2: second frequency (Hz) of tone to detect
                          (TDM endpoints only)
        :parameter bw2: bandwidth (Hz) of second frequency (TDM endpoints only)

        :returns: True if detector start is successfully initiated otherwise
         False. If an error occurs a CamelotError exception is raised.
         Due to server processing delay, the tone detector may
         not immediately start upon return of this routine.
         A tonedetstarted event is generated once the detector actually
         begins running.  See mediaevent and getmediaevent.

        >>> ep1.start_tone_detector()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        if not self._is_valid_integer(tone_id):
            log.error('invalid tone id')
            return
        '''---------------check------------------'''
        if not self._is_valid_integer(freq):
            log.error('invalid tone id')
            return
        if bw:
            if not self._is_valid_integer(bw):
                log.error('invalid bandwidth')
                return
        else:
            bw = 0
        if freq2:
            if not self._is_valid_integer(freq2):
                log.error('invalid bandwidth')
                return
        else:
            freq2 = 0
        if bw2:
            if not self._is_valid_integer(bw2):
                log.error('invalid bandwidth')
                return
        else:
            bw2 = 0
        kwargs = {'tone_id': tone_id,
                  'freq': freq,
                  'bw': bw,
                  'freq2': freq2,
                  'bw2': bw2
                  }
        return self._query_camelot(
            camelot.START_TONE_DETECTOR, stream_ref, **kwargs)

    def stop_tone_detector(self, stream_ref, tone_id):
        '''Stop a tone detector on an inbound stream

        :parameter stream_ref: stream reference

        :returns: True if detector stop is successfully initiated.
         If an error occurs CamelotError exception is raised.
         When the detector ceases operation, a dtmfdetdone event is generated.
         See media_event and get_media_event.

        >>> ep1.stop_tone_detector()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        if not self._is_valid_integer(tone_id):
            log.error('invalid tone id')
            return
        kwargs = {'tone_id': tone_id
                  }
        return self._query_camelot(
            camelot.STOP_TONE_DETECTOR, stream_ref, **kwargs)

    def start_cadence_detector(self, stream_ref, tone_id, freq, freq2=0):
        '''
        Start a cadence detector on an inbound stream for particular
        frequency.The parameter "freq" takes the frequency value to be
        detected.In case of Dual frequency tones the second frequency should
        be provided with optional parameter "freq2".
        The cadence detector is identified by an integer, 0 to n,
        specified via tone_id. The cadence detector will start detecting media
        tone once there is some traffic in the selected stream. Events will be
        sent to client periodically.The time period can be configured using
        "media.cadencedetect.eventsampleperiod", this is in millisecond.
        If not configured, the default value is 100 (millisecond).

        For RTP streams only g711u(default),
        g711a, g722-64, g7221-32, g7221-24, g723, g728, g729, g729a,
        g729b, g729ab, ilbc20, ilbc30, isac30, isac60 and gsmamr
        codecs are supported for cadence detection.

        Note: All the limitations and conditions applied for
        "start_tone_detector" will also hold true for this API except that
        freq2 is currently not supported for tone detector (for non TDM
        endpoints), whereas cadence detector supports freq2 as well.

        :parameter stream_ref: stream reference
        :parameter tone_id: integer id, 0 to n, to identify detector
        :parameter freq:  frequency (Hz) of tone to detect.
        :parameter freq2: second frequency (Hz) of tone to detect incase of
         dual frequency tone


        :returns: True if detector start is successfully initiated otherwise
         False. If an error occurs a CamelotError exception is raised.
         Due to server processing delay, the tone detector may
         not immediately start upon return of this routine.
         A cadencedetstarted event is generated once the detector actually
         begins running.  See mediaevent and getmediaevent.
         The periodic event sent to client will be cadencereport event.
         It will send event about 'tone' and 'no_tone' on presence and absence
         of tone respectively.

         Example:
         0a669624 2016-12-20T14:31:30.830-05:30 cadencereport 1 tone
         0a669624 2016-12-20T14:31:30.930-05:30 cadencereport 1 no_tone

         For more reference on use of API please check
         'https://wiki.cisco.com/display/CAMELOT/Cadence+Detection+Functionality'

        >>> ep1.start_cadence_detector()
            True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        if not self._is_valid_integer(tone_id):
            log.error('invalid tone id')
            return
        '''---------------check------------------'''
        if not self._is_valid_integer(freq):
            log.error('invalid tone id')
            return

        if freq2:
            if not self._is_valid_integer(freq2):
                log.error('invalid second frequency')
                return

        kwargs = {'tone_id': tone_id,
                  'freq': freq,
                  'freq2': freq2
                  }
        return self._query_camelot(
            camelot.START_CADENCE_DETECTOR, stream_ref, **kwargs)

    def stop_cadence_detector(self, stream_ref, tone_id):
        '''Stop a cadence detector on an inbound stream

        :parameter stream_ref: stream reference

        :returns: True if cadence detector stop is successfully initiated.
         If an error occurs CamelotError exception is raised.
         tonedetdone event is sent to client once cadence
         detector stops.
         See media_event and get_media_event.

        >>> ep1.stop_cadence_detector()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        if not self._is_valid_integer(tone_id):
            log.error('invalid tone id')
            return
        kwargs = {'tone_id': tone_id
                  }
        return self._query_camelot(
            camelot.STOP_CADENCE_DETECTOR, stream_ref, **kwargs)

    def start_tone_player(self, stream_ref, tone_seq=None, tones=None):
        '''
        Start playing tones on an outbound stream.

        Starts playing the specified tonesequence(s) on the specified stream.
        Note that codec used to build toneseq must be compatible with
        stream's encoding, or this procedure will fail.

        :parameter stream_ref: stream reference
        :parameter tone_seq: either a single toneseq handle (to be played
            exactly once) or dictionaries of records of the
            following form: {'toneseq':'', 'iterations':''}\n
            * toneseq: Handle for a tone sequence built with camelot
              create_tone_seq
            * iterations: number of times to play tone sequence,
              0 for indefinitely
        :parameter tones: lists of tones to be played ['1336 1000 500 5',
         ,'697 1000 500 5']\n
            * 1336 1000 500 5 - 1336 is frequency, 1000 is ontime,
              500 is off time, 5 is iteration
        :returns: True if player start is successfully initiated.
             If an error occurs False is returned. Due to server processing
             delay, the tone player may not immediately start upon return
             of this routine.  A tonestarted event is generated once the player
             actually begins running.  Once the tones have been played, a
             tonedone event is generated.

        >>> ep1.start_tone_player()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        str_ref = int(stream_ref, 16)
        if tones:
            if not isinstance(tones, list):
                raise Exception('tones is not passed as a list')
            tone_seq_str = ''
            len_tone_seq = 0
            for tone_seq_handle in tones:
                if not isinstance(tone_seq_handle, str):
                    continue
                if len(tone_seq_handle.strip().split()) != 4:
                    raise Exception('invalid tone[%s]' % tone_seq_handle)
                tone_seq_str += tone_seq_handle + ' '
                len_tone_seq += 1
            if tone_seq_str:
                tone_seq_str = tone_seq_str.strip()
            kwargs = {'len_tone_seq': len_tone_seq,
                      'tone_seq_str': tone_seq_str
                      }
        elif tone_seq:
            if len(tone_seq) < 1:
                log.error('No Tone sequence specified')
                return
            len_tone_seq = 0
            tone_seq_str = ''
            if type(tone_seq) == list:
                for tone_seq_handle in tone_seq:
                    if type(tone_seq_handle) == dict:
                        toneseq = tone_seq_handle.get('toneseq')
                        interations = tone_seq_handle.get('interations')
                    else:
                        continue
                    tone_seq_str += (' ' + toneseq + ' ' + interations)
                    len_tone_seq += 1
            else:
                tone_seq_str = ' ' + tone_seq + ' 1'
                len_tone_seq += 1

            kwargs = {'len_tone_seq': len_tone_seq,
                      'tone_seq_str': tone_seq_str
                      }
        else:
            raise Exception('start_tone_player() parameters are missing')
        return self._query_camelot(
            camelot.START_TONE_PLAYER, str_ref, **kwargs)

    def stop_tone_player(self, stream_ref):
        '''Stops an active tone player.

        :parameter stream_ref: stream reference

        :returns: True if player stop is successfully initiated.
         If an error occurs, False is returned. Once the player ceases
         operation, a tonedone event is generated.

        >>> ep1.stop_tone_player()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(camelot.STOP_TONE_PLAYER, stream_ref)

    def start_traffic_player(self, stream_ref, mode):
        '''
        Starts playing bearer traffic on an outbound stream.

        By default, all audio traffic streams consist of a continuous 130hz
        tone that is encoded for all audio codecs when camserv starts.

        If you'd prefer to have some alternate content for your endpoint's
        outbound audio traffic stream, write a file of the following form to
        Camelot's CamelotInstallDir/lib/media/ directory
        (where CamelotInstallDir is C:/Camelot by default):

        traffic-samplerate.pcm16

        Where samplerate is 16000 when using g722-64, isac-30, or isac-60
        codecs and 8000 when using any other codecs.

        The .pcm16 file must contain some number of signed linear
        16-bit(little-endian) samples without any header/trailer information.
        This file format can be written with a number of free or shareware
        audio tools, such as Microsoft SoundRecorder or the GoldWave audio
        editor a. You must restart camserv after writing these .pcm16 file(s)
        into the media directory.

        Limitations

        Presently, with the exception of CTS eps, media for eps using
        AAC codec is not supported. If the ep is configured to use AAC
        codec, there will be no RTP packets sent over the media stream.
        With CTS ep, AAC media traffic will be sent, however, a
        pre-recorded file of RTP packet is played back and that there
        is no actual encoding/decoding of the media.

        :parameter mode: One of the following values
            * continuous - stream traffic continuously
            * random - stream traffic intermittently
            * playonce - stream traffic once

        :returns: True if player start is successfully initiated.
         If an error occurs False is returned.
         Due to server processing delay, the traffic player may not
         immediately start upon return of this routine. A trafficstarted
         event is generated once the player actually begins running.

         Wiki link: https://wiki.cisco.com/display/CAMELOT/starttrafficplayer

        >>> ep1.start_traffic_player()
        True
        '''
        mode_list = ['random', 'continuous', 'playonce']
        if not mode or mode not in mode_list:
            log.error('mode not specified or invalid')
            return
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        kwargs = {'mode': mode
                  }
        return self._query_camelot(
            camelot.START_TRAFFIC_PLAYER, stream_ref, **kwargs)

    def stop_traffic_player(self, stream_ref):
        '''
        Stops the traffic player.

        Stops an outbound stream's traffic player.

        :parameter stream_ref: stream reference

        :returns: True if player stop is successfully initiated.
         If an error occurs False is returned. Once the player ceases
         operation, a trafficdone event is generated.

        >>> ep1.stop_traffic_player()
        True
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(camelot.STOP_TRAFFIC_PLAYER, stream_ref)

    def release_stream_ref(self, stream_ref):
        '''
        Release/decrement the reference count associated with a stream.

        Decrements the Camelot server's reference count associated with
        a stream.  A stream can not be released or deleted on the server
        unless its reference count is 0 or below. Currently a stream's
        reference count is incremented when a stream event of type
        start is sent to a client application. It is incremented once
        for each client receiving the event. It is the responsibility
        of each client to decrement the reference count via releasestreamref
        when the client is done processing the stream. This ensures the stream
        is not deleted inadvertently via releasestreams or autorelease before
        the client can process the stream.

        :parameter stream_ref: stream reference

        :returns: nothing
        '''
        if not self._is_valid_call_ref(stream_ref):
            log.error('invalid stream reference')
            return
        return self._query_camelot(camelot.RELEASE_STREAM_REF, stream_ref)

    def send_tones(self, stream_ref, tone_type, frequencies=[],
                   continuous_tone='-1', tone_duration=0, frequencyA=-1,
                   amplituteA=65536, frequencyB=-1, amplituteB=65536):
        '''
        This API is used for CAS Endpoints to send tones.

        :parameter stream_ref: Valid stream ref reference to send tone.
                               It should be of outbound stream reference.
        :parameter tone_type: Type of tone to be sent.
                                Valid values are:\n
                                * camelot.Tones.ToneType.continuousTone
                                * camelot.Tones.ToneType.multiFrequencyTone
                                * camelot.Tones.ToneType.singleTone
                                * camelot.Tones.ToneType.dualTone
        :parameter frequencies: This parameter is valid only for multifreuqncy
                                tones.   Maximum count of frequencies
                                in a list is 12.  Valid Values are:\n
                                * camelot.Tones.DivaMF.tone1
                                * camelot.Tones.DivaMF.tone2
                                * camelot.Tones.DivaMF.tone3
                                * camelot.Tones.DivaMF.tone4
                                * camelot.Tones.DivaMF.tone5
                                * camelot.Tones.DivaMF.tone6
                                * camelot.Tones.DivaMF.tone7
                                * camelot.Tones.DivaMF.tone8
                                * camelot.Tones.DivaMF.tone9
                                * 1camelot.Tones.DivaMF.tone0
                                * camelot.Tones.DivaMF.toneStart
                                * camelot.Tones.DivaMF.toneStop
        :parameter continous_tone: This parameter is applicable only for
                                   continous tone type. Valid value are
                                   '0x80' to '0xCB'. Default is -1.
                                   Refer the Diva SDK document for tone name.
        :parameter tone_duration: This parameter is applicable for continuous,
                                      single and dual tone type.
                                      duration in seconds
        :parameter frequencyA: This parameter is applicable only for single or
                                dual tone type. Value between 0 to 4000 (in Hz)
                                default is -1.
        :parameter amplituteA: This parameter is applicable only for single or
                                dual tone type.  Value between -32767 to 32767.
                                default is 65535
        :parameter frequencyB: This parameter is applicable only for dual tone
                                type. Value between 0 to 4000 (in Hz)
                                default is -1.
        :parameter amplituteB: This parameter is applicable only for dual tone
                                type.  Value between -32767 to 32767.
                                default is 65535
        :returns: True or Camelot Exception\n
                  possible Exceptions are:\n
                  * Invalid stream Reference\n
                  * endpoint does not support this feature\n
                  * Continuous tone type requires continuous_tone id given \
                    valid values 0x80 to OxCB.\n
                  * Multifrequcenty tone requires valid frequency list\n
                  * maximum count of frequencies list should be 12\n
                  * single tone requires frequencyA (0 to 4000)
                  * single tone rquires amplituteA (-32767 to 32767)\n
                  * dual tone requires frequencies in (0 to 4000)\n
                  * dual tone rquires amplitutes in (-32767 to 32767

        >>> ep1.send_tones('0x7843e12a', tone_type=0, continuous_tone='0x82',
            tone_duration=5)
        >>> True

        >>> ep1.send_tones('0x763211f2',tone_type=1, freuqencies=[1,2,3,4])
        >>> True

        >>> ep1.send_tones('0x8732fa21', 2, frequencyA=2000, amplituteA=300,
                tone_duration=4)
        >>> True

        >>> ep1.send_tones('0x8732fa21', 3, frequencyA=2000, amplituteA=300,
                frequencyB=2500, amplitureB=400, tone_duration=4)
        >>> True
        '''
        log.debug('Entering method send_tones().')

        if stream_ref != 'null' and not self._is_valid_call_ref(stream_ref):
            raise camelot.CamelotError("Invalid stream Reference")
        tone_value = tone_type.value
        if tone_value == 0:
            if continuous_tone == '-1':
                raise camelot.CamelotError
                ("Continuous tone type requires continuous_tone id given \
                valid values 0x80 to OxCB")
            if not tone_duration:
                raise camelot.CamelotError
                ("Continuous tone duration should be non zero")
        elif tone_value == 1:
            if not len(frequencies):
                raise camelot.CamelotError
                ("Multifrequcenty tone requires valid frequency list")
            elif len(frequencies) > 12:
                raise camelot.CamelotError
                ("maximum count of frequencies list should be 12")
        elif tone_value == 2:
            if frequencyA == -1:
                raise camelot.CamelotError
                ("single tone requires frequencyA (0 to 4000)")
            if amplituteA == 65536:
                raise camelot.CamelotError
                ("single tone rquires amplituteA (-32767 to 32767)")
        elif tone_value == 3:
            if frequencyA == -1 or frequencyB == -1:
                raise camelot.CamelotError
                ("dual tone requires frequencies in (0 to 4000)")
            if amplituteA == 65536 or amplituteB == 65536:
                raise camelot.CamelotError
                ("dual tone rquires amplitutes in (-32767 to 32767)")
        else:
            raise camelot.CamelotError("Invalid tone type")

        kwargs = {'tone_type': tone_value,
                  'mf_frequencies': frequencies,
                  'continuous_tone': continuous_tone,
                  'tone_duration': tone_duration,
                  'frequencyA': frequencyA,
                  'amplituteA': amplituteA,
                  'frequencyB': frequencyB,
                  'amplituteB': amplituteB}

        return self._binary_to_boolean(self._query_camelot
                                       (camelot.SEND_TONES, stream_ref,
                                        **kwargs))

    def detect_tones(self,
                     stream_ref,
                     tone_type=camelot.Tones.ToneType.all,
                     continuous_tone=[],
                     report_flag=-1,
                     frequencies=[],
                     min_duration=-1,
                     min_snr=65536,
                     min_level=65536,
                     max_highlow_am=65536,
                     max_lowhigh_fm=65536):
        '''
        This API is used for CAS endpoints to enable diferent tone detections.

        :parameter stream_ref: Valid stream_ref.  The stream_ref should be of
                               receiving inbound stream
        :parameter tone_type: Type of tone to be detected. Valid values are:\n
                                * camelot.Tones.ToneType.continuousTone
                                * camelot.Tones.ToneType.multiFrequencyTone
                                * camelot.Tones.ToneType.singleTone
                                * camelot.Tones.ToneType.dualTone
                                * camelot.Tones.ToneType.all (Default)
                                * camelot.Tones.ToneType.none
                            Note: camelot.Tones.ToneType.none will disable
                                  tone detection.
        :parameter frequencies: This parameter is valid only for multifreuqncy.
                                The given frequencies are only reported through
                                event call backs.
                                Valid Values are:\n
                                * camelot.Tones.DivaMF.tone1
                                * camelot.Tones.DivaMF.tone2
                                * camelot.Tones.DivaMF.tone3
                                * camelot.Tones.DivaMF.tone4
                                * camelot.Tones.DivaMF.tone5
                                * camelot.Tones.DivaMF.tone6
                                * camelot.Tones.DivaMF.tone7
                                * camelot.Tones.DivaMF.tone8
                                * camelot.Tones.DivaMF.tone9
                                * 1camelot.Tones.DivaMF.tone0
                                * camelot.Tones.DivaMF.toneStart
                                * camelot.Tones.DivaMF.toneStop
        :parameter continous_tone: This parameter is applicable only for
                                   continous tone type. The given frequency
                                   only is reported through event call back.
                                   Valid value are
                                   '0x80' to '0xCB'.
                                   Refer the Diva SDK document for tone name.
        :parameter report_flag: Applicable only for single or dual tone.\n
                               possible values are:\n
                               For single tone:\n
                               * 2 - Signal Noise Ratio\n
                               * 4 - Energy\n
                               * 8 - Frequency\n
                               * 16 - Energy variation\n
                               * 32 - Frequency variation\n
                               For dual tone:\n
                               * 2 - signal noise reation \n
                               * 4 - energy low tone \n
                               * 8 - energy high tone \n
                               * 16 - frequency low tone \n
                               * 32 - frequency hight tone \n
        :parameter min_duration: Applicable only for single or dual tone.\n
                                the minimum duration of a tone before the
                                detection is reported (in milli seconds)
        :parameter min_snr: Applicable only for single or dual tone.\n
                            minimum signal noise ratio (-32768 to 32767)
        :parameter min_level: Applicable only for single or dual tone.\n
                            minimum level of detected signal\n
                             * -1 - any level
                             * -32767 to 32767
        :parameter max_highlow_am: Applicable only for single or dual tone.\n
                                    * if single tone this parameter means,
                                    maximum allowed variation of signal
                                    frequency. value in between 0 to 65535
                                    * if dual tone this parameter means,
                                    maximum allowed difference in levels
                                    between the higher and the lower frequency
                                    tone. The value -32767 corresponds to
                                    -127.996 dB and the value 32767 corresponds
                                    to +127.996 dB. The value -32768 is invalid
        :parameter max_lowhigh_fm: Applicable only for single or dual tone.\n
                                    * if single tone this paramter means,
                                    maximum allowed variation of the signal
                                    frequency. value between 0 - 4000 (Hz)
                                    * if dual tone this paramter means,
                                    maximum allowed difference in level between
                                    the lower and higher frequency tone. The
                                    value -32767 corresponds to -127.996 dB and
                                    the value 32767 corresponds to +127.996 dB.
                                    The value -32768 is invalid

        :returns: True or Camelot Exception\n
                  possible exceptions are:\n
                  * invalid stream reference\n
                  * endpoint does not support this feature\n
                  * Continuous tone type requires continuous_tone id given \
                    valid values 0x80 to OxCB\n
                  * Multifrequcenty tone requires valid frequency list\n
                  * Invalid report flag\n
                  * Invalid min_duration\n
                  * Invalid min_snr; valid:-32768 to 32767\n
                  * Invalid min_level;valid:-1, -32767 to 32767\n
                  * Invalid max_highlow_am;SingleTone: 0 to 65535\n
                    DualTone: -32768 to 32767\n
                  * Invalid max_lowhigh_fm;SingleTone: valid 0 to 4000\n
                    DualTone: -32768 to 32767\n
                  * Invalid tone_type; valid 0 to 3\n

        >>> enable continuous and multi frequency tone
        >>> ep2.detect_tones('0x792af221', camelot.Tones.ToneType.all)
        >>> True
        >>> ep2.detect_tones('0x792af221')
        >>> True

        >>> disable continuous and multi frequency tone
        >>> ep2.detect_tones('0x792af221', camelot.Tones.ToneType.none)
        >>> True

        >>> continuous tone
        >>> ep2.detect_tones('0x792af221',
            camelot.Tones.ToneType.continuousTone,
            continuous_tone=[0x80,0x81])
        >>> True

        >>> multi frequency tone
        >>> ep2.detect_tones('0x792af221',
             camelot.Tones.ToneType.multiFrequencyTone,
             frequencies=[camelot.Tones.DivaMF.tone1,
                          camelot.Tones.DivaMF.tone2,
                          camelot.Tones.DivaMF.tone3])
        >>> True

        >>> single tone
        >>> ep2.detect_tones('0x792af221',
                             camelot.Tones.ToneType.singleTone,
                             8, 2000, 200, 200, 3000)
        >>> True

        >>> dual tone
        >>> ep2.detect_tones('0x792af221',
                             camelot.Tones.ToneType.dualTone,
                             8, 2000, 200, 200, 3000)
        >>> True
        '''
        log.debug('Entering method detect_tones')
        if stream_ref != 'null' and not self._is_valid_call_ref(stream_ref):
            raise Exception("Invalid stream Reference")
        tone_value = tone_type.value
        if tone_value in [4, 5]:
            tone_value = tone_type.value
        else:
            if tone_value == 0:
                if not len(continuous_tone):
                    raise camelot.CamelotError
                    ("Continuous tone type requires continuous_tone id given \
                    valid values 0x80 to OxCB")
            elif tone_value == 1:
                if not len(frequencies):
                    raise camelot.CamelotError
                    ("Multifrequcenty tone requires valid frequency list")
            elif tone_value in [2, 3]:
                if report_flag not in [2, 4, 8, 16, 32]:
                    raise camelot.CamelotError('Invalid report flag')
                if min_duration == -1:
                    raise camelot.CamelotError('Invalid min_duration')
                if min_snr == 65536:
                    raise Exception('Invalid min_snr; valid:-32768 to 32767')
                if min_level == 65536:
                    raise camelot.CamelotError('Invalid min_level;\
                        valid:-1, -32767 to 32767')
                if max_highlow_am == 65536:
                    raise camelot.CamelotError('Invalid max_highlow_am;\
                        SingleTone: 0 to 65535\nDualTone: -32768 to 32767')
                if max_lowhigh_fm == 65536:
                    raise camelot.CamelotError('Invalid max_lowhigh_fm;\
                    SingleTone: valid 0 to 4000\nDualTone: -32768 to 32767')
            else:
                raise camelot.CamelotError('Invalid tone_type; valid 0 to 3')
        kwargs = {'tone_type': tone_value,
                  'continuous_tone': list(sorted
                                          (set(continuous_tone),
                                           key=continuous_tone.index)),
                  'mf_frequencies': list(sorted
                                         (set(frequencies),
                                          key=frequencies.index)),
                  'report_flag': report_flag,
                  'min_duration': min_duration,
                  'min_snr': min_snr,
                  'min_level': min_level,
                  'max_highlow_am': max_highlow_am,
                  'max_lowhigh_fm': max_lowhigh_fm}
        return self._binary_to_boolean(self._query_camelot(
            camelot.DETECT_TONES, stream_ref, **kwargs))
