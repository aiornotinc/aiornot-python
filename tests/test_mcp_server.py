from aiornot import mcp_server


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


def test_mcp_module_imports_without_optional_dependency():
    assert callable(mcp_server.create_server)


def test_mcp_text_tool_reuses_operations(monkeypatch):
    fake_mcp = FakeMCP()
    mcp_server._register_tools(fake_mcp)

    calls = []

    def fake_analyze_text_value(text, external_id=None, include_annotations=False):
        calls.append(
            {
                "text": text,
                "external_id": external_id,
                "include_annotations": include_annotations,
            }
        )
        return {"id": "txt-1", "external_id": external_id}

    monkeypatch.setattr(
        "aiornot.operations.analyze_text_value",
        fake_analyze_text_value,
    )

    result = fake_mcp.tools["aiornot_analyze_text"](
        "hello",
        external_id="ext-1",
        include_annotations=True,
    )

    assert result == {"id": "txt-1", "external_id": "ext-1"}
    assert calls == [
        {
            "text": "hello",
            "external_id": "ext-1",
            "include_annotations": True,
        }
    ]
