# -*- coding: utf-8 -*-
import socks
import socket
import mechanize
import re
from urlparse import urlparse
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
    print dorequest('http://echoip.com', params)


# --------------------------------------------------------------------------
def dorequest(url, params):
    req = mechanize.Request(url)
    if params.agent is not None:
        req.add_header("User-agent", params.agent)
    else:
        req.add_header("User-agent", "Soy el lefito.")
    result = {}
    try:
        respuesta = mechanize.urlopen(req)
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
    print "[0] Init Intelligence"
    print "[1] Start Recogn"
    print "[q] Quit"
    choice = str(raw_input("Select:"))
    return choice


# --------------------------------------------------------------------------
def initintell(intell, params):
    if params.url is not None:
        intell['target'] = params.url
    else:
        intell['target'] = str(raw_input("url: "))
    originalreq = dorequest(intell['target'], params)
    intell['originalreq_lines'] = originalreq['body'].splitlines()
    intell['originalhead'] = originalreq['head']
    print originalreq['head']
    intell['originalsess'] = getsess(originalreq['head'])
    intell['parsedurl'] = urlparse(intell['target'])
    intell['parametros'] = intell['parsedurl'].query.split('&')


# --------------------------------------------------------------------------
def startrecogn(intell, params):
    if params.payloads is not None:
        pause = raw_input("Pause? [y/n]")
        payloadslist = readpayloads(params.payloads)
        attack(intell, payloadslist, pause, params)
    else:
        selectedpayloadlist = menupayloads('./payloads')
        while selectedpayloadlist != 'q':
            pause = raw_input("Pause? [y/n]")
            payloadslist = readpayloads(selectedpayloadlist)
            attack(intell, payloadslist, pause, params)
            selectedpayloadlist = menupayloads('./payloads')
    return True


# --------------------------------------------------------------------------
def getsess(info):
    if 'set-cookie' in info:
        print info['set-cookie']
        m = re.search("(PHPSESSID=(?P<value>.*);)", info['set-cookie'])
        if m:
            print m.group('value')
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
    for parametro in intell['parametros']:
        urls = genurls(payloadslist, parametro, intell)
        for url in urls:
            print '-' * len(url)
            print url
            print '-' * len(url)
            req = "%s://%s%s?%s" % (intell['parsedurl'].scheme,
                                    intell['parsedurl'].netloc,
                                    intell['parsedurl'].path,
                                    url)
            result = dorequest(req, params)
            result_lines = result['body'].splitlines()
            d = difflib.Differ()
            diff = difflib.unified_diff(intell['originalreq_lines'], result_lines)
            for line in diff:
                if line.startswith('+'):
                    line = line.strip("+ ")
                    line = cleanhtml(line)
                    if len(line) > 1:
                        print line
            if pause == 'y':
                cont = raw_input('press enter to continue (q+enter to quit)')
                if cont == 'q':
                    return True


# --------------------------------------------------------------------------
def genurls(payloadslist, parametro, intell):
    valores = parametro.split('=')
    resultado = []
    for payload in payloadslist:
        str = payload.replace("[FOO]", valores[0])
        str = str.replace("[BAR]", valores[1])
        str = str.replace("[SESS]", intell['originalsess'])
        str = str.replace("[HOST]", intell['parsedurl'].netloc)
        str = str.replace("[STHOST]", intell['parsedurl'].netloc.replace("www.", ""))
        resultado.append(str)
    return resultado


# --------------------------------------------------------------------------
def menupayloads(dirname):
    listapayloads = os.listdir(dirname)
    n = 0
    listapayloads.sort()
    for payload in listapayloads:
        print "[%i] %s" % (n, payload)
        n += 1
    print "[q] Salir"
    try:
        select = int(raw_input("elige: "))
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
