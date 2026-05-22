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


def test_mcp_video_url_tool_reuses_operations(monkeypatch):
    fake_mcp = FakeMCP()
    mcp_server._register_tools(fake_mcp)

    calls = []

    def fake_analyze_video_url(
        url,
        output_dir="aiornot-downloads",
        max_duration=120,
        delete_after=False,
        external_id=None,
        only=None,
        excluding=None,
    ):
        calls.append(
            {
                "url": url,
                "output_dir": output_dir,
                "max_duration": max_duration,
                "delete_after": delete_after,
                "external_id": external_id,
                "only": only,
                "excluding": excluding,
            }
        )
        return {
            "download": {
                "url": url,
                "path": "aiornot-downloads/Sample [abc123].mp4",
                "deleted": delete_after,
                "max_duration": max_duration,
            },
            "response": {"id": "vid-1", "external_id": external_id},
        }

    monkeypatch.setattr(
        "aiornot.operations.analyze_video_url",
        fake_analyze_video_url,
    )

    result = fake_mcp.tools["aiornot_analyze_video_url"](
        "https://example.com/watch?v=abc123",
        output_dir="downloads",
        max_duration=300,
        delete_after=True,
        external_id="ext-1",
        only=["ai_video"],
        excluding=["deepfake_video"],
    )

    assert result["download"]["deleted"] is True
    assert calls == [
        {
            "url": "https://example.com/watch?v=abc123",
            "output_dir": "downloads",
            "max_duration": 300,
            "delete_after": True,
            "external_id": "ext-1",
            "only": ["ai_video"],
            "excluding": ["deepfake_video"],
        }
    ]


def test_mcp_voice_and_music_url_tools_reuse_operations(monkeypatch):
    fake_mcp = FakeMCP()
    mcp_server._register_tools(fake_mcp)

    calls = []

    def fake_analyze_voice_url(
        url,
        output_dir="aiornot-downloads",
        max_duration=3600,
        delete_after=False,
    ):
        calls.append(
            {
                "modality": "voice",
                "url": url,
                "output_dir": output_dir,
                "max_duration": max_duration,
                "delete_after": delete_after,
            }
        )
        return {
            "download": {
                "url": url,
                "path": "aiornot-downloads/Sample [abc123].webm",
                "deleted": delete_after,
                "max_duration": max_duration,
            },
            "response": {"id": "voice-1"},
        }

    def fake_analyze_music_url(
        url,
        output_dir="aiornot-downloads",
        max_duration=3600,
        delete_after=False,
    ):
        calls.append(
            {
                "modality": "music",
                "url": url,
                "output_dir": output_dir,
                "max_duration": max_duration,
                "delete_after": delete_after,
            }
        )
        return {
            "download": {
                "url": url,
                "path": "aiornot-downloads/Sample [abc123].m4a",
                "deleted": delete_after,
                "max_duration": max_duration,
            },
            "response": {"id": "music-1"},
        }

    monkeypatch.setattr(
        "aiornot.operations.analyze_voice_url",
        fake_analyze_voice_url,
    )
    monkeypatch.setattr(
        "aiornot.operations.analyze_music_url",
        fake_analyze_music_url,
    )

    voice_result = fake_mcp.tools["aiornot_analyze_voice_url"](
        "https://example.com/voice",
        output_dir="voice-downloads",
    )
    music_result = fake_mcp.tools["aiornot_analyze_music_url"](
        "https://example.com/music",
        max_duration=7200,
        delete_after=True,
    )

    assert voice_result["download"]["max_duration"] == 3600
    assert music_result["download"]["deleted"] is True
    assert calls == [
        {
            "modality": "voice",
            "url": "https://example.com/voice",
            "output_dir": "voice-downloads",
            "max_duration": 3600,
            "delete_after": False,
        },
        {
            "modality": "music",
            "url": "https://example.com/music",
            "output_dir": "aiornot-downloads",
            "max_duration": 7200,
            "delete_after": True,
        },
    ]
