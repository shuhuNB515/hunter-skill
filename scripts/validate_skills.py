#!/usr/bin/env python3
"""Validate hunter-skill core files and specialized sub-skills structure."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
CORE_FILES = [
    "README.md",
    "SKILL.md",
    "HACKER_MINDSET.md",
    "THREAT_KNOWLEDGE.md",
    "PLAYBOOK.md",
    "APP_PLAYBOOK.md",
    "RULES_butian.md",
    "VULN_DB.md",
    "config/variables.md",
]


def main() -> int:
    errors = []
    for rel in CORE_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"Missing core file: {rel}")

    skills_dir = ROOT / "skills"
    if not skills_dir.is_dir():
        errors.append("Missing skills/ directory")
        skill_dirs = []
    else:
        skill_dirs = sorted(
            p for p in skills_dir.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        )

    valid_skills = 0
    empty_dirs = []
    for sdir in skill_dirs:
        if not any(sdir.iterdir()):
            empty_dirs.append(sdir.name)
            continue
        has_md = any(sdir.glob("*.md")) or any(sdir.rglob("SKILL.md"))
        if not has_md:
            errors.append(f"Skill directory has no markdown entry: skills/{sdir.name}")
        else:
            valid_skills += 1

    print(f"Core files checked: {len(CORE_FILES)}")
    print(f"Sub-skill directories validated: {valid_skills}/{len(skill_dirs) - len(empty_dirs)}")
    if empty_dirs:
        print(f"Skipped empty local directories: {', '.join(empty_dirs)}")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
