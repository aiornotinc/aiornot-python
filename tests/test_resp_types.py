from aiornot.resp_types import ImageResp, MusicResp, TextResp, VideoResp, VoiceResp


def test_image_free():
    data = {
        "created_at": "2023-11-28T20:06:30.130964Z",
        "id": "b2beb42b-9ef7-4d65-b52f-ac4d5b05e772",
        "report": {
            "ai_generated": {
                "verdict": "ai",
                "ai": {"is_detected": True, "confidence": 0.95},
                "human": {"is_detected": False, "confidence": 0.05},
                "generator": {},
            },
            "meta": {
                "width": 1024,
                "height": 768,
                "format": "jpg",
                "size_bytes": 204800,
                "md5": "abc123",
                "processing_status": {"ai_generated": "processed"},
            },
        },
    }

    resp = ImageResp(**data)
    assert resp.is_ai()


def test_image_premium():
    data = {
        "id": "52b65859-24e6-45c6-adda-927b82f810cf",
        "report": {
            "ai_generated": {
                "verdict": "ai",
                "ai": {"confidence": 0.9521987438201904, "is_detected": True},
                "human": {"confidence": 0.04780122637748718, "is_detected": False},
                "generator": {
                    "midjourney": 0.002055001212283969,
                    "dall_e": 2.053672869806178e-05,
                    "stable_diffusion": 2.974699054902885e-05,
                    "this_person_does_not_exist": 2.7012615646526683e-06,
                },
            },
            "deepfake": {"is_detected": False, "confidence": 0.1, "rois": []},
            "nsfw": {"version": "1.0.0", "is_detected": False},
            "quality": {"is_detected": True},
            "meta": {
                "width": 2048,
                "height": 1536,
                "format": "png",
                "size_bytes": 3145728,
                "md5": "def456",
                "processing_status": {
                    "ai_generated": "processed",
                    "deepfake": "processed",
                    "nsfw": "processed",
                    "quality": "processed",
                },
            },
        },
        "created_at": "2023-11-17T02:27:03.430897Z",
    }

    resp = ImageResp(**data)
    assert resp.is_ai()

    # Test forward compatibility - add an extra field
    data["foo"] = "bar"
    data["report"]["new_feature"] = {"detected": True}
    resp = ImageResp(**data)
    assert resp.is_ai()

    # Test that models accept extra fields
    assert hasattr(resp, "foo") is True  # Extra fields are accessible as attributes
    assert resp.foo == "bar"  # And have the expected value


def test_image_selected_report_without_ai_generated():
    data = {
        "id": "52b65859-24e6-45c6-adda-927b82f810cf",
        "created_at": "2026-05-19T20:06:30Z",
        "report": {
            "nsfw": {"is_detected": False},
            "reverse_search": {
                "was_found": True,
                "matches": [
                    {
                        "domain": "example.com",
                        "image_url": "https://example.com/image.jpg",
                    }
                ],
            },
            "meta": {
                "width": 2048,
                "height": 1536,
                "format": "png",
                "size_bytes": 3145728,
                "md5": "def456",
                "processing_status": {
                    "nsfw": "processed",
                    "reverse_search": "processed",
                },
            },
        },
    }

    resp = ImageResp(**data)
    assert not resp.is_ai()
    assert resp.report.nsfw is not None
    assert resp.report.nsfw.version is None
    assert resp.report.reverse_search is not None
    assert resp.report.reverse_search.matches[0].domain == "example.com"


def test_text_current_gateway_shape():
    data = {
        "id": "txt-1",
        "created_at": "2026-05-19T20:06:30Z",
        "report": {
            "ai_text": {
                "is_detected": True,
                "confidence": 0.91,
                "annotations": [{"start": 0, "end": 4}],
            }
        },
        "metadata": {
            "word_count": 500,
            "character_count": 2500,
            "token_count": 650,
            "md5": "abc123",
        },
        "external_id": "tracking-id",
    }

    resp = TextResp(**data)
    assert resp.is_ai()
    assert resp.metadata.word_count == 500
    assert resp.report.ai_text.annotations == [{"start": 0, "end": 4}]


def test_v1_voice_and_music_current_gateway_shape():
    data = {
        "id": "aud-1",
        "created_at": "2026-05-19T20:06:30Z",
        "report": {
            "verdict": "ai",
            "confidence": 0.82,
            "duration": 5,
            "total_bytes": 123456,
            "md5": "abc123",
        },
    }

    voice = VoiceResp(**data)
    music = MusicResp(**data)

    assert voice.is_ai()
    assert music.is_ai()
    assert voice.report.duration == 5
    assert music.report.total_bytes == 123456


def test_video_current_gateway_shape():
    data = {
        "id": "vid-1",
        "created_at": "2026-05-19T20:06:30Z",
        "external_id": "tracking-id",
        "report": {
            "ai_video": {"is_detected": False, "confidence": 0.2},
            "deepfake_video": {
                "is_detected": True,
                "confidence": 0.8,
                "no_faces_found": False,
            },
            "meta": {
                "duration": 12.4,
                "total_bytes": 123456,
                "md5": "def456",
                "audio": "processed",
                "video": "processed",
            },
        },
    }

    resp = VideoResp(**data)
    assert resp.is_ai()
    assert resp.report.meta.duration == 12.4
    assert resp.report.deepfake_video is not None
    assert resp.report.deepfake_video.no_faces_found is False
