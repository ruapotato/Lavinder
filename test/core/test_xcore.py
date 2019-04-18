import pytest

from ..conftest import BareConfig
from liblavinder.core import xcore


@pytest.mark.parametrize("lavinder", [BareConfig], indirect=True)
def test_keys(lavinder):
    xc = xcore.XCore()
    assert "a" in xc.get_keys()
    assert "shift" in xc.get_modifiers()
