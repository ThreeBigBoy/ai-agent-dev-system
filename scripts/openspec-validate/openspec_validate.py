#!/usr/bin/env python3
"""
OpenSpec Validate Tool
用于验证 OpenSpec 目录结构的完整性和一致性

功能：
1. 验证 specs/ 目录结构
2. 验证 changes/ 和 changes/archive/ 目录结构
3. 检查归档完整性
4. 验证 change-id 是否存在

版本: v1.0
创建日期: 2026-03-17
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationStatus(Enum):
    """验证状态"""
    PASS = "✅ 通过"
    FAIL = "❌ 不通过"
    WARNING = "⚠️ 警告"
    INFO = "ℹ️ 信息"


@dataclass
class ValidationResult:
    """验证结果"""
    status: ValidationStatus
    check_item: str
    detail: str
    suggestion: Optional[str] = None


class OpenSpecValidator:
    """OpenSpec 验证器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.openspec_dir = self.project_root / "openspec"
        self.specs_dir = self.openspec_dir / "specs"
        self.changes_dir = self.openspec_dir / "changes"
        self.archive_dir = self.changes_dir / "archive"
        self.results: List[ValidationResult] = []

    def validate_all(self, change_id: Optional[str] = None) -> List[ValidationResult]:
        """执行所有验证"""
        self.results = []

        # 1. 验证目录结构
        self._validate_directory_structure()

        # 2. 验证 specs/ 结构
        self._validate_specs_structure()

        # 3. 验证 changes/ 结构
        self._validate_changes_structure()

        # 4. 验证 archive/ 结构
        self._validate_archive_structure()

        # 5. 如果指定了 change-id，验证该 change-id
        if change_id:
            self._validate_change_id(change_id)

        return self.results

    def _validate_directory_structure(self):
        """验证基本目录结构"""
        # 检查 openspec/ 目录
        if not self.openspec_dir.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                check_item="openspec/ 目录存在性",
                detail="openspec/ 目录不存在",
                suggestion="请创建 openspec/ 目录"
            ))
            return
        else:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item="openspec/ 目录存在性",
                detail="openspec/ 目录存在"
            ))

        # 检查 specs/ 目录
        if not self.specs_dir.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.WARNING,
                check_item="openspec/specs/ 目录存在性",
                detail="specs/ 目录不存在",
                suggestion="请创建 openspec/specs/ 目录用于存放已实现的规范"
            ))
        else:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item="openspec/specs/ 目录存在性",
                detail="specs/ 目录存在"
            ))

        # 检查 changes/ 目录
        if not self.changes_dir.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.WARNING,
                check_item="openspec/changes/ 目录存在性",
                detail="changes/ 目录不存在",
                suggestion="请创建 openspec/changes/ 目录用于存放变更提案"
            ))
        else:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item="openspec/changes/ 目录存在性",
                detail="changes/ 目录存在"
            ))

    def _validate_specs_structure(self):
        """验证 specs/ 目录结构"""
        if not self.specs_dir.exists():
            return

        # 获取所有 capability 目录
        capabilities = [d for d in self.specs_dir.iterdir() if d.is_dir()]

        if not capabilities:
            self.results.append(ValidationResult(
                status=ValidationStatus.INFO,
                check_item="specs/ 能力目录",
                detail="specs/ 下暂无能力目录",
                suggestion="可以创建能力目录（如 user-auth/、payment/ 等）"
            ))

        for cap_dir in capabilities:
            spec_file = cap_dir / "spec.md"
            if not spec_file.exists():
                self.results.append(ValidationResult(
                    status=ValidationStatus.WARNING,
                    check_item=f"specs/{cap_dir.name}/spec.md 存在性",
                    detail=f"{cap_dir.name}/spec.md 不存在",
                    suggestion=f"请创建 {cap_dir.name}/spec.md 描述该能力规范"
                ))
            else:
                self.results.append(ValidationResult(
                    status=ValidationStatus.PASS,
                    check_item=f"specs/{cap_dir.name}/spec.md 存在性",
                    detail=f"{cap_dir.name}/spec.md 存在"
                ))

    def _validate_changes_structure(self):
        """验证 changes/ 目录结构（非 archive 部分）"""
        if not self.changes_dir.exists():
            return

        # 获取所有 change-id 目录（排除 archive）
        change_dirs = [d for d in self.changes_dir.iterdir()
                      if d.is_dir() and d.name != "archive" and not d.name.startswith(".")]

        if not change_dirs:
            self.results.append(ValidationResult(
                status=ValidationStatus.INFO,
                check_item="changes/ 变更目录",
                detail="changes/ 下暂无进行中的变更",
                suggestion="可以创建变更目录（如 add-feature-x/）"
            ))

        for change_dir in change_dirs:
            self._validate_single_change(change_dir, is_archive=False)

    def _validate_archive_structure(self):
        """验证 changes/archive/ 目录结构"""
        if not self.archive_dir.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.INFO,
                check_item="changes/archive/ 目录",
                detail="archive/ 目录不存在，暂无归档变更",
                suggestion="归档操作时会自动创建"
            ))
            return

        # 获取所有归档的 change-id 目录
        archived_changes = [d for d in self.archive_dir.iterdir()
                           if d.is_dir() and not d.name.startswith(".")]

        if not archived_changes:
            self.results.append(ValidationResult(
                status=ValidationStatus.INFO,
                check_item="changes/archive/ 归档变更",
                detail="archive/ 下暂无归档变更"
            ))

        for archived_dir in archived_changes:
            self._validate_single_change(archived_dir, is_archive=True)

    def _validate_single_change(self, change_dir: Path, is_archive: bool):
        """验证单个 change-id 目录的结构"""
        prefix = "归档 " if is_archive else ""
        location = f"changes/archive/{change_dir.name}" if is_archive else f"changes/{change_dir.name}"

        # 检查 proposal.md
        proposal_file = change_dir / "proposal.md"
        if not proposal_file.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                check_item=f"{prefix}{location}/proposal.md 存在性",
                detail=f"{location}/proposal.md 不存在",
                suggestion="变更提案是必需的，请创建 proposal.md"
            ))
        else:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item=f"{prefix}{location}/proposal.md 存在性",
                detail=f"{location}/proposal.md 存在"
            ))

        # 检查 tasks.md
        tasks_file = change_dir / "tasks.md"
        if not tasks_file.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                check_item=f"{prefix}{location}/tasks.md 存在性",
                detail=f"{location}/tasks.md 不存在",
                suggestion="任务清单是必需的，请创建 tasks.md"
            ))
        else:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item=f"{prefix}{location}/tasks.md 存在性",
                detail=f"{location}/tasks.md 存在"
            ))

        # 检查 specs/ 目录（可选）
        specs_dir = change_dir / "specs"
        if specs_dir.exists():
            capabilities = [d for d in specs_dir.iterdir() if d.is_dir()]
            for cap_dir in capabilities:
                spec_file = cap_dir / "spec.md"
                if spec_file.exists():
                    self.results.append(ValidationResult(
                        status=ValidationStatus.PASS,
                        check_item=f"{prefix}{location}/specs/{cap_dir.name}/spec.md 存在性",
                        detail=f"{location}/specs/{cap_dir.name}/spec.md 存在"
                    ))

    def _validate_change_id(self, change_id: str):
        """验证指定的 change-id"""
        # 检查是否在 changes/
        change_dir = self.changes_dir / change_id
        # 检查是否在 changes/archive/
        archived_dir = self.archive_dir / f"{change_id}"

        # 查找可能的后缀（如日期）
        archived_dirs = []
        if self.archive_dir.exists():
            archived_dirs = [d for d in self.archive_dir.iterdir()
                           if d.is_dir() and d.name.startswith(change_id)]

        if change_dir.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item=f"change-id '{change_id}' 存在性",
                detail=f"'{change_id}' 存在于 changes/（进行中）"
            ))
        elif archived_dirs:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item=f"change-id '{change_id}' 存在性",
                detail=f"'{change_id}' 已归档于 changes/archive/{archived_dirs[0].name}"
            ))
        else:
            self.results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                check_item=f"change-id '{change_id}' 存在性",
                detail=f"'{change_id}' 不存在于 changes/ 或 changes/archive/",
                suggestion=f"请确认 change-id 拼写正确，或检查 openspec/ 目录"
            ))

    def print_results(self):
        """打印验证结果"""
        print("\n" + "="*60)
        print("OpenSpec Validate Tool - 验证结果")
        print("="*60)

        # 统计
        pass_count = sum(1 for r in self.results if r.status == ValidationStatus.PASS)
        fail_count = sum(1 for r in self.results if r.status == ValidationStatus.FAIL)
        warning_count = sum(1 for r in self.results if r.status == ValidationStatus.WARNING)
        info_count = sum(1 for r in self.results if r.status == ValidationStatus.INFO)

        print(f"\n总检查项: {len(self.results)}")
        print(f"  ✅ 通过: {pass_count}")
        print(f"  ❌ 不通过: {fail_count}")
        print(f"  ⚠️ 警告: {warning_count}")
        print(f"  ℹ️ 信息: {info_count}")
        print()

        # 按状态分组显示
        if fail_count > 0:
            print("【❌ 不通过项】")
            for result in self.results:
                if result.status == ValidationStatus.FAIL:
                    print(f"  • {result.check_item}")
                    print(f"    详情: {result.detail}")
                    if result.suggestion:
                        print(f"    建议: {result.suggestion}")
                    print()

        if warning_count > 0:
            print("【⚠️ 警告项】")
            for result in self.results:
                if result.status == ValidationStatus.WARNING:
                    print(f"  • {result.check_item}")
                    print(f"    详情: {result.detail}")
                    if result.suggestion:
                        print(f"    建议: {result.suggestion}")
                    print()

        if info_count > 0:
            print("【ℹ️ 信息项】")
            for result in self.results:
                if result.status == ValidationStatus.INFO:
                    print(f"  • {result.check_item}: {result.detail}")
            print()

        # 总结
        print("="*60)
        if fail_count == 0:
            print("✅ 验证通过！未发现严重问题。")
            if warning_count > 0:
                print(f"⚠️  有 {warning_count} 个警告项建议处理。")
        else:
            print(f"❌ 验证未通过！有 {fail_count} 个必须修复的问题。")
        print("="*60)

        return fail_count == 0


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="OpenSpec Validate Tool - 验证 OpenSpec 目录结构完整性",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 验证当前目录的 OpenSpec 结构
  python openspec_validate.py

  # 验证指定项目目录
  python openspec_validate.py --project /path/to/project

  # 验证指定的 change-id
  python openspec_validate.py --change-id add-feature-x

  # 严格模式（将警告视为不通过）
  python openspec_validate.py --strict
        """
    )

    parser.add_argument(
        "--project", "-p",
        default=".",
        help="项目根目录路径（默认: 当前目录）"
    )

    parser.add_argument(
        "--change-id", "-c",
        default=None,
        help="验证指定的 change-id 是否存在"
    )

    parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="严格模式（将警告视为不通过）"
    )

    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="以 JSON 格式输出结果"
    )

    args = parser.parse_args()

    # 验证项目目录
    project_path = Path(args.project).resolve()
    if not project_path.exists():
        print(f"❌ 错误: 项目目录不存在: {project_path}")
        sys.exit(1)

    # 执行验证
    validator = OpenSpecValidator(str(project_path))
    results = validator.validate_all(change_id=args.change_id)

    # 输出结果
    if args.json:
        # JSON 格式输出
        output = []
        for r in results:
            output.append({
                "status": r.status.value,
                "check_item": r.check_item,
                "detail": r.detail,
                "suggestion": r.suggestion
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        success = validator.print_results()

    # 返回退出码
    fail_count = sum(1 for r in results if r.status == ValidationStatus.FAIL)
    warning_count = sum(1 for r in results if r.status == ValidationStatus.WARNING)

    if fail_count > 0:
        sys.exit(1)
    elif args.strict and warning_count > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
