import { useEffect, useState } from "react";

export default function TodoCreateModal({
  open,
  onClose,
  onCreate,
  onEdit,
  editingTodo,
}) {
  const [errors, setErrors] = useState({});
  const [deadline, setDeadline] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    if (!open) {
      setDescription("");
      setDeadline("");
      setErrors({});
      return;
    }

    if (editingTodo) {
      setDescription(editingTodo.description || "");
      // Convert server ISO (UTC) into a local `datetime-local` input value
      if (editingTodo.deadline) {
        const dt = new Date(editingTodo.deadline);
        const y = dt.getFullYear();
        const m = String(dt.getMonth() + 1).padStart(2, "0");
        const d = String(dt.getDate()).padStart(2, "0");
        const hh = String(dt.getHours()).padStart(2, "0");
        const mm = String(dt.getMinutes()).padStart(2, "0");
        setDeadline(`${y}-${m}-${d}T${hh}:${mm}`);
      } else {
        setDeadline("");
      }
    } else {
      setDescription("");
      setDeadline("");
    }
  }, [editingTodo, open]);

  if (!open) return null;

  const isEditing = Boolean(editingTodo);
  const isReadOnly = editingTodo?.is_overdue;

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (isReadOnly) {
      return;
    }

    const newErrors = {};

    if (!description.trim()) {
      newErrors.description = "Description is required";
    }

    if (!deadline) {
      newErrors.deadline = "Deadline is required";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      setErrors({});

      const todoData = {
        // Convert local datetime-local value to UTC ISO so backend treats
        // the deadline as the correct instant in time.
        deadline: new Date(deadline).toISOString(),
        description,
        completion: editingTodo ? editingTodo.completion : false,
      };

      if (editingTodo) {
        await onEdit(editingTodo.id, todoData);
      } else {
        await onCreate(todoData);
      }

      setDescription("");
      setDeadline("");

      onClose();
    } catch (error) {
      setErrors(error.response?.data || {});
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-lg">
        <h2 className="text-lg font-semibold mb-4">
          {isEditing ? (isReadOnly ? "View Todo" : "Edit Todo") : "Create Todo"}
        </h2>

        {isReadOnly && (
          <p className="text-sm text-red-600 mb-4">
            This todo is overdue. Editing is disabled, but you can still delete
            it from the list.
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label>Description</label>

            <textarea
              value={description}
              onChange={(e) => {
                if (!isReadOnly) {
                  setDescription(e.target.value);
                }

                if (errors.description) {
                  setErrors({ ...errors, description: null });
                }
              }}
              disabled={isReadOnly}
              className={`w-full border rounded p-2 ${
                errors.description ? "border-red-500" : ""
              } ${isReadOnly ? "bg-stone-100" : ""}`}
            />

            {errors.description && (
              <p className="text-red-500 text-sm mt-1">
                {Array.isArray(errors.description)
                  ? errors.description[0]
                  : errors.description}
              </p>
            )}
          </div>
          <div>
            <label>Deadline</label>

            <input
              type="datetime-local"
              value={deadline}
              onChange={(e) => {
                if (!isReadOnly) {
                  setDeadline(e.target.value);
                }

                if (errors.deadline) {
                  setErrors({ ...errors, deadline: null });
                }
              }}
              disabled={isReadOnly}
              className={`w-full border rounded p-2 ${
                errors.deadline ? "border-red-500" : ""
              } ${isReadOnly ? "bg-stone-100" : ""}`}
            />

            {errors.deadline && (
              <p className="text-red-500 text-sm mt-1">
                {Array.isArray(errors.deadline)
                  ? errors.deadline[0]
                  : errors.deadline}
              </p>
            )}
          </div>

          <div className="flex justify-end gap-2">
            <button type="button" onClick={onClose}>
              Close
            </button>

            <button
              type="submit"
              disabled={isReadOnly}
              className={`bg-stone-900 text-white px-4 py-2 rounded ${
                isReadOnly ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {isReadOnly ? "View only" : isEditing ? "Save" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
