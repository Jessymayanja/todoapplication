export default function TodoForm({ onAdd }) {
  return (
    <div className="flex items-center justify-between mb-6 rounded-lg border border-stone-200 bg-stone-50 px-4 py-3">
      <div>
        <p className="text-sm font-medium text-stone-700">
          It all starts with proper planning?
        </p>
        <p className="text-xs text-stone-500">
          Click the button to create a new todo.
        </p>
      </div>

      <button
        type="button"
        onClick={onAdd}
        className="rounded-lg bg-red-700 px-4 py-2.5 text-sm font-semibold text-white
                   hover:bg-red-800 transition-colors
                   focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-700"
      >
        +
      </button>
    </div>
  );
}
