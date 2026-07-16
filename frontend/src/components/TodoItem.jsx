import { useEffect, useState } from "react";

/**
 * Format a UTC ISO deadline string for display in the user's local timezone.
 * new Date(isoString) correctly parses the "Z" suffix as UTC and converts
 * to local time automatically — no manual stripping needed.
 */
const formatDeadline = (deadline) => {
  if (!deadline) return "";
  const date = new Date(deadline); // ← parse as UTC, display as local
  return date.toLocaleString("en-GB", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

/**
 * Compare the UTC deadline against the current local time.
 * Both new Date(deadline) and new Date() are in the same epoch milliseconds,
 * so the comparison is always correct regardless of timezone.
 */
const computeIsOverdue = (deadline, isComplete) => {
  if (isComplete || !deadline) return false;
  return new Date(deadline) < new Date(); // ← UTC deadline vs local now
};

const getDeadlineStatus = (isComplete, isOverdue) => {
  if (isComplete) return "complete";
  if (isOverdue) return "overdue";
  return "normal";
};

const getStatusColor = (status) => {
  switch (status) {
    case "complete":
      return "border-stone-100 bg-stone-50 text-stone-400";
    case "overdue":
      return "border-red-300 bg-red-50 text-red-600";
    default:
      return "border-stone-100 bg-stone-50 text-stone-700";
  }
};

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENT
// ─────────────────────────────────────────────────────────────────────────────

export default function TodoItem({ todo, onToggle, onDelete, onEdit }) {
  const isComplete = !!todo.completion;

  const [isOverdue, setIsOverdue] = useState(
    computeIsOverdue(todo.deadline, isComplete),
  );

  useEffect(() => {
    setIsOverdue(computeIsOverdue(todo.deadline, isComplete));

    // Re-evaluate every second so the card turns red the moment the
    // deadline passes — without needing a page refresh.
    const interval = setInterval(() => {
      setIsOverdue(computeIsOverdue(todo.deadline, isComplete));
    }, 1000);

    return () => clearInterval(interval);
  }, [todo.deadline, isComplete]);

  const statusType = getDeadlineStatus(isComplete, isOverdue);
  const statusColor = getStatusColor(statusType);

  return (
    <li
      className={`flex items-center gap-3 p-3 rounded-xl border ${statusColor}`}
    >
      <input
        type="checkbox"
        checked={isComplete}
        onChange={() => !isOverdue && onToggle(todo)}
        disabled={isOverdue}
        className={`w-4 h-4 accent-red-600 ${
          isOverdue ? "cursor-not-allowed opacity-50" : "cursor-pointer"
        }`}
      />

      <div className="flex-1">
        <span
          className={`text-sm block ${
            isComplete ? "line-through" : isOverdue ? "font-semibold" : ""
          }`}
        >
          {todo.description}
        </span>

        {todo.deadline && (
          <span className="text-xs block mt-1 opacity-75">
            Due: {formatDeadline(todo.deadline)}
            {isOverdue && " • Overdue!"}
          </span>
        )}
      </div>

      <button
        onClick={() => onDelete(todo.id)}
        className="text-stone-400 hover:text-red-500 text-xs transition-colors"
      >
        ✕
      </button>

      <button
        onClick={() => !isOverdue && onEdit(todo)}
        disabled={isOverdue}
        className={`text-xs transition-colors ${
          isOverdue
            ? "text-stone-400 cursor-not-allowed"
            : "text-blue-500 hover:text-blue-700"
        }`}
      >
        {isOverdue ? "View" : "Edit"}
      </button>
    </li>
  );
}
