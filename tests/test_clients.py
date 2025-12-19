"""Tests for sync and async client method signatures."""

import inspect

from aiornot import AsyncClient, Client


def test_matching_public_methods():
    """Ensure sync and async clients have matching public methods."""
    sync_methods = {
        name
        for name in dir(Client)
        if callable(getattr(Client, name)) and not name.startswith("_")
    }
    async_methods = {
        name
        for name in dir(AsyncClient)
        if callable(getattr(AsyncClient, name)) and not name.startswith("_")
    }

    assert sync_methods == async_methods, (
        f"Method mismatch. "
        f"Only in sync: {sync_methods - async_methods}. "
        f"Only in async: {async_methods - sync_methods}"
    )


def test_matching_signatures():
    """Ensure sync and async client methods have matching signatures."""
    sync_methods = [
        func
        for func in dir(Client)
        if callable(getattr(Client, func)) and not func.startswith("_")
    ]

    for method in sync_methods:
        sync_sig = inspect.signature(getattr(Client, method))
        async_sig = inspect.signature(getattr(AsyncClient, method))

        # Get parameter names and defaults, ignoring self
        sync_params = list(sync_sig.parameters.values())[1:]  # Skip 'self'
        async_params = list(async_sig.parameters.values())[1:]

        assert len(sync_params) == len(async_params), (
            f"Parameter count mismatch for {method}: "
            f"sync has {len(sync_params)}, async has {len(async_params)}"
        )

        for sync_p, async_p in zip(sync_params, async_params):
            assert sync_p.name == async_p.name, (
                f"Parameter name mismatch for {method}: "
                f"sync has {sync_p.name}, async has {async_p.name}"
            )
            assert sync_p.default == async_p.default or (
                sync_p.default is inspect.Parameter.empty
                and async_p.default is inspect.Parameter.empty
            ), (
                f"Default value mismatch for {method}.{sync_p.name}: "
                f"sync has {sync_p.default}, async has {async_p.default}"
            )


def test_client_has_required_methods():
    """Ensure clients have all the required methods."""
    required_methods = [
        # Core methods
        "is_live",
        # Image methods
        "image_report",
        "image_report_from_file",
        "image_report_batch",
        "image_report_directory",
        "image_report_from_csv",
        # Video methods
        "video_report",
        "video_report_from_file",
        "video_report_batch",
        "video_report_from_csv",
        # Voice methods
        "voice_report",
        "voice_report_from_file",
        "voice_report_batch",
        "voice_report_from_csv",
        # Music methods
        "music_report",
        "music_report_from_file",
        "music_report_batch",
        "music_report_from_csv",
        # Text methods
        "text_report",
        "text_report_batch",
    ]

    for method in required_methods:
        assert hasattr(Client, method), f"Client missing method: {method}"
        assert hasattr(AsyncClient, method), f"AsyncClient missing method: {method}"
