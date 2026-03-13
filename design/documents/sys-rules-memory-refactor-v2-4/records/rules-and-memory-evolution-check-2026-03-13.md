## sys-rules-memory-refactor-v2-4：rules × memory 协同演进自检记录（2026-03-13）

### 1. 本次变更范围

- 更新 `global-rules/projects-rules-for-agent.md` 第九章，增加一条「规则与记忆的演进约束」条款（HOW 一律先下沉 SKILL/memory，只在 rules 中保留结论级 HOW + 索引）；  
- 新增 memory pattern：`memory/patterns/pattern-rules-and-memory-evolution-governance.md`，系统化描述规则与记忆协同演进模式；  
- 在 V2.4.2 方案文档中追加「第六节评估 + 第七节必做治理任务清单」，并将 adapter/backend 文档更新列为必做项。

### 2. 自检：是否先走完 SKILL/memory → rules 流程？

1. **这次改动是否引入新的红线/必须动作/时机？**  
   - 是：在第九章新增了「规则与记忆的演进约束」这一治理红线，用于约束未来 HOW 类内容的归属。  

2. **新增内容是结论级 HOW 还是过程级 HOW？**  
   - 结论级 HOW：  
     - 第九章新增条款仅声明「HOW 优先下沉 SKILL/memory，rules 只保结论级 HOW + 索引」，属于治理级约束，而非具体执行步骤。  
     - 具体「如何执行自检」「如何在 records 中记录」「如何在 adapter/backend 中接线」的步骤，全部写入本 records 与新的 memory pattern 中。  

3. **对应 SKILL / memory 是否已存在或已补齐？**  
   - 已补齐：  
     - 新建 `memory/patterns/pattern-rules-and-memory-evolution-governance.md`，详细描述：  
       - rules 的职责与记忆职责；  
       - 改 rules 前的 checklist；  
       - 如何在 design/records 和迭代日志中留痕；  
       - 与宿主 adapter / backend 的关系。  

4. **rules 中是否只保留结论级 HOW，并写明索引？**  
   - 是：  
     - 第九章新增条款只保结论级约束，不包含任何长篇步骤或案例；  
     - 细节 HOW（演进模式与自检流程）在 memory pattern 与本 records 中说明。

### 3. 对宿主 adapter / backend 的影响

- Cursor / VS Code / generic adapter 与 `agent_team_project/` 的 README 已存在并描述了各自职责与模型策略；  
- V2.4.2 方案第 6.3 与第 7 节已将「加载顺序规范（simple 首轮轻量、heavy 加载 rules+SKILL+少量 memory）」和「在 adapter/backend 文档中显式说明」标为必做任务，供后续 adapter 文档演进时执行。

### 4. 结论

- 本轮对 rules 的改动已按「先 SKILL/memory、后 rules」的模式执行，并在 design/records 中留下自检记录；  
- 后续在对 `projects-rules-for-agent.md` 做任何 HOW 相关修改时，应复用本记录与 `pattern-rules-and-memory-evolution-governance.md` 中的 checklist 做自检。

