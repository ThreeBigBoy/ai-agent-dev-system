/**
 * 人工确认弹窗组件 (P1-A6)
 * 支持 approve / reject / comment，与 MCP human_confirm_submit 及后端 /confirm/submit 对齐。
 * 使用方式：<ConfirmPanel {...props} onClose={...} onSubmit={...} />
 */
import React, { useState } from "react";

export interface ConfirmPanelProps {
  /** 待确认项 ID（与 request_id 一致） */
  requestId: string;
  /** 变更 ID */
  changeId: string;
  /** 步骤名，如 step4.5_design / step7.5_acceptance */
  stepName: string;
  /** 简要说明 */
  contextSummary: string;
  /** 待确认产出物路径列表 */
  artifacts?: string[];
  /** 关闭弹窗（不提交） */
  onClose: () => void;
  /** 提交结果：decision, comment?, reviewer? */
  onSubmit: (payload: { decision: "approve" | "reject" | "comment"; comment?: string; reviewer?: string }) => void;
  /** 可选：默认 reviewer 显示名 */
  defaultReviewer?: string;
}

export const ConfirmPanel: React.FC<ConfirmPanelProps> = ({
  requestId,
  changeId,
  stepName,
  contextSummary,
  artifacts = [],
  onClose,
  onSubmit,
  defaultReviewer = "",
}) => {
  const [decision, setDecision] = useState<"approve" | "reject" | "comment">("approve");
  const [comment, setComment] = useState("");
  const [reviewer, setReviewer] = useState(defaultReviewer);

  const handleSubmit = () => {
    onSubmit({
      decision,
      comment: comment.trim() || undefined,
      reviewer: reviewer.trim() || undefined,
    });
    onClose();
  };

  return (
    <div className="confirm-panel-overlay" role="dialog" aria-labelledby="confirm-panel-title">
      <div className="confirm-panel">
        <h2 id="confirm-panel-title">人工确认 · {stepName}</h2>
        <p className="confirm-panel-change">变更: {changeId}</p>
        <p className="confirm-panel-summary">{contextSummary}</p>
        {artifacts.length > 0 && (
          <ul className="confirm-panel-artifacts">
            {artifacts.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        )}
        <div className="confirm-panel-actions">
          <label>
            <input
              type="radio"
              name="decision"
              checked={decision === "approve"}
              onChange={() => setDecision("approve")}
            />
            通过 (approve)
          </label>
          <label>
            <input
              type="radio"
              name="decision"
              checked={decision === "reject"}
              onChange={() => setDecision("reject")}
            />
            驳回 (reject)
          </label>
          <label>
            <input
              type="radio"
              name="decision"
              checked={decision === "comment"}
              onChange={() => setDecision("comment")}
            />
            仅评论 (comment)
          </label>
        </div>
        <div className="confirm-panel-field">
          <label>备注 (可选)</label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            placeholder="填写备注或修改意见"
          />
        </div>
        <div className="confirm-panel-field">
          <label>确认人</label>
          <input
            type="text"
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
            placeholder="姓名或 ID"
          />
        </div>
        <div className="confirm-panel-buttons">
          <button type="button" onClick={onClose}>
            取消
          </button>
          <button type="button" onClick={handleSubmit} className="primary">
            提交
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmPanel;
