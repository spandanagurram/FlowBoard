import { useEffect, useState } from "react";

import Button from "../../../components/ui/Button";
import Input from "../../../components/ui/Input";

function CreateProjectModal({
  isOpen,
  onClose,
  onSubmit,
  initialValues = {
    name: "",
    key: "",
    description: "",
  },
  title = "Create Project",
  submitText = "Create",
  showKey = true,
}) {
  const [values, setValues] = useState(initialValues);

  useEffect(() => {
    setValues(initialValues);
  }, [initialValues.name, initialValues.key, initialValues.description]);

  const handleChange = (event) => {
    setValues((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(values);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-xl bg-white p-6">

        <h2 className="mb-6 text-2xl font-bold">
          {title}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-5">

          <Input
            label="Project Name"
            name="name"
            value={values.name}
            onChange={handleChange}
            required
          />

          {showKey && (
            <Input
              label="Project Key"
              name="key"
              value={values.key}
              onChange={handleChange}
              required
            />
          )}

          <Input
            label="Description"
            name="description"
            value={values.description}
            onChange={handleChange}
          />

          <div className="flex justify-end gap-3">

            <Button
              type="button"
              variant="secondary"
              className="w-auto"
              onClick={onClose}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              className="w-auto"
            >
              {submitText}
            </Button>

          </div>

        </form>

      </div>
    </div>
  );
}

export default CreateProjectModal;