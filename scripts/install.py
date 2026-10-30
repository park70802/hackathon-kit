#!/usr/bin/env python3
"""Copy AGENTS.md, bundled Codex Skills, and PROGRESS.md into a task root.

No network, subprocess, git operations, or overwriting existing files.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent
SKILLS_ROOT = SOURCE / ".agents" / "skills"
PROGRESS_TEMPLATE = SOURCE / "templates" / "PROGRESS.md"


def plan_install(target: Path) -> list[tuple[Path, Path]]:
    target = target.expanduser().resolve()
    if not target.is_dir():
        raise ValueError(f"대상 폴더가 없습니다: {target}")

    sources = [(SOURCE / "AGENTS.md", target / "AGENTS.md")]
    sources.extend(
        (skill, target / ".agents" / "skills" / skill.name)
        for skill in sorted(SKILLS_ROOT.iterdir())
        if skill.is_dir()
    )
    sources.append((PROGRESS_TEMPLATE, target / "PROGRESS.md"))
    for src, _ in sources:
        if not src.exists():
            raise ValueError(f"원본 파일이 없습니다: {src}")
    return sources


def install(target: Path, *, dry_run: bool = False) -> list[Path]:
    items = plan_install(target)
    conflicts = [dst for _, dst in items if dst.exists() or dst.is_symlink()]
    if conflicts:
        raise FileExistsError(
            "기존 파일과 충돌합니다. 덮어쓰지 않았습니다. 과제 지침이 우선입니다:\n"
            + "\n".join(f" - {p}" for p in conflicts)
        )

    for src, dst in items:
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        print(("확인: " if dry_run else "설치: ") + str(dst))
    return [dst for _, dst in items]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Codex 지침, Skill 및 PROGRESS.md 복사 (기존 파일 덮어쓰기 없음)"
    )
    parser.add_argument("--target", required=True, type=Path, help="실제 과제 프로젝트 루트")
    parser.add_argument("--dry-run", action="store_true", help="복사하지 않고 대상 경로만 확인")
    args = parser.parse_args()
    try:
        install(args.target, dry_run=args.dry_run)
    except (OSError, ValueError) as exc:
        print("설치 중단:", exc)
        return 1
    print("완료. Codex가 실제 과제 프로젝트 경로에서 지침을 읽는지 별도로 확인하세요.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
