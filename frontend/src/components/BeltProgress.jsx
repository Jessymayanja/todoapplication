import { getBeltRank } from "../beltRanks";

export default function BeltProgress({ completed, total }) {
  const percent = total === 0 ? 0 : Math.round((completed / total) * 100);
  const rank = getBeltRank(percent);

  return (
    <div className="mb-7">
      <div className="flex items-end justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-stone-500">
          Belt progress
        </span>
        <span
          className="text-xs font-semibold px-2.5 py-1 rounded-full border"
          style={{
            background: rank.color,
            color: rank.text,
            borderColor: rank.border,
          }}
        >
          {rank.label}
        </span>
      </div>

      <div className="h-3 w-full rounded-full bg-stone-200 overflow-hidden border border-stone-300">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${percent}%`, background: rank.color }}
        />
      </div>

      <p className="mt-2 text-xs text-stone-500">
        {completed} of {total} {total === 1 ? "task" : "tasks"} complete (
        {percent}%)
      </p>
    </div>
  );
}
