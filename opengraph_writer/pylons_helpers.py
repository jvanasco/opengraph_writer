from . import OpenGraphItem


def pylons_opengraph_item(c):
    """gets the opengraph item attached to the pylons c object. if non exists, makes a new one, attaches and returns it."""
    if not hasattr(c, 'pyramid_opengraph_item'):
        c.pyramid_opengraph_item = OpenGraphItem()
    return c.pyramid_opengraph_item
