"""Batch operation result types."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generic, Iterator, Literal, TypeVar, Union

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass
class BatchResult(Generic[T]):
    """Result of a single item in a batch operation."""

    input: Union[str, Path, bytes]
    status: Literal["success", "error"]
    result: T | None = None
    error: str | None = None
    message: str | None = None
    duration_ms: float | None = None

    @property
    def success(self) -> bool:
        return self.status == "success"

    def to_jsonl(self) -> str:
        """Serialize to JSONL-compatible string."""
        if self.success:
            data = {
                "status": "success",
                "input": str(self.input),
                "result": self.result.model_dump() if self.result else None,
            }
        else:
            data = {
                "status": "error",
                "input": str(self.input),
                "error": self.error,
                "message": self.message,
            }
        if self.duration_ms is not None:
            data["duration_ms"] = self.duration_ms
        return json.dumps(data)


@dataclass
class BatchSummary(Generic[T]):
    """Summary of batch operation."""

    results: list[BatchResult[T]] = field(default_factory=list)
    total: int = 0
    succeeded: int = 0
    failed: int = 0

    @property
    def success_rate(self) -> float:
        return self.succeeded / self.total if self.total > 0 else 0.0

    def successful(self) -> list[T]:
        """Return list of successful results."""
        return [r.result for r in self.results if r.success and r.result is not None]

    def errors(self) -> list[BatchResult[T]]:
        """Return list of failed results."""
        return [r for r in self.results if not r.success]

    def to_jsonl(self) -> Iterator[str]:
        """Yield JSONL lines for all results + summary."""
        for r in self.results:
            yield r.to_jsonl()
        yield json.dumps(
            {
                "status": "summary",
                "total": self.total,
                "succeeded": self.succeeded,
                "failed": self.failed,
                "success_rate": self.success_rate,
            }
        )

    def write_jsonl(self, path: Union[str, Path]) -> None:
        """Write all results to a JSONL file."""
        with open(path, "w") as f:
            for line in self.to_jsonl():
                f.write(line + "\n")
