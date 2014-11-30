# -*- coding: utf-8 -*-
import socks
import socket
import mechanize


# --------------------------------------------------------------------------
def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock


# --------------------------------------------------------------------------
def connect_tor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
    # patch the socket module
    socket.socket = socks.socksocket
    socket.create_connection = create_connection


# --------------------------------------------------------------------------
def testip(params):
    print dorequest('http://echoip.com', params)


# --------------------------------------------------------------------------
def dorequest(url, params):
    req = mechanize.Request(url)
    if params.agent is not None:
        req.add_header("User-agent", params.agent)
    else:
        req.add_header("User-agent", "Soy el lefito.")
    result={}
    try:
        respuesta = mechanize.urlopen(req)
        result['body'] = respuesta.read()
        result['head'] = respuesta.info()
    except:
        result={
            'body': 'error',
            'head': 'error',
            }
    return result


# --------------------------------------------------------------------------
def menuppal(intell, params):
    choice = showmenuppal()
    while choice != "q":
        if choice == "0":
          initintell(intell,params)
        elif choice == "1":
          startrecogn(intell,params)
        choice = showmenuppal()
    return True


# --------------------------------------------------------------------------
class Parameters:
    """Program parameters"""
    # ----------------------------------------------------------------------
    def __init__(self, **kwargs):
        self.param1 = kwargs.get("param1")
        self.param2 = kwargs.get("param2")
        self.verbosity = kwargs.get("verbosity")
