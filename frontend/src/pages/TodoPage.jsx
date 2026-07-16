import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { isAuthenticated } from "../services/authService";
import {
  getTodos,
  createTodo,
  updateTodo,
  deleteTodo as deleteTodoAPI,
} from "../services/todoService";

import TodoForm from "../components/TodoForm";
import TodoList from "../components/TodoList";
import BeltProgress from "../components/BeltProgress";
import TodoCreateModel from "../components/TodoCreateModel";
import Navbar from "../components/Navbar";

export default function TodoPage() {
  const [todos, setTodos] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingTodo, setEditingTodo] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    const id = setInterval(() => {
      if (!isAuthenticated()) navigate("/login");
    }, 5000);

    return () => clearInterval(id);
  }, [navigate]);

  useEffect(() => {
    fetchTodos();
  }, []);

  function sortTodos(todos) {
    return [...todos].sort((a, b) => {
      const overdueA = !!a.is_overdue;
      const overdueB = !!b.is_overdue;

      if (overdueA !== overdueB) {
        return overdueA ? 1 : -1;
      }

      if (!a.deadline || !b.deadline) {
        return 0;
      }

      return new Date(a.deadline) - new Date(b.deadline);
    });
  }

  async function fetchTodos() {
    try {
      const response = await getTodos();
      setTodos(sortTodos(response.data));
    } catch (error) {
      console.error("Failed to load todos:", error);
    }
  }
  async function addTodo(todoData) {
    try {
      const response = await createTodo(todoData);

      setTodos((prev) => sortTodos([...prev, response.data]));
    } catch (error) {
      console.log(error.response?.data);
    }
  }
  async function toggleTodo(todo) {
    try {
      const updatedTodo = {
        ...todo,
        completion: !todo.completion,
      };

      const response = await updateTodo(todo.id, updatedTodo);

      setTodos((prev) =>
        sortTodos(prev.map((t) => (t.id === todo.id ? response.data : t))),
      );
    } catch (error) {
      console.error("Failed to update todo:", error);
    }
  }

  async function deleteTodo(id) {
    try {
      await deleteTodoAPI(id);

      setTodos((prev) => sortTodos(prev.filter((todo) => todo.id !== id)));
    } catch (error) {
      console.error("Failed to delete todo:", error);
    }
  }

  async function editTodo(id, todoData) {
    try {
      const response = await updateTodo(id, todoData);

      setTodos((prev) =>
        sortTodos(prev.map((todo) => (todo.id === id ? response.data : todo))),
      );

      setEditingTodo(null);
      setShowModal(false);
    } catch (error) {
      console.error("Failed to edit todo:", error);
    }
  }

  const completedCount = todos.filter((t) => t.completion).length;

  return (
    <div className="h-screen bg-stone-100 flex justify-center px-4 py-4 overflow-hidden">
      <div className="w-full max-w-md flex flex-col">
        <div className="mb-2">
          <Navbar />
        </div>

        <div className="bg-white rounded-2xl border border-stone-200 shadow-sm p-4 flex-1 flex flex-col overflow-hidden">
          <h1 className="text-base font-semibold text-stone-900 mb-1">
            Today's Todos
          </h1>
          <p className="text-xs text-stone-500 mb-3">
            Finish and clear your tasks after completion to track progress
            automatically.
          </p>

          <BeltProgress completed={completedCount} total={todos.length} />

          <TodoForm
            onAdd={() => {
              setEditingTodo(null);
              setShowModal(true);
            }}
          />

          <div className="flex-1 overflow-y-auto">
            <TodoList
              todos={todos}
              onToggle={toggleTodo}
              onDelete={deleteTodo}
              onEdit={(todo) => {
                setEditingTodo(todo);
                setShowModal(true);
              }}
            />
          </div>
          <TodoCreateModel
            open={showModal}
            onClose={() => {
              setShowModal(false);
              setEditingTodo(null);
            }}
            onCreate={addTodo}
            onEdit={editTodo}
            editingTodo={editingTodo}
          />
        </div>

        <p className="text-center text-xs text-stone-400 mt-2">
          Dojo Hub (SMC) Ltd · Software Starter Course
        </p>
      </div>
    </div>
  );
}
