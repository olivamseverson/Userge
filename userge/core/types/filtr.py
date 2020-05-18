# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Filtr', 'clear_db']

from typing import List, Tuple

from pyrogram.client.handlers.handler import Handler

from userge import logging, Config
from .. import client as _client, get_collection

_DISABLED_FILTERS = get_collection("DISABLED_FILTERS")
_UNLOADED_FILTERS = get_collection("UNLOADED_FILTERS")
_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  [[[[[  %s  ]]]]]  !>>>"

_DISABLED: List[str] = []
_UNLOADED: List[str] = []

for flt in _DISABLED_FILTERS.find():
    _DISABLED.append(flt['filter'])

for flt in _UNLOADED_FILTERS.find():
    _UNLOADED.append(flt['filter'])

def _init(name: str) -> Tuple[bool, bool]:
    name = name.lstrip(Config.CMD_TRIGGER)
    enabled = True
    loaded = True
    if name in _DISABLED:
        enabled = False
    if name in _UNLOADED:
        loaded = False
    return enabled, loaded

def _enable(name: str) -> None:
    name = name.lstrip(Config.CMD_TRIGGER)
    _DISABLED.remove(name)
    _DISABLED_FILTERS.delete_one({'filter': name})

def _disable(name: str) -> None:
    name = name.lstrip(Config.CMD_TRIGGER)
    _DISABLED.append(name)
    _DISABLED_FILTERS.insert_one({'filter': name})

def _load(name: str) -> None:
    name = name.lstrip(Config.CMD_TRIGGER)
    if name in _UNLOADED:
        _UNLOADED.remove(name)
        _UNLOADED_FILTERS.delete_one({'filter': name})

def _unload(name: str) -> None:
    name = name.lstrip(Config.CMD_TRIGGER)
    _UNLOADED.append(name)
    _UNLOADED_FILTERS.insert_one({'filter': name})

def clear_db() -> bool:
    """clear filters in DB"""
    _DISABLED.clear()
    _UNLOADED.clear()
    _DISABLED_FILTERS.drop()
    _UNLOADED_FILTERS.drop()
    _LOG.info(_LOG_STR, f"cleared filter DB!")
    return True

class Filtr:
    """filter class"""
    def __init__(self, client: '_client.Userge', group: int) -> None:
        self._client = client
        self._group = group
        self._enabled = True
        self._loaded = False
        self.name: str
        self.about: str
        self._handler: Handler

    def __repr__(self) -> str:
        return f"<filter - {self.name}>"

    def init(self) -> None:
        """initialize the filter"""
        self._enabled, loaded = _init(self.name)
        if loaded:
            self.load()

    @property
    def is_enabled(self) -> bool:
        """returns enable status"""
        return self._loaded and self._enabled

    @property
    def is_disabled(self) -> bool:
        """returns disable status"""
        return self._loaded and not self._enabled

    @property
    def is_loaded(self) -> bool:
        """returns load status"""
        return self._loaded

    def update_filter(self, name: str, about: str, handler: Handler) -> None:
        """update name, about and handler in filter"""
        self.name = name
        self.about = about
        self._handler = handler
        _LOG.debug(_LOG_STR, f"created filter -> {self.name}")

    def enable(self) -> str:
        """enable the filter"""
        if self._enabled:
            return ''
        self._enabled = True
        _enable(self.name)
        _LOG.debug(_LOG_STR, f"enabled filter -> {self.name}")
        return self.name

    def disable(self) -> str:
        """disable the filter"""
        if not self._enabled:
            return ''
        self._enabled = False
        _disable(self.name)
        _LOG.info(_LOG_STR, f"disabled filter -> {self.name}")
        return self.name

    def load(self) -> str:
        """load the filter"""
        if self._loaded:
            return ''
        self._client.add_handler(self._handler, self._group)
        self._loaded = True
        _load(self.name)
        _LOG.debug(_LOG_STR, f"loaded filter -> {self.name}")
        return self.name

    def unload(self) -> str:
        """unload the filter"""
        if not self._loaded:
            return ''
        self._client.remove_handler(self._handler, self._group)
        self._loaded = False
        _unload(self.name)
        _LOG.info(_LOG_STR, f"unloaded filter -> {self.name}")
        return self.name