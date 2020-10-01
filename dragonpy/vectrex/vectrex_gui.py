import logging

from dragonpy.core.gui import BaseTkinterGUI


log = logging.getLogger(__name__)


class VectrexGUI(BaseTkinterGUI):
    """
    The complete Tkinter GUI window
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def display_callback(self, *args, **kwargs):
        log.error(f'TODO: {args!r} {kwargs!r}')
