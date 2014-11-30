# -*- coding: utf-8 -*-

import argparse
# --------------------------------------------------------------------------
class Parameters:
    """Program parameters"""
    # ----------------------------------------------------------------------
    def __init__(self, **kwargs):
        self.param1 = kwargs.get("param1")
        self.param2 = kwargs.get("param2")
        self.verbosity = kwargs.get("verbosity")
# --------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OMSTD Example')
    parser.add_argument("-p1", dest="param1", help="parameter1")
    parser.add_argument("-p2", dest="param1", help="parameter2")
    parser.add_argument("-v", dest="verbosity", type="int", help="verbosity")
    params = parser.parse_args()
    input_parameters = Parameters(param1=params.param1,
                                  param2=params.param2,
                                  verbosity=params.verbosity)
    d = divide(input_parameters)
    print(d)
