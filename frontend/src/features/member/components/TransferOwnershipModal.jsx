import Button from "../../../components/ui/Button";

function TransferOwnershipModal({
  isOpen,
  onClose,
  member,
  onTransfer,
}) {
  if (!isOpen || !member) {
    return null;
  }

  const handleSubmit = async () => {
    try {
        await onTransfer(member.user_id);
        onClose();
    } catch (error) {
        // Keep the modal open if the transfer fails.
    }
 };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">

        <h2 className="text-xl font-semibold">
          Transfer Workspace Ownership
        </h2>

        <div className="mt-5 space-y-3">

          <p>
            You are transferring ownership to
          </p>

          <div className="rounded-md border border-slate-200 p-3">

            <p className="font-semibold">
              {member.username}
            </p>

            <p className="text-sm text-slate-500">
              {member.email}
            </p>

          </div>

          <div className="rounded-md bg-yellow-50 border border-yellow-300 p-3 text-sm space-y-2">

            <p>
              • This member will become the new Owner.
            </p>

            <p>
              • You will become an Admin.
            </p>

            <p className="font-medium text-red-600">
              This action should only be performed if you intend to permanently transfer ownership.
            </p>

          </div>

        </div>

        <div className="mt-6 flex justify-end gap-3">

          <Button
            className="w-auto"
            onClick={onClose}
          >
            Cancel
          </Button>

          <Button
            className="w-auto"
            onClick={handleSubmit}
          >
            👑 Transfer Ownership
          </Button>

        </div>

      </div>
    </div>
  );
}

export default TransferOwnershipModal;