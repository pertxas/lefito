# -*- coding: utf-8 -*-
from api import Parameters, Displayer, IntellCollector, connect_tor, testip, menuppal
import argparse

# --------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="lefito hace cositas de lfi")
    parser.add_argument("-u", dest="url", help="target url")
    parser.add_argument("-p", dest="payloads", help="payloads file")
    parser.add_argument("-t", dest="tor", help="use tor")
    parser.add_argument("-c", dest="checkip", help="check ip")
    parser.add_argument("-a", dest="agent", help="custom user agent")
    parser.add_argument("-f", dest="file", help="outputfile")
    params = parser.parse_args()
    input_parameters = Parameters(url=params.url,
                                  payloads=params.payloads,
                                  tor=params.tor,
                                  checkip=params.checkip,
                                  file=params.file,
                                  agent=params.agent,)
    d = Displayer()
    d.config(out_screen=True,
             out_file=params.file,
             verbosity=1)
    i = IntellCollector()
    if params.tor is not None:
        connect_tor()
    if params.checkip is not None:
        testip(input_parameters)
    menuppal(input_parameters)
