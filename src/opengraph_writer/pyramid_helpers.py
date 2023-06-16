# stdlib
from typing import TYPE_CHECKING

# local
from . import OpenGraphItem

if TYPE_CHECKING:
    from pyramid.config import Configurator
    from pyramid.request import Request

# ==============================================================================


def new_OpenGraphItem(request: "Request") -> OpenGraphItem:
    """simply creates a new hub"""
    return OpenGraphItem()


def includeme(config: "Configurator") -> None:
    """
    the pyramid includeme command
    including this will automatically setup the OpenGraphItem object
    for every request
    """
    config.add_request_method(new_OpenGraphItem, "opengraph_item", reify=True)
