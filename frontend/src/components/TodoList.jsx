import TodoItem from "./TodoItem";

export default function TodoList({ todos, onToggle, onDelete, onEdit }) {
  if (todos.length === 0) {
    return (
      <p className="text-center text-stone-400 text-sm mt-6">
        No todos yet! Add your first task above.
      </p>
    );
  }

  return (
    <ul className="mt-2 space-y-2 pr-2">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
          onEdit={onEdit}
        />
      ))}
    </ul>
  );
}
