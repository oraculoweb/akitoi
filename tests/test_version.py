"""
Basic tests for the Akitoi package.
"""
import akitoi


def test_version():
    """Test that version is defined."""
    assert hasattr(akitoi, "__version__")
    assert isinstance(akitoi.__version__, str)
    assert akitoi.__version__ == "0.1.0"


def test_package_metadata():
    """Test package metadata attributes."""
    assert hasattr(akitoi, "__author__")
    assert hasattr(akitoi, "__email__")
    assert isinstance(akitoi.__author__, str)
    assert isinstance(akitoi.__email__, str)
