import camelot
import time


''' Used for parsing Streams'''
def get_stream_ref(ep, direction, type, callref):
	ep.release_streams()
	streams = ep.get_streams()
	for stream in streams:
		if ( stream['CallId'] == callref and stream['Direction'] == direction and stream['Type'] == type ):
			return stream['StrmID']

''' Used for Event Callback'''
def event_callbacks(event):
    print("Received Event : %s" % event)
    print("Received Event Type : %s" % event.event_type)
    print("Received Event Sub_type: %s" % event.event_sub_type)
    print("Received Event Message: %s" % event.message)
    return()



''' Sever Information'''
CamelotServerIp = "10.38.243.32"
CamelotServerPort = 5001
CcmIp = "10.38.243.17"
ep1line = 1005550070
ep2line = 1005550071
ep1Mac = "SEP001005550070"
ep2Mac = "SEP001005550071"
# Place holder for Phones
epphone = ep1Mac
# Server Connections information
serv = camelot.create_camelot_server(CamelotServerIp, CamelotServerPort)
serv.log_mask(moduleid="*",level="debug_5",device="file")
serv.log_mask(moduleid="*",level="debug_5",device="console")
# Set Call Back for Events at Server
#serv.register_event_callback(event_callback)
# Create Endpoint ( needed for all actions)
ep = serv.create_new_endpoint('sipx',epphone)

# Start call back for events at device level
ep.register_event_callback(event_callbacks)
__return__ = ep.start_info_events()
print("Start info events = {0}".format(__return__))
__return__ = ep.start_station_events()
print("Start Station events = {0}".format(__return__))


''' Actions for Phone Calls'''
action = "inservice"

if "inservice" in action:
    ep.config('sip.phone.ip', CamelotServerIp)
    ep.config('sip.phone.httpip', CcmIp)
    ep.config('sip.phone.modelnumber', '684')
    ep.config('sip.protocol.reguseragenthdr', 'Cisco-CP8851/11.5.1')
    ep.set_client_data(epphone)
    ep.init()
    ep.inservice()
    time.sleep(3)
    print("ep1 state -> {0}".format(ep.get_info()['state']))
    # Test the return pull
    time.sleep(4)
    ret = serv.get_endpoint(epphone)
    print("Return from Ret = {0}".format(ret))

if "stat" in action:
    try:
        ep = serv.get_endpoint(epphone,get_from_server=True)
        print("Return from Ret = {0}".format(ep.get_info()))
    except:
        print("Error pulling Endpoint Information for {0}".format(epphone))
    #ret = serv.get_end_point('phone1')

if "outservice" in action:
    ret = serv.get_endpoint(epphone,get_from_server=True)
    #ret = serv.get_end_point('phone1')
    __return__ = ret.outofservice()
    print("Return from Ret = {0}".format(__return__))

if "get_call_info" in action:
    ep1 = serv.get_endpoint(epphone,get_from_server=True)
    __return__ = ep1.get_calls()
    print("Return from Ret = {0}".format(__return__))
    ep1callref = ep1.get_calls()[0]['Id']
    print("Call Ref = {0}".format(ep1callref))
    ep1txstreamref = get_stream_ref(ep1, direction='Tx', type='audio', callref=ep1callref)
    print("ep1 get_stream_info_ext for Tx -> {0}".format(ep1.get_stream_info_ext(stream_ref=ep1txstreamref)))

if "place_call_1_to_2_handup" in action:
    ep1 = serv.get_endpoint(ep1Mac,get_from_server=True)
    ep2 = serv.get_endpoint(ep2Mac, get_from_server=True)
    ep2.enable_auto_answer()
    ep1.onhook()
    ep2.onhook()
    print("ep1 state -> {0}".format(ep1.get_info()['state']))
    print("ep2 state -> {0}".format(ep2.get_info()['state']))
    print("Placing call from ep1 to ep2")
    ep1callref = ep1.place_call(ep2.get_dn())
    time.sleep(2)
    ep2callref = ep2.get_calls()[0]['Id']
    print("ep1 getstreams -> {0}".format(ep1.get_streams()))
    print("ep2 getstreams -> {0}".format(ep2.get_streams()))
    ep1txstreamref = get_stream_ref(ep1, direction='Tx', type='audio', callref=ep1callref)
    ep1rxstreamref = get_stream_ref(ep1, direction='Rx', type='audio', callref=ep1callref)
    ep2txstreamref = get_stream_ref(ep2, direction='Tx', type='audio', callref=ep2callref)
    ep2rxstreamref = get_stream_ref(ep2, direction='Rx', type='audio', callref=ep2callref)
    ep1.start_media_player(stream_ref=ep1txstreamref, encoding='wav',
                           url='file://usr/local/camelot/lib/media/Record.wav')
    i = 0
    while i <= 5:
        # Print Stream information
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print("ep1 get_stream_info_ext for Tx -> {0}".format(ep1.get_stream_info_ext(stream_ref=ep1txstreamref)))
        print("ep2 get_stream_info_ext for Rx -> {0}".format(ep2.get_stream_info_ext(stream_ref=ep2rxstreamref)))
        # Print call information
        print("----------------")
        print("ep1 get_stream_info_ext for Tx -> {0}".format(ep1.get_stream_info(stream_ref=ep1txstreamref)))
        print("ep2 get_stream_info_ext for Rx -> {0}".format(ep2.get_stream_info(stream_ref=ep2rxstreamref)))
        print("----------------")
        time.sleep(2)
        i = i + 1
    # Hang up the Call
    ep1.onhook(callref=ep1callref)
    time.sleep(2)
    print("Call status = {0}".format(ep1.get_calls()))

if "place_call_1_to_2_callup" in action:
    ep1 = serv.get_endpoint(ep1Mac,get_from_server=True)
    ep2 = serv.get_endpoint(ep2Mac, get_from_server=True)
    ep2.enable_auto_answer()
    ep1.onhook()
    ep2.onhook()
    print("ep1 state -> {0}".format(ep1.get_info()['state']))
    print("ep2 state -> {0}".format(ep2.get_info()['state']))
    print("Placing call from ep1 to ep2")
    ep1callref = ep1.place_call(ep2.get_dn())
    time.sleep(2)
    print(ep1.get_calls())
    print(ep2.get_calls())
    ep2callref = ep2.get_calls()[0]['Id']
    print("ep1 getstreams -> {0}".format(ep1.get_streams()))
    print("ep2 getstreams -> {0}".format(ep2.get_streams()))
    ep1streamref = get_stream_ref(ep1, direction='Tx', type='audio', callref=ep1callref)
    ep2streamref = get_stream_ref(ep2, direction='Rx', type='audio', callref=ep2callref)
    ep1.start_media_player(stream_ref=ep1streamref, encoding='wav',
                           url='file://usr/local/camelot/lib/media/Record.wav')
    print("ep1 get_stream_info for Tx -> {0}".format(ep1.get_stream_info(stream_ref=ep1streamref)))
    print("ep2 get_stream_info for Rx -> {0}".format(ep2.get_stream_info(stream_ref=ep2streamref)))
    time.sleep(2)
    # Hang up the Call
    time.sleep(2)
    print("Call status = {0}".format(ep1.get_calls()))

if "disconnect_call" in action:
    ep = serv.get_endpoint(epphone,get_from_server=True)
    __return__ = ep.get_calls()
    print("Call state = {0}".format(__return__[0]['CallState']))
    if "disconnected" in __return__[0]['CallState']:
        print("Call Already Disconnected = {0}".format(__return__))
    elif __return__[0] and "connected" in __return__[0]['CallState']:
        __return_2__ = ep.onhook(callref=__return__[0]['call_ref'])
        __return__ = ep.get_calls()
        i = 0
        while i <= 5 and "disconnected" not in __return__[0]['CallState']:
            __return__ = ep.get_calls()
            print("Call state = {0}".format(__return__[0]['CallState']))
            time.sleep(2)
            i = i + 1

if "find_error" in action:
    try:
        endpoint = serv.get_endpoint("SEP000000581401", get_from_server=True)
        print("return = {0}".format(endpoint))
    except camelot.CamelotError as err:
        print("Error = {0}".format(err))
        endpoint = serv.create_new_endpoint('sipx',"SEP000000581401")
        endpoint.set_client_data("SEP000000581401")
        print("Error return = {0}".format(endpoint))