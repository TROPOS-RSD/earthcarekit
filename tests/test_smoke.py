"""Minimal smoke tests so CI validates imports and package metadata."""


def test_package_version() -> None:
    import earthcarekit as eck

    assert isinstance(eck.__version__, str)
    assert len(eck.__version__) > 0
