from __future__ import annotations


EXTERNAL_ID_MAX_LENGTH = 36


def validate_external_id(external_id: str | None) -> str | None:
    if external_id is not None and len(external_id) > EXTERNAL_ID_MAX_LENGTH:
        raise ValueError(
            f"external_id must be {EXTERNAL_ID_MAX_LENGTH} characters or fewer"
        )
    return external_id
