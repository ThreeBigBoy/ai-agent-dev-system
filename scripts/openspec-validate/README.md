# OpenSpec Validate Tool

OpenSpec 目录结构验证工具，用于验证 OpenSpec 项目的目录结构完整性和一致性。

## 功能

1. **目录结构验证**: 验证 `openspec/`、`specs/`、`changes/`、`changes/archive/` 目录结构
2. **变更完整性检查**: 检查指定 change-id 的目录结构和必需文件
3. **归档完整性验证**: 验证归档操作的完整性（specs/ 合并 + changes/ 移动）
4. **规范性检查**: 检查 proposal.md、tasks.md、spec.md 等必需文件

## 安装

```bash
# 复制到项目目录
cp -r openspec-validate /path/to/your/project/scripts/

# 或者创建符号链接
ln -s /path/to/openspec-validate/openspec_validate.py /usr/local/bin/openspec-validate
```

## 使用方法

### v1.0 基础用法（目录结构验证）

```bash
# 验证当前目录的 OpenSpec 结构
python openspec_validate.py

# 验证指定项目目录
python openspec_validate.py --project /path/to/project

# 验证指定的 change-id
python openspec_validate.py --change-id add-feature-x

# 严格模式（将警告视为不通过）
python openspec_validate.py --strict

# 以 JSON 格式输出
python openspec_validate.py --json
```

### v2.0 质量门禁自动化验证（推荐）

```bash
# 完整质量门禁验证（默认启用质量门禁检查）
python openspec_validate_v2.py --quality-gate

# 验证指定 change-id 的质量门禁
python openspec_validate_v2.py --change-id check-langgraph-backend --quality-gate

# 严格模式质量门禁验证（警告视为不通过）
python openspec_validate_v2.py --quality-gate --strict

# 基础验证（禁用质量门禁，仅检查目录结构）
python openspec_validate_v2.py --no-quality-gate

# 自定义检查项
python openspec_validate_v2.py --quality-gate --no-terminology --no-skill-version

# JSON 格式输出（便于 CI/CD 集成）
python openspec_validate_v2.py --quality-gate --json
```

### 使用示例

```bash
# 验证 ai-agent-dev-system 项目
cd /path/to/ai-agent-dev-system
python scripts/openspec-validate/openspec_validate.py

# 输出示例
============================================================
OpenSpec Validate Tool - 验证结果
============================================================

总检查项: 15
  ✅ 通过: 12
  ❌ 不通过: 0
  ⚠️ 警告: 2
  ℹ️ 信息: 1

【⚠️ 警告项】
  • openspec/changes/archive/ 目录
    详情: archive/ 目录不存在，暂无归档变更
    建议: 归档操作时会自动创建

============================================================
✅ 验证通过！未发现严重问题。
⚠️  有 2 个警告项建议处理。
============================================================
```

## 检查项说明

### 基本目录结构
- ✅ openspec/ 目录存在性
- ✅ openspec/specs/ 目录存在性
- ✅ openspec/changes/ 目录存在性

### specs/ 目录
- ✅ specs/[capability]/ 能力目录
- ✅ specs/[capability]/spec.md 规范文档

### changes/ 目录（进行中变更）
- ✅ changes/[change-id]/proposal.md 变更提案
- ✅ changes/[change-id]/tasks.md 任务清单
- ✅ changes/[change-id]/specs/[capability]/spec.md 规范增量（可选）

### changes/archive/ 目录（已归档变更）
- ✅ changes/archive/[change-id]-YYYY-MM-DD/ 归档目录
- ✅ 归档目录完整性检查

## v2.0 质量门禁自动化验证详细说明

### 新增功能

| 功能 | 说明 | 命令行选项 |
|-----|------|-----------|
| **质量门禁检查** | 自动化验证质量门禁执行 | `--quality-gate` (默认启用) |
| **术语使用检查** | 检测术语定义漂移 | `--no-terminology` (禁用) |
| **Skill 版本检查** | 验证 skill 版本一致性 | `--no-skill-version` (禁用) |
| **阶段统计** | 按 8+1 阶段统计检查结果 | 自动输出 |
| **深度 change-id 检查** | 评审/验收/归档记录验证 | `--change-id [id]` |

### 质量门禁自动化检查项

#### 1. 质量门禁检查清单验证
- 检查 `preference-quality-gate-checklist.md` 是否存在
- 分析迭代日志中的质量门禁执行记录
- 按阶段统计质量门禁执行情况

#### 2. 术语使用规范性验证
- **高风险检测**: 检测模糊表达（如"标记完成"、"简单完成"）
- **归档术语检查**: 验证是否包含"合并 specs/ + 移动 changes/"
- **评审术语检查**: 验证"有条件通过"等术语使用

#### 3. Skill 版本一致性验证
检查以下 skill 是否为预期版本：
- code-review v1.1
- func-test v1.1
- prd-review v1.1
- architecture-review v1.1

#### 4. 迭代日志格式验证
- 验证迭代日志文件存在性
- 检查记录格式规范性
- 统计记录数量和格式合规性

#### 5. 指定 change-id 深度验证
当使用 `--change-id` 时，额外检查：
- 评审记录（首次评审 + 重新评审）
- 评审修复循环执行痕迹
- 验收记录
- 归档记录

### v2.0 使用示例

```bash
# 示例 1: 完整质量门禁验证
cd /path/to/ai-agent-dev-system
python scripts/openspec-validate/openspec_validate_v2.py --quality-gate

# 输出示例
======================================================================
OpenSpec Validate Tool v2.0 - 质量门禁自动化验证结果
======================================================================

总检查项: 12
  ✅ 通过: 10
  ❌ 不通过: 0
  ⚠️ 警告: 2
  ℹ️ 信息: 0

【按阶段统计】
  Step 1: 1/1 通过 (100%)
  Step 8: 1/1 通过 (100%)
  通用: 8/10 通过 (80%)

【⚠️ 警告项】
  • [通用] 术语定义漂移风险
    详情: 发现可能的术语定义漂移表达
    建议: 使用精确术语：归档=合并 specs/ + 移动 changes/

======================================================================
✅ 质量门禁验证通过！未发现严重问题。
📊 质量门禁检查清单执行报告：
   - 目录结构检查: ✅ 通过
   - 术语使用检查: ✅ 通过
   - Skill 版本检查: ✅ 通过
   - 迭代日志检查: ✅ 通过
======================================================================
```

```bash
# 示例 2: 验证指定 change-id
python scripts/openspec-validate/openspec_validate_v2.py \
  --change-id check-langgraph-backend \
  --quality-gate

# 输出示例
======================================================================
OpenSpec Validate Tool v2.0 - 质量门禁自动化验证结果
======================================================================

总检查项: 18
  ✅ 通过: 16
  ❌ 不通过: 0
  ⚠️ 警告: 2
  ℹ️ 信息: 0

【按阶段统计】
  Step 2: 1/1 通过 (100%)
  Step 4: 1/1 通过 (100%)
  Step 6: 1/1 通过 (100%)
  Step 7: 1/1 通过 (100%)
  Step 8: 1/1 通过 (100%)
  通用: 11/14 通过 (79%)

check-langgraph-backend 深度检查结果:
  ✅ 评审记录: 发现 2 条评审记录
  ✅ 评审修复循环: 发现 2 条重新评审/修复记录
  ✅ 验收记录: 发现 1 条验收记录
  ✅ 归档记录: 发现归档记录
======================================================================
```

```bash
# 示例 3: 严格模式（CI/CD 推荐）
python scripts/openspec-validate/openspec_validate_v2.py --quality-gate --strict

# 退出码: 0 (通过) / 1 (失败项) / 2 (严格模式警告)
```

```bash
# 示例 4: JSON 输出（便于自动化处理）
python scripts/openspec-validate/openspec_validate_v2.py --quality-gate --json

# 输出示例
[
  {
    "status": "✅ 通过",
    "check_item": "质量门禁检查清单可用性",
    "stage": "通用",
    "detail": "preference-quality-gate-checklist.md 存在",
    "suggestion": null,
    "auto_fixable": false
  },
  {
    "status": "⚠️ 警告",
    "check_item": "术语定义漂移风险",
    "stage": "通用",
    "detail": "发现可能的术语定义漂移表达",
    "suggestion": "使用精确术语：归档=合并 specs/ + 移动 changes/",
    "auto_fixable": false
  }
]
```

### v2.0 退出码

| 退出码 | 含义 | 使用场景 |
|-------|------|---------|
| 0 | 验证通过 | 无失败项，严格模式下无警告 |
| 1 | 验证未通过 | 存在失败项（必须修复） |
| 2 | 严格模式警告 | 存在警告项（建议修复） |

### 使用场景推荐

| 场景 | 推荐命令 | 说明 |
|-----|---------|------|
| **日常开发** | `python openspec_validate_v2.py` | 快速验证质量门禁 |
| **提交前检查** | `python openspec_validate_v2.py --strict` | 严格模式，确保无警告 |
| **CI/CD 集成** | `python openspec_validate_v2.py --quality-gate --strict --json` | 自动化验证 |
| **变更归档前** | `python openspec_validate_v2.py --change-id [id] --quality-gate` | 深度验证 change-id |
| **问题排查** | `python openspec_validate_v2.py --quality-gate --change-id [id]` | 检查评审/验收/归档完整性 |

## CI/CD 集成（v1.0 + v2.0）

### GitHub Actions 示例

```yaml
# 基础验证（v1.0）
- name: Validate OpenSpec Structure
  run: |
    python scripts/openspec-validate/openspec_validate.py --strict

# 质量门禁验证（v2.0 推荐）
- name: Validate Quality Gates
  run: |
    python scripts/openspec-validate/openspec_validate_v2.py --quality-gate --strict

# 指定变更验证
- name: Validate Change
  if: github.event.inputs.change-id
  run: |
    python scripts/openspec-validate/openspec_validate_v2.py \
      --change-id ${{ github.event.inputs.change-id }} \
      --quality-gate --strict
```

### GitLab CI 示例

```yaml
validate_openspec:
  script:
    - python scripts/openspec-validate/openspec_validate_v2.py --quality-gate --strict
  allow_failure: false
```

## 关联文档

- OpenSpec.md: OpenSpec 开发规范
- preference-quality-gate-checklist: 8+1 质量门禁检查清单
- preference-archive-operation-checklist: 归档操作检查清单

## 版本历史

| 版本 | 日期 | 更新内容 |
|-----|------|---------|
| v1.0 | 2026-03-17 | 初始版本，支持基本目录结构验证、change-id 验证、JSON 输出 |
| v2.0 | 2026-03-17 | 质量门禁自动化验证，新增：质量门禁检查清单验证、术语使用检查、Skill 版本一致性检查、迭代日志格式验证、指定 change-id 深度检查、阶段统计、自动修复建议 |

## 工具选择指南

| 需求 | 推荐工具 | 说明 |
|-----|---------|------|
| 快速目录结构检查 | v1.0 | 轻量级，速度快 |
| 质量门禁自动化验证 | **v2.0** | **推荐**，覆盖 8+1 闭环质量门禁 |
| CI/CD 集成 | v2.0 | 支持 JSON 输出和严格模式 |
| 深度 change-id 验证 | v2.0 | 检查评审/验收/归档完整流程 |
| 术语使用规范性检查 | v2.0 | 检测术语定义漂移 |

## 关联文档

- **OpenSpec.md**: OpenSpec 开发规范
- **preference-quality-gate-checklist**: 8+1 质量门禁检查清单
- **preference-archive-operation-checklist**: 归档操作检查清单
- **preference-terminology-glossary**: OpenSpec 规范术语表
- **anti-pattern-terminology-drift**: 术语定义漂移反模式
- **pattern-complete-quality-closed-loop**: 完整质量闭环流程

## 维护者

ai-agent-dev-system 架构组

## 反馈与改进

如有问题或改进建议，请：
1. 查阅关联文档确认是否为已知问题
2. 在迭代日志中记录发现的问题
3. 必要时启动复盘分析流程
