# -*- coding: utf-8 -*-
import socks
import socket
import re
import urllib.request
from urllib.parse import urlparse
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
    url = 'http://www.leaky.org/ip_tester.pl'
    #url = 'http://echoip.com'
    req = dorequest(url, params)
    out = Displayer()
    for line in req['body'].splitlines():
        line = line.decode('utf-8')
        out.display_verbosity(line)
        if line.startswith('<p>Your') or line.startswith('The conn'):
            out.display(cleanhtml(line))


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
def menuppal(params):
    intell = IntellCollector()
    choice = showmenuppal()
    while choice != "q":
        if choice == "0":
            intell.gather(params)
        elif choice == "1":
            intell.show()
        elif choice == "2":
            startrecogn(params)
        choice = showmenuppal()
    return True


# --------------------------------------------------------------------------
def showmenuppal():
    print("[0] Init Intelligence")
    print("[1] Show Intelligence")
    print("[2] Start Recogn")
    print("[q] Quit")
    choice = str(input("Select:"))
    return choice

# --------------------------------------------------------------------------
def startrecogn(params):
    if params.payloads is not None:
        pause = input("Pause? [y/n]")
        payloadslist = readpayloads(params.payloads)
        attack(payloadslist, pause, params)
    else:
        selectedpayloadlist = menupayloads('./payloads')
        while selectedpayloadlist != 'q':
            pause = input("Pause? [y/n]")
            payloadslist = readpayloads(selectedpayloadlist)
            attack(payloadslist, pause, params)
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
def attack(payloadslist, pause, params):
    intell = IntellCollector()
    out = Displayer()
    for parametro in intell.parametros:
        urls = genurls(payloadslist, parametro)
        for url in urls:
            out.display('-' * len(url))
            out.display(url)
            out.display('-' * len(url))
            req = "%s://%s%s?%s" % (intell.parsedurl.scheme,
                                    intell.parsedurl.netloc,
                                    intell.parsedurl.path,
                                    url)
            result = dorequest(req, params)
            result_lines = [x.decode(intell.charset) for x in result['body'].splitlines()]
            difflib.Differ()
            diff = difflib.unified_diff(intell.originalreq_lines, result_lines)
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
def genurls(payloadslist, parametro):
    intell = IntellCollector()
    valores = parametro.split('=')
    resultado = []
    for payload in payloadslist:
        cadena = payload.replace("[FOO]", valores[0])
        cadena = cadena.replace("[BAR]", valores[1])
        cadena = cadena.replace("[SESS]", intell.originalsess)
        cadena = cadena.replace("[HOST]", intell.parsedurl.netloc)
        cadena = cadena.replace("[STHOST]", intell.parsedurl.netloc.replace("www.", ""))
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
        self.file = kwargs.get("file")


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


# -------------------------------------------------------------------------
class IntellCollector:
    """gathered data container"""
    instance = None

    # ---------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, *args, **kwargs)
            cls.__initialized = False
        return cls.instance

    # ---------------------------------------------------------------------
    def config(self, **kwargs):
        self.target = kwargs.get("target", None)

    # ---------------------------------------------------------------------
    def gather(self, params):
        out = Displayer()
        if params.url is not None:
            self.target = params.url
        else:
            self.target = str(input("url: "))
        originalreq = dorequest(self.target, params)
        m = re.search(b"(charset=(?P<value>.*)\")", originalreq['body'])
        if m:
            self.charset = m.group('value').decode()
        self.originalreq_lines = [x.decode(self.charset) for x in originalreq['body'].splitlines()]
        self.originalhead = originalreq['head']
        out.display(originalreq['head'])
        self.originalsess = getsess(originalreq['head'])
        self.parsedurl = urlparse(self.target)
        self.parametros = self.parsedurl.query.split('&')

    # ---------------------------------------------------------------------
    def show(self):
        out = Displayer()
        out.display("target: %s" % str(self.target))
        out.display("originalreq_lines: %s" % str(self.originalreq_lines))
        out.display("originalhead: %s" % str(self.originalhead))
        out.display("originalsess: %s" % str(self.originalsess))
        out.display("parsedurl: %s" % str(self.parsedurl))
        out.display("parametros: %s" % str(self.parametros))
        out.display("charset: %s" % str(self.charset))

    # ---------------------------------------------------------------------
    def __init__(self):
        if not self.__initialized:
            self.__initialized = True
            self.target = None
            self.originalreq_lines = []
            self.originalhead = None
            self.originalsess = None
            self.parsedurl = None
            self.parametros = []
            self.charset = 'utf-8'
