"""Iteration management for Spec Iter projects."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def to_kebab_case(name: str) -> str:
    """Convert arbitrary text to lowercase kebab-case."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", name)
    return normalized.strip("-").lower()


class IterManager:
    """Manage Spec Iter iteration metadata and paths."""

    VALID_STAGES = ["new", "specified", "planned", "executed", "completed"]

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.speciter_dir = self.project_root / ".speciter"
        self.iters_file = self.speciter_dir / "iters.json"
        self.iterations_dir = self.speciter_dir / "iterations"

    def load_iters(self) -> dict:
        if self.iters_file.exists():
            return json.loads(self.iters_file.read_text(encoding="utf-8"))
        return {"iterations": []}

    def save_iters(self, data: dict) -> None:
        self.speciter_dir.mkdir(parents=True, exist_ok=True)
        self.iterations_dir.mkdir(parents=True, exist_ok=True)
        self.iters_file.write_text(
            json.dumps(data, indent=4) + "\n",
            encoding="utf-8",
        )

    def verify_iters_file_exists(self) -> None:
        if not self.iters_file.exists():
            raise FileNotFoundError(
                "iters.json not found. Run `spec-iter init` to initialize the project."
            )

    def resolve_iteration_id(self, iter_id: str) -> str:
        self.verify_iters_file_exists()
        iterations = self.load_iters().get("iterations", [])

        try:
            numeric_id = int(iter_id)
        except ValueError as exc:
            raise ValueError(
                f"Invalid iteration ID '{iter_id}': must be a number >= 1"
            ) from exc

        if numeric_id < 1:
            raise ValueError(f"Iteration ID must be >= 1, got {numeric_id}")
        if numeric_id > len(iterations):
            raise ValueError(
                f"Iteration #{numeric_id} not found (only {len(iterations)} iterations)"
            )

        return iterations[numeric_id - 1]["name"]

    def create_iteration(self, name: str) -> tuple[str, Path]:
        kebab_name = to_kebab_case(name)
        if not kebab_name:
            raise ValueError(f"Invalid iteration name '{name}'")

        data = self.load_iters()
        if any(item["name"] == kebab_name for item in data.get("iterations", [])):
            raise ValueError(f"Iteration '{kebab_name}' already exists")

        iteration_dir = self.iterations_dir / kebab_name
        iteration_dir.mkdir(parents=True, exist_ok=True)

        data.setdefault("iterations", []).append(
            {
                "time": datetime.now().isoformat(),
                "name": kebab_name,
                "stage": "new",
            }
        )
        data["iterations"].sort(key=lambda item: item["time"], reverse=True)
        self.save_iters(data)
        return kebab_name, iteration_dir

    def list_iterations(self, limit: Optional[int] = None) -> list[dict]:
        self.verify_iters_file_exists()
        iterations = self.load_iters().get("iterations", [])
        return iterations if limit is None else iterations[:limit]

    def get_iteration_path(self, iter_id: str) -> Path:
        return self.iterations_dir / self.resolve_iteration_id(iter_id)

    def get_spec_path(self, iter_id: str) -> Path:
        return self.get_iteration_path(iter_id) / "SPEC.md"

    def get_plan_path(self, iter_id: str) -> Path:
        return self.get_iteration_path(iter_id) / "PLAN.md"

    def get_iteration_stage(self, iter_id: str) -> str:
        resolved_id = self.resolve_iteration_id(iter_id)
        for iteration in self.list_iterations():
            if iteration["name"] == resolved_id:
                return iteration["stage"]
        raise ValueError(f"Iteration '{iter_id}' not found")

    def update_iteration_stage(self, iter_id: str, stage: str) -> None:
        self.verify_iters_file_exists()
        if stage not in self.VALID_STAGES:
            raise ValueError(
                f"Invalid stage '{stage}'. Valid stages: {', '.join(self.VALID_STAGES)}"
            )

        resolved_id = self.resolve_iteration_id(iter_id)
        data = self.load_iters()

        for iteration in data.get("iterations", []):
            if iteration["name"] == resolved_id:
                iteration["stage"] = stage
                iteration["time"] = datetime.now().isoformat()
                break
        else:
            raise ValueError(f"Iteration '{iter_id}' not found")

        data["iterations"].sort(key=lambda item: item["time"], reverse=True)
        self.save_iters(data)
