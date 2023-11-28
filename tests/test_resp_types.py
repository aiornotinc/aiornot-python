from aiornot.resp_types import ImageResp


def test_image_free():
    data = {
        "created_at": "2023-11-28T20:06:30.130964Z",
        "facets": {
            "nsfw": {"is_detected": False, "version": "1.0.0"},
            "quality": {"is_detected": False, "version": "1.0.0"},
        },
        "id": "b2beb42b-9ef7-4d65-b52f-ac4d5b05e772",
        "report": {
            "ai": {"is_detected": True},
            "human": {"is_detected": False},
            "verdict": "ai",
        },
    }

    resp = ImageResp(**data)
    assert resp.is_ai()


def test_image_premium():
    data = {
      "id": "52b65859-24e6-45c6-adda-927b82f810cf",
      "report": {
        "verdict": "ai",
        "ai": {
          "confidence": 0.9521987438201904,
          "is_detected": True
        },
        "human": {
          "confidence": 0.04780122637748718,
          "is_detected": False
        },
        "generator": {
          "midjourney": {
            "confidence": 0.002055001212283969,
            "is_detected": False
          },
          "dall_e": {
            "confidence": 2.053672869806178e-05,
            "is_detected": False
          },
          "stable_diffusion": {
            "confidence": 2.974699054902885e-05,
            "is_detected": False
          },
          "this_person_does_not_exist": {
            "confidence": 2.7012615646526683e-06,
            "is_detected": False
          }
        }
      },
      "facets": {
        "nsfw": {
          "version": "1.0.0",
          "is_detected": False
        },
        "quality": {
          "version": "1.0.0",
          "is_detected": True
        }
      },
      "created_at": "2023-11-17T02:27:03.430897Z"
    }

    resp = ImageResp(**data)
    assert resp.is_ai()


    # add an extra field
    data["foo"] = "bar"
    resp = ImageResp(**data)
    assert resp.is_ai()

