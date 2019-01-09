import os
import locale
from datetime import datetime
from collections import OrderedDict
from os import environ
from termcolor import colored
from n_utils.log_events import fmttime
from n_utils.cf_utils import log
from n_utils import PARAM_NOT_AVAILABLE

class LazyParam(object):

    def __init__(self, matcher, resolver):
        self.matcher = matcher
        self.resolver = resolver
        self.resolving_failed = False

    def __eq__(self, other):
        return self.matcher == other.matcher and self.resolver == other.resolver

class LazyOrderedDict(OrderedDict):

    def __init__(*args, **kwds):
        self = args[0]
        OrderedDict.__init__(*args, **kwds)
        self.lazy_params = []

    def add_lazyparam(self, matcher, resolver):
        self.lazy_params.append(LazyParam(matcher, resolver))

    def __getitem__(self, key):
        ret = None
        try:
            if "LAZY_DEBUG" in environ:
                log("Getting " + key)
            return OrderedDict.__getitem__(self, key)
        except KeyError as ke:
            ret = self._lazy_resolve(key)
            if ret:
                return ret
            else:
                raise ke

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        if value == PARAM_NOT_AVAILABLE:
            res_val = self._lazy_resolve(key)
            if res_val:
                value = res_val
        OrderedDict.__setitem__(self, key, value, dict_setitem=dict.__setitem__)

    def __contains__(self, key):
        if not OrderedDict.__contains__(self, key):
            ret = self._lazy_resolve(key)
            if ret:
                return True
            else:
                return False
        return True

    def _lazy_resolve(self, key):
        ret = None
        for lz_param in self.lazy_params:
            if not lz_param.resolving_failed and lz_param.matcher(key):
                ret = lz_param.resolver(key)
                if ret:
                    self.__setitem__(key, ret)
                else:
                    lz_param.resolving_failed = True
        return ret

    def update(self, other):
        OrderedDict.update(self, other)
        if isinstance(other, LazyOrderedDict):
            for lazy_param in other.lazy_params:
                if not lazy_param in self.lazy_params:
                    self.lazy_params.append(lazy_param)      
