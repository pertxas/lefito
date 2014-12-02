# -*- coding: utf-8 -*-
import socks
import socket
import re
import urllib.request
import urlparse3
import difflib
import os


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
    req = dorequest('http://echoip.com', params)
    out = Displayer()
    out.display(str(req['body']))


# --------------------------------------------------------------------------
def dorequest(url, params):
    req = urllib.request.Request(url)
    if params.agent is not None:
        req.add_header("User-agent", params.agent)
    else:
        req.add_header("User-agent", "Soy el lefito.")
    result = {}
    try:
        respuesta = urllib.request.urlopen(req)
        result['body'] = respuesta.read()
        result['head'] = respuesta.info()
    except:
        result = {
            'body': 'error',
            'head': 'error',
        }
    return result


# --------------------------------------------------------------------------
def menuppal(intell, params):
    choice = showmenuppal()
    while choice != "q":
        if choice == "0":
            initintell(intell, params)
        elif choice == "1":
            startrecogn(intell, params)
        choice = showmenuppal()
    return True


# --------------------------------------------------------------------------
def showmenuppal():
    print("[0] Init Intelligence")
    print("[1] Start Recogn")
    print("[q] Quit")
    choice = str(input("Select:"))
    return choice


# --------------------------------------------------------------------------
def initintell(intell, params):
    out = Displayer()
    if params.url is not None:
        intell['target'] = params.url
    else:
        intell['target'] = str(input("url: "))
    originalreq = dorequest(intell['target'], params)
    intell['originalreq_lines'] = originalreq['body'].splitlines()
    intell['originalhead'] = originalreq['head']
    out.display(originalreq['head'])
    intell['originalsess'] = getsess(originalreq['head'])
    intell['parsedurl'] = urlparse3.parse_url(intell['target'])
    intell['parametros'] = intell['parsedurl'].query.split('&')


# --------------------------------------------------------------------------
def startrecogn(intell, params):
    if params.payloads is not None:
        pause = input("Pause? [y/n]")
        payloadslist = readpayloads(params.payloads)
        attack(intell, payloadslist, pause, params)
    else:
        selectedpayloadlist = menupayloads('./payloads')
        while selectedpayloadlist != 'q':
            pause = input("Pause? [y/n]")
            payloadslist = readpayloads(selectedpayloadlist)
            attack(intell, payloadslist, pause, params)
            selectedpayloadlist = menupayloads('./payloads')
    return True


# --------------------------------------------------------------------------
def getsess(info):
    out = Displayer()
    if 'set-cookie' in info:
        out.display(info['set-cookie'])
        m = re.search("(PHPSESSID=(?P<value>.*);)", info['set-cookie'])
        if m:
            out.display(m.group('value'))
            return m.group('value')
        else:
            return ''
    else:
        return ''


# --------------------------------------------------------------------------
def readpayloads(fname):
    with open(fname) as f:
        content = f.readlines()
        content = [x.strip('\n') for x in content]
    return content


# --------------------------------------------------------------------------
def attack(intell, payloadslist, pause, params):
    out = Displayer()
    for parametro in intell['parametros']:
        urls = genurls(payloadslist, parametro, intell)
        for url in urls:
            out.display('-' * len(url))
            out.display(url)
            out.display('-' * len(url))
            req = "%s://%s%s?%s" % (intell['parsedurl'].scheme,
                                    intell['parsedurl'].netloc,
                                    intell['parsedurl'].path,
                                    url)
            result = dorequest(req, params)
            result_lines = result['body'].splitlines()
            difflib.Differ()
            diff = difflib.unified_diff(intell['originalreq_lines'], result_lines)
            for line in diff:
                if line.startswith('+'):
                    line = line.strip("+ ")
                    line = cleanhtml(line)
                    if len(line) > 1:
                        out.display(line)
            if pause == 'y':
                cont = input('press enter to continue (q+enter to quit)')
                if cont == 'q':
                    return True


# --------------------------------------------------------------------------
def genurls(payloadslist, parametro, intell):
    valores = parametro.split('=')
    resultado = []
    for payload in payloadslist:
        cadena = payload.replace("[FOO]", valores[0])
        cadena = cadena.replace("[BAR]", valores[1])
        cadena = cadena.replace("[SESS]", intell['originalsess'])
        cadena = cadena.replace("[HOST]", intell['parsedurl'].netloc)
        cadena = cadena.replace("[STHOST]", intell['parsedurl'].netloc.replace("www.", ""))
        resultado.append(cadena)
    return resultado


# --------------------------------------------------------------------------
def menupayloads(dirname):
    listapayloads = os.listdir(dirname)
    n = 0
    listapayloads.sort()
    for payload in listapayloads:
        print("[%i] %s" % (n, payload))
        n += 1
    print("[q] Salir")
    try:
        select = int(input("elige: "))
        payloadseleccionado = listapayloads[select]
        return dirname + '/' + payloadseleccionado
    except:
        return 'q'


# --------------------------------------------------------------------------
def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


# --------------------------------------------------------------------------
class Parameters:
    """Program parameters"""
    # ----------------------------------------------------------------------
    def __init__(self, **kwargs):
        self.url = kwargs.get("url")
        self.payloads = kwargs.get("payloads")
        self.tor = kwargs.get("tor")
        self.checkip = kwargs.get("checkip")
        self.agent = kwargs.get("agent")


# -------------------------------------------------------------------------
class Displayer:
    """Output system"""
    instance = None

    # ---------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, *args, **kwargs)
            cls.__initialized = False
        return cls.instance

    # ---------------------------------------------------------------------
    def config(self, **kwargs):
        self.out_file = kwargs.get("out_file", None)
        self.out_screen = kwargs.get("out_screen", True)
        self.verbosity = kwargs.get("verbosity", 0)
        if self.out_file:
            self.out_file_handler = open(self.out_file, "w")

    # ---------------------------------------------------------------------
    def display(self, message):
        if self.verbosity > 0:
            self.__display(message)

    # ---------------------------------------------------------------------
    def display_verbosity(self, message):
        if self.verbosity > 1:
            self.__display(message)

    # ---------------------------------------------------------------------
    def display_more_verbosity(self, message):
        if self.verbosity > 2:
            self.__display(message)

    # ---------------------------------------------------------------------
    def __display(self, message):
        if self.out_screen:
            print(message)
        if self.out_file_handler:
            self.out_file_handler.write(message)

    # ---------------------------------------------------------------------
    def __init__(self):
        if not self.__initialized:
            self.__initialized = True
            self.out_file = None
            self.out_file_handler = None
            self.out_screen = True
            self.verbosity = 0
