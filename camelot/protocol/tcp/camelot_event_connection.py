'''
Created on 11-Sep-2013

@author: smaturi
'''
from threading import Thread
import socket
from camelot.events import Event, InfoEventType, EventType
import camelot
from camelot import camlogger


log = camlogger.getLogger(__name__)


class ConnectionError(Exception):
    pass


class EventConnection(object):
    EVENT_MESSAGE_HEADER_TO_READ = 16
    HEX_TO_DIGIT_RADIX = 16

    def __init__(self, event_sock, server_ip, server_port, conn):
        self.event_socket = event_sock
        self.camelot_server_ip = server_ip
        self.camelot_server_port = server_port
        self.connection = conn
        self.event_thread = Thread(target=self.run)

    def start(self):
        self.stopped = False
        self.event_thread.daemon = True
        self.event_thread.start()

    def run(self):
        while not self.stopped:
            try:

                event = self.event_socket.recv(
                    EventConnection.EVENT_MESSAGE_HEADER_TO_READ)
                if self.stopped:
                    break
                if not event:
                    log.error("End of stream reached for the socket, Event "
                              "channel is closed")
                    self.connection.close_event_channel()
                    self.stopped = True
                else:

                    event_header_msg = event.strip()

                    if event_header_msg:

                        tokens = event_header_msg.split(":")

                        event_msg_len = int(
                            tokens[2], EventConnection.HEX_TO_DIGIT_RADIX)

                        event_msg = self.event_socket.recv(event_msg_len)

                        log.debug(
                            "A Event message of %s is read from the event "
                            "port actual length is %s" % (
                                event_msg, event_msg_len))

                        self.process_event(tokens[1], event_msg)
            except socket.timeout as e:
                # log.debug("Read timed out: %s" % e)
                pass
            except socket.error as e:
                log.exception("Unexpected Error stopping the Connection")
                self.connection.close_event_channel()
                self.stopped = True
            except Exception as e:
                log.error("Unexpected exception %s" % e)

            if self.stopped:
                break

        if self.event_socket:
            try:
                self.event_socket.close()
            except Exception as e:
                log.warning("Could not stop the event thread")

    def stop_events(self):
        self.stopped = True
        self.event_socket.close()

    def process_event(self, ep_address, message):

        log.debug("An Event message is received for EP %s and message :%s" % (
            ep_address, message))
        msg_tokens = message.split(" ")
        event_type = msg_tokens.pop(0)

        event_dict = {'camelot_ip': self.camelot_server_ip,
                      'camelot_port': self.camelot_server_port,
                      'endpoint_id': ep_address,
                      'event_type': event_type,
                      'event_sub_type': None,
                      'message': ' '.join(msg_tokens)}
        event = Event()
        event._copy_from_dict(event_dict)
        if event_type in [InfoEventType.STATE,
                          InfoEventType.CALLS,
                          InfoEventType.BACKUPCM,
                          InfoEventType.BCGREADY,
                          InfoEventType.LOSTCONN,
                          InfoEventType.PRIMARYCM]:
            event.event_sub_type = event_type
            event.event_type = EventType.INFO_EVENT
        elif event_type in [EventType.STATION_EVENT,
                            EventType.CALL_EVENT]:
            event.event_sub_type = msg_tokens[1]

        serv = camelot.get_camelot_server(self.camelot_server_ip,
                                          self.camelot_server_port)

        log.debug("calling default event callback on server")
        serv._default_event_callback(event)
