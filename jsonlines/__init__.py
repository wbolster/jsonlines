
__version__ = '0.0.1'
__version_info__ = tuple(map(int, __version__.split('.')))


# Import public API
from .jsonlines import (  # noqa
    Reader,
    Writer,
    open,
)
