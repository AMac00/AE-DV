'''
Use of below variable in json.
"camelot_ep_template_file":"template/camelot_parm_template.py",
"add_feature": ["bfcp"],
"phone_model": "DX70"

"services": {
    "camelot": {
        "camelot_ip": "10.8.124.99",
        "camelot_port": 5011,
        "camelot_version": "12.5.8.0.0.0",
        "config_params": {
            "camelot_ep_template_file":"camelot_parm_template.py",
            "add_feature": ["bfcp"],
            "phone_model": "DX70",
            "sip.phone.ip": "10.8.124.99",
            "sip.phone.tftpip": "10.8.4.19"
        }
    }

'''
phones_camelot_params = {
    "DX70": {
        "sip.phone.modelnumber": "36241",
        "sip.phone.payloadtype.1": "107",
        "sip.phone.payloadtype.2": "108",
        "sip.phone.payloadtype.3": "114",
        "sip.phone.payloadtype.4": "104",
        "sip.phone.payloadtype.5": "105",
        "sip.phone.payloadtype.6": "105",
        "sip.phone.payloadtype.7": "9",
        "sip.phone.payloadtype.8": "18",
        "sip.phone.payloadtype.9": "0",
        "sip.phone.tls1dot2": "2",
        "sip.phone.transport": "1",
        "sip.phone.vidcodectype.1": "H264",
        "sip.phone.vidcodectype.2": "H264",
        "sip.phone.vidcodectype.3": "H263-1998",
        "sip.phone.vidcodectype.4": "H263",
        "sip.phone.videotias": "3072000",
        "sip.phone.vidpayloadtype.1": "97",
        "sip.phone.vidpayloadtype.1.h264maxbr": "2500",
        "sip.phone.vidpayloadtype.1.h264maxfps": "3000",
        "sip.phone.vidpayloadtype.1.h264packetizationmode": "0",
        "sip.phone.vidpayloadtype.1.h264profilelevelid": "0x428014",
        "sip.phone.vidpayloadtype.1.maxbr": "2500",
        "sip.phone.vidpayloadtype.2": "126",
        "sip.phone.vidpayloadtype.2.h264maxfps": "3000",
        "sip.phone.vidpayloadtype.2.h264packetizationmode": "1",
        "sip.phone.vidpayloadtype.2.h264profilelevelid": "0x428014",
        "sip.phone.vidpayloadtype.2.maxbr": "2500",
        "sip.phone.vidpayloadtype.3": "96",
        "sip.phone.vidpayloadtype.3.maxbr": "30000",
        "sip.phone.vidpayloadtype.4": "34",
        "sip.phone.vidpayloadtype.4.maxbr": "10000",
        "sip.protocol.regsupportedhdr": "replaces,100rel,timer,"
                                        "gruu,path,outbound,"
                                        "X-cisco-serviceuri,"
                                        "X-cisco-callinfo,"
                                        "X-cisco-service-control,"
                                        "X-cisco-srtp-fallback,"
                                        "X-cisco-sis-7.1.1,"
                                        "norefersub,extended-refer,sdp-anat",
        "sip.protocol.reguseragenthdr": "TANDBERG/529 (ce8.3.0.c1a7707) "
                                        "Cisco-DX70"
    },
    "8865": {
        "sip.phone.codectype.3": "iSAC_30",
        "sip.phone.payloadtype.7": "18",
        "sip.phone.payloadtype.2": "9",
        "sip.protocol.regsupportedhdr": "replaces,join,sdp-anat,"
                                        "norefersub,resource-priority,"
                                        "extended-refer,X-cisco-callinfo,"
                                        "X-cisco-serviceuri,"
                                        "X-cisco-escapecodes,"
                                        "X-cisco-service-control,"
                                        "X-cisco-srtp-fallback,"
                                        "X-cisco-monrec,X-cisco-config,"
                                        "X-cisco-sis-7.0.0,X-cisco-xsi-8.5.1",
        "sip.phone.vidpayloadtype.2": "126",
        "sip.phone.vidpayloadtype.2.h264profilelevelid": "0x428016",
        "sip.phone.vidpayloadtype.2.h264packetizationmode": "1",
        "sip.phone.payloadtype.4": "0",
        "sip.phone.vidpayloadtype.3": "97",
        "sip.phone.videoTIAS": "4000000",
        "sip.phone.codectype.1": "opus",
        "sip.phone.payloadtype.6": "116",
        "sip.phone.vidpayloadtype.3.h264packetizationmode": "0",
        "sip.phone.vidpayloadtype.1": "100",
        "sip.phone.vidcodectype.1": "H264",
        "sip.phone.payloadtype.5": "8",
        "sip.phone.payloadtype.1": "114",
        "sip.phone.vidpayloadtype.1.h264packetizationmode": "1",
        "sip.phone.codectype.6": "iLBC_20",
        "sip.phone.vidpayloadtype.1.h264profilelevelid": "0x640C16",
        "sip.phone.codectype.2": "g7221_32k",
        "sip.phone.vidcodectype.3": "H264",
        "sip.phone.vidpayloadtype.3.h264profilelevelid": "0x428016",
        "sip.phone.vidcodectype.2": "H264",
        "sip.protocol.reguseragenthdr": "Cisco-CP8865/11.5.1",
        "sip.phone.modelnumber": "36225",
        "sip.phone.audioTIAS": "64000",
        "sip.phone.payloadtype.3": "124"
    }
}

features_camelot_params = {
    "bfcp": {
        "sip.phone.bfcp.enabled": "2",
        "sip.phone.bfcp.floorctrl": "3",
        "sip.phone.bfcp.setup": "3",
        "sip.phone.bfcp.secondvideo.1.label ": "3",
        "sip.phone.bfcp.transport": "1",
        "sip.phone.bfcp.secondvideo.1.contenttype": "1",
        "sip.phone.bfcp.secondvideo.count": "1"
    }
}
