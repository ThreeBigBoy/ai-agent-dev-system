#!/usr/bin/env python3
"""
OpenSpec Validate Tool v2.0 - 质量门禁自动化工具

扩展功能：
1. 目录结构验证（v1.0 基础功能）
2. 质量门禁检查清单自动化验证
3. 术语使用检查
4. Skill 版本一致性检查
5. 迭代日志记录格式验证
6. 评审修复循环检查

版本: v2.0
创建日期: 2026-03-17
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


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
    stage: Optional[str] = None  # 关联的 8+1 阶段
    suggestion: Optional[str] = None
    auto_fixable: bool = False  # 是否可自动修复


class QualityGateValidator:
    """质量门禁验证器（v2.0 质量门禁自动化）"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.openspec_dir = self.project_root / "openspec"
        self.specs_dir = self.openspec_dir / "specs"
        self.changes_dir = self.openspec_dir / "changes"
        self.archive_dir = self.changes_dir / "archive"
        self.design_dir = self.project_root / "design"
        self.iteration_log = self.design_dir / "documents" / "迭代日志.md"
        self.results: List[ValidationResult] = []
        
        # 8+1 阶段定义
        self.stages = [
            "Step 1: 需求分析",
            "Step 2: PRD 评审", 
            "Step 3: 工程结构分析",
            "Step 4: 技术方案评审",
            "Step 5: 编码实现",
            "Step 6: 代码评审",
            "Step 7: 功能验收",
            "Step 8: 归档",
            "Step 9: 复盘"
        ]

    def validate_all(self, change_id: Optional[str] = None, 
                     strict: bool = False,
                     check_quality_gate: bool = True,
                     check_terminology: bool = True,
                     check_skill_version: bool = True) -> List[ValidationResult]:
        """执行所有验证"""
        self.results = []

        # 1. 基础目录结构验证（v1.0 功能）
        self._validate_directory_structure()
        
        # 2. 质量门禁自动化检查（v2.0 新增）
        if check_quality_gate:
            self._validate_quality_gates()
        
        # 3. 术语使用检查（v2.0 新增）
        if check_terminology:
            self._validate_terminology_usage()
        
        # 4. Skill 版本一致性检查（v2.0 新增）
        if check_skill_version:
            self._validate_skill_versions()
        
        # 5. 迭代日志记录格式验证（v2.0 新增）
        self._validate_iteration_log()
        
        # 6. 指定 change-id 深度检查
        if change_id:
            self._validate_change_id_deep(change_id)

        return self.results

    def _validate_directory_structure(self):
        """验证基础目录结构（继承 v1.0）"""
        # 检查 openspec/ 目录
        if not self.openspec_dir.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                check_item="openspec/ 目录存在性",
                detail="openspec/ 目录不存在",
                stage="Step 1",
                suggestion="请创建 openspec/ 目录",
                auto_fixable=True
            ))
            return
        else:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item="openspec/ 目录存在性",
                detail="openspec/ 目录存在",
                stage="Step 1"
            ))

        # 检查迭代日志
        if not self.iteration_log.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                check_item="迭代日志存在性",
                detail="design/documents/迭代日志.md 不存在",
                stage="通用",
                suggestion="请创建迭代日志文件",
                auto_fixable=True
            ))
        else:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item="迭代日志存在性",
                detail="迭代日志存在",
                stage="通用"
            ))

    def _validate_quality_gates(self):
        """验证质量门禁自动化"""
        # 检查是否有质量门禁检查清单参考
        quality_gate_checklist = Path("/Users/billhu/Documents/AI OnePeace/AI Dev/01ProjectsDesignManage/ai-agent-dev-system") / "memory" / "preferences" / "preference-quality-gate-checklist.md"
        
        if quality_gate_checklist.exists():
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item="质量门禁检查清单可用性",
                detail="preference-quality-gate-checklist.md 存在，可用于质量门禁检查",
                stage="通用"
            ))
        else:
            self.results.append(ValidationResult(
                status=ValidationStatus.WARNING,
                check_item="质量门禁检查清单可用性",
                detail="质量门禁检查清单不存在",
                stage="通用",
                suggestion="请创建 preference-quality-gate-checklist.md"
            ))

        # 检查各阶段的质量门禁执行痕迹（通过迭代日志分析）
        if self.iteration_log.exists():
            log_content = self.iteration_log.read_text(encoding='utf-8')
            
            # 检查是否有质量门禁执行记录
            if "质量门禁" in log_content or "检查清单" in log_content:
                self.results.append(ValidationResult(
                    status=ValidationStatus.PASS,
                    check_item="质量门禁执行痕迹",
                    detail="迭代日志中发现质量门禁执行记录",
                    stage="通用"
                ))
            else:
                self.results.append(ValidationResult(
                    status=ValidationStatus.WARNING,
                    check_item="质量门禁执行痕迹",
                    detail="迭代日志中未发现质量门禁执行记录",
                    stage="通用",
                    suggestion="建议在迭代日志中记录质量门禁检查结果"
                ))

    def _validate_terminology_usage(self):
        """验证术语使用规范性"""
        # 检查关键术语的使用一致性
        terms_to_check = {
            "归档": ["合并 specs", "移动 changes", "archive"],
            "评审": ["通过", "有条件通过", "不通过", "修复循环"],
            "验收": ["通过", "有条件通过", "不通过"]
        }

        if self.iteration_log.exists():
            log_content = self.iteration_log.read_text(encoding='utf-8')
            
            # 检查归档术语使用
            if "归档" in log_content:
                if "合并 specs" in log_content or "移动 changes" in log_content:
                    self.results.append(ValidationResult(
                        status=ValidationStatus.PASS,
                        check_item="归档术语使用规范性",
                        detail="归档术语使用符合规范定义（合并 specs/ + 移动 changes/）",
                        stage="Step 8"
                    ))
                else:
                    self.results.append(ValidationResult(
                        status=ValidationStatus.WARNING,
                        check_item="归档术语使用规范性",
                        detail="归档术语使用可能不完整，缺少具体操作描述",
                        stage="Step 8",
                        suggestion="归档记录应包含：合并 specs/ + 移动 changes/"
                    ))

        # 检查是否存在术语定义漂移的迹象
        drift_indicators = ["标记完成", "简单完成", "基本完成"]
        if self.iteration_log.exists():
            log_content = self.iteration_log.read_text(encoding='utf-8')
            found_drift = any(indicator in log_content for indicator in drift_indicators)
            
            if found_drift:
                self.results.append(ValidationResult(
                    status=ValidationStatus.WARNING,
                    check_item="术语定义漂移风险",
                    detail="发现可能的术语定义漂移表达（如'标记完成'等模糊描述）",
                    stage="通用",
                    suggestion="使用精确术语：归档=合并 specs/ + 移动 changes/"
                ))
            else:
                self.results.append(ValidationResult(
                    status=ValidationStatus.PASS,
                    check_item="术语定义漂移风险",
                    detail="未发现明显的术语定义漂移表达",
                    stage="通用"
                ))

    def _validate_skill_versions(self):
        """验证 Skill 版本一致性"""
        skills_dir = Path("/Users/billhu/Documents/AI OnePeace/AI Dev/01ProjectsDesignManage/ai-agent-dev-system") / "skills"
        
        if not skills_dir.exists():
            return

        # 检查关键 skill 的版本
        key_skills = {
            "code-review": "v1.1",
            "func-test": "v1.1", 
            "prd-review": "v1.1",
            "architecture-review": "v1.1"
        }

        for skill_name, expected_version in key_skills.items():
            skill_file = skills_dir / skill_name / "SKILL.md"
            
            if not skill_file.exists():
                self.results.append(ValidationResult(
                    status=ValidationStatus.WARNING,
                    check_item=f"{skill_name} skill 存在性",
                    detail=f"{skill_name}/SKILL.md 不存在",
                    stage="通用",
                    suggestion=f"请确认 {skill_name} skill 已创建"
                ))
                continue

            # 读取 skill 文件检查版本
            content = skill_file.read_text(encoding='utf-8')
            
            # 查找版本声明
            version_patterns = [
                f"技能版本.*{expected_version}",
                f"version.*{expected_version}",
                f"v{expected_version.replace('v', '')}"
            ]
            
            found_version = any(re.search(pattern, content, re.IGNORECASE) for pattern in version_patterns)
            
            if found_version:
                self.results.append(ValidationResult(
                    status=ValidationStatus.PASS,
                    check_item=f"{skill_name} skill 版本",
                    detail=f"{skill_name} skill 版本符合预期（{expected_version}）",
                    stage="通用"
                ))
            else:
                self.results.append(ValidationResult(
                    status=ValidationStatus.WARNING,
                    check_item=f"{skill_name} skill 版本",
                    detail=f"{skill_name} skill 版本可能不是最新（预期 {expected_version}）",
                    stage="通用",
                    suggestion=f"建议升级 {skill_name} skill 到 {expected_version}"
                ))

    def _validate_iteration_log(self):
        """验证迭代日志记录格式"""
        if not self.iteration_log.exists():
            return

        content = self.iteration_log.read_text(encoding='utf-8')
        lines = content.split('\n')

        # 检查记录格式
        correct_format_count = 0
        incorrect_format_count = 0
        
        expected_pattern = r'\|\s*-\s*\d{4}-\d{2}-\d{2}\s*\|.*\|.*\|.*\|'

        for line in lines:
            if line.strip().startswith('|-') and '20' in line:  # 粗略筛选可能的记录行
                if re.search(expected_pattern, line):
                    correct_format_count += 1
                else:
                    incorrect_format_count += 1

        if incorrect_format_count == 0 and correct_format_count > 0:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item="迭代日志格式规范性",
                detail=f"迭代日志格式符合规范（{correct_format_count} 条记录）",
                stage="通用"
            ))
        elif incorrect_format_count > 0:
            self.results.append(ValidationResult(
                status=ValidationStatus.WARNING,
                check_item="迭代日志格式规范性",
                detail=f"发现 {incorrect_format_count} 条可能格式不规范的记录",
                stage="通用",
                suggestion="迭代日志记录格式：|- YYYY-MM-DD | change-id | Agent | 摘要 |"
            ))

        # 检查是否包含 change-id
        if "check-langgraph-backend" in content or "migrate-langgraph-backend" in content:
            self.results.append(ValidationResult(
                status=ValidationStatus.PASS,
                check_item="迭代日志 change-id 标注",
                detail="迭代日志中包含 change-id 标注",
                stage="通用"
            ))

    def _validate_change_id_deep(self, change_id: str):
        """深度验证指定 change-id"""
        # 基础存在性检查
        change_dir = self.changes_dir / change_id
        archived_dirs = []
        
        if self.archive_dir.exists():
            archived_dirs = [d for d in self.archive_dir.iterdir() 
                           if d.is_dir() and d.name.startswith(change_id)]

        if not change_dir.exists() and not archived_dirs:
            self.results.append(ValidationResult(
                status=ValidationStatus.FAIL,
                check_item=f"change-id '{change_id}' 存在性",
                detail=f"'{change_id}' 不存在",
                stage="通用"
            ))
            return

        # 检查评审修复循环痕迹
        if self.iteration_log.exists():
            content = self.iteration_log.read_text(encoding='utf-8')
            
            # 查找该 change-id 的记录
            change_records = [line for line in content.split('\n') if change_id in line]
            
            # 检查是否有评审记录
            review_records = [r for r in change_records if "评审" in r]
            rereview_records = [r for r in change_records if "重新评审" in r or "修复" in r]
            
            if review_records:
                self.results.append(ValidationResult(
                    status=ValidationStatus.PASS,
                    check_item=f"{change_id} 评审记录",
                    detail=f"发现 {len(review_records)} 条评审记录",
                    stage="Step 2/4/6"
                ))
                
                if rereview_records:
                    self.results.append(ValidationResult(
                        status=ValidationStatus.PASS,
                        check_item=f"{change_id} 评审修复循环",
                        detail=f"发现 {len(rereview_records)} 条重新评审/修复记录，评审修复循环已执行",
                        stage="Step 2/4/6"
                    ))

            # 检查是否有验收记录
            test_records = [r for r in change_records if "验收" in r or "func-test" in r]
            if test_records:
                self.results.append(ValidationResult(
                    status=ValidationStatus.PASS,
                    check_item=f"{change_id} 验收记录",
                    detail=f"发现 {len(test_records)} 条验收记录",
                    stage="Step 7"
                ))

            # 检查是否有归档记录
            archive_records = [r for r in change_records if "归档" in r]
            if archive_records:
                self.results.append(ValidationResult(
                    status=ValidationStatus.PASS,
                    check_item=f"{change_id} 归档记录",
                    detail=f"发现归档记录",
                    stage="Step 8"
                ))

    def print_results(self, show_details: bool = True):
        """打印验证结果"""
        print("\n" + "="*70)
        print("OpenSpec Validate Tool v2.0 - 质量门禁自动化验证结果")
        print("="*70)

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
        
        # 按阶段分组统计
        stage_stats = {}
        for r in self.results:
            stage = r.stage or "未分类"
            if stage not in stage_stats:
                stage_stats[stage] = {"total": 0, "pass": 0}
            stage_stats[stage]["total"] += 1
            if r.status == ValidationStatus.PASS:
                stage_stats[stage]["pass"] += 1
        
        if show_details and stage_stats:
            print("\n【按阶段统计】")
            for stage, stats in sorted(stage_stats.items()):
                pass_rate = stats["pass"] / stats["total"] * 100 if stats["total"] > 0 else 0
                print(f"  {stage}: {stats['pass']}/{stats['total']} 通过 ({pass_rate:.0f}%)")
        print()

        if show_details:
            # 按状态分组显示
            if fail_count > 0:
                print("【❌ 不通过项】")
                for result in self.results:
                    if result.status == ValidationStatus.FAIL:
                        stage_str = f"[{result.stage}] " if result.stage else ""
                        print(f"  • {stage_str}{result.check_item}")
                        print(f"    详情: {result.detail}")
                        if result.suggestion:
                            print(f"    建议: {result.suggestion}")
                        if result.auto_fixable:
                            print(f"    💡 可自动修复")
                        print()

            if warning_count > 0:
                print("【⚠️ 警告项】")
                for result in self.results:
                    if result.status == ValidationStatus.WARNING:
                        stage_str = f"[{result.stage}] " if result.stage else ""
                        print(f"  • {stage_str}{result.check_item}")
                        print(f"    详情: {result.detail}")
                        if result.suggestion:
                            print(f"    建议: {result.suggestion}")
                        print()

        # 总结
        print("="*70)
        if fail_count == 0:
            print("✅ 质量门禁验证通过！未发现严重问题。")
            if warning_count > 0:
                print(f"⚠️  有 {warning_count} 个警告项建议处理。")
        else:
            print(f"❌ 质量门禁验证未通过！有 {fail_count} 个必须修复的问题。")
        
        # 质量门禁报告输出
        if fail_count == 0:
            print("\n📊 质量门禁检查清单执行报告：")
            print(f"   - 目录结构检查: ✅ 通过")
            print(f"   - 术语使用检查: {'✅ 通过' if any('术语' in r.check_item and r.status == ValidationStatus.PASS for r in self.results) else '⚠️ 需关注'}")
            print(f"   - Skill 版本检查: {'✅ 通过' if any('skill 版本' in r.check_item and r.status == ValidationStatus.PASS for r in self.results) else '⚠️ 需关注'}")
            print(f"   - 迭代日志检查: {'✅ 通过' if any('迭代日志' in r.check_item and r.status == ValidationStatus.PASS for r in self.results) else '⚠️ 需关注'}")
        
        print("="*70)

        return fail_count == 0


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="OpenSpec Validate Tool v2.0 - 质量门禁自动化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础验证（目录结构）
  python openspec_validate_v2.py

  # 完整质量门禁验证
  python openspec_validate_v2.py --quality-gate

  # 验证指定 change-id
  python openspec_validate_v2.py --change-id check-langgraph-backend --quality-gate

  # 严格模式（质量门禁不通过则失败）
  python openspec_validate_v2.py --strict --quality-gate

  # 输出 JSON 格式
  python openspec_validate_v2.py --quality-gate --json
        """
    )

    parser.add_argument("--project", "-p", default=".", help="项目根目录路径")
    parser.add_argument("--change-id", "-c", default=None, help="验证指定的 change-id")
    parser.add_argument("--strict", "-s", action="store_true", help="严格模式")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--quality-gate", "-q", action="store_true", 
                       help="启用质量门禁检查（默认启用）")
    parser.add_argument("--no-quality-gate", action="store_true", 
                       help="禁用质量门禁检查")
    parser.add_argument("--no-terminology", action="store_true", 
                       help="禁用术语检查")
    parser.add_argument("--no-skill-version", action="store_true", 
                       help="禁用 Skill 版本检查")

    args = parser.parse_args()

    # 验证项目目录
    project_path = Path(args.project).resolve()
    if not project_path.exists():
        print(f"❌ 错误: 项目目录不存在: {project_path}")
        sys.exit(1)

    # 确定检查选项
    check_quality_gate = not args.no_quality_gate and (args.quality_gate or True)
    check_terminology = not args.no_terminology
    check_skill_version = not args.no_skill_version

    # 执行验证
    validator = QualityGateValidator(str(project_path))
    results = validator.validate_all(
        change_id=args.change_id,
        strict=args.strict,
        check_quality_gate=check_quality_gate,
        check_terminology=check_terminology,
        check_skill_version=check_skill_version
    )

    # 输出结果
    if args.json:
        output = []
        for r in results:
            output.append({
                "status": r.status.value,
                "check_item": r.check_item,
                "stage": r.stage,
                "detail": r.detail,
                "suggestion": r.suggestion,
                "auto_fixable": r.auto_fixable
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        success = validator.print_results(show_details=not args.json)

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
