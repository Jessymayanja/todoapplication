import api from "../api/axios";

export const getTodos = () => {
  return api.get("/todos/");
};

export const createTodo = (todoData) => {
  return api.post("/todos/create/", todoData);
};

export const updateTodo = (id, todoData) => {
  return api.put(`/todos/${id}/update/`, todoData);
};

export const deleteTodo = (id) => {
  return api.delete(`/todos/${id}/delete/`);
};
