from aiornot import Client, AsyncClient
import inspect


def test_matching_signatures():
    sync_methods = [
        func
        for func in dir(Client)
        if callable(getattr(Client, func)) and not func.startswith("_")
    ]
    async_methods = [
        func
        for func in dir(AsyncClient)
        if callable(getattr(AsyncClient, func)) and not func.startswith("_")
    ]

    assert set(sync_methods) == set(async_methods)

    # For each method, check that the signatures match
    for method in sync_methods:
        sync_sig = inspect.signature(getattr(Client, method))
        async_sig = inspect.signature(getattr(AsyncClient, method))
        assert sync_sig == async_sig
