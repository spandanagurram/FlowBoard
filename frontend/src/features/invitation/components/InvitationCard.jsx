import Button from "../../../components/ui/Button";

function InvitationCard({
  invitation,
  loading,
  onAccept,
  onReject,
}) {
  const formatDate = (date) =>
    new Date(date).toLocaleDateString();

  const renderContent = () => {
    switch (invitation.status) {
      case "PENDING":
        return (
          <>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-slate-500">
                  Workspace
                </p>

                <p className="font-medium">
                  {invitation.workspace_name}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Invited Email
                </p>

                <p className="font-medium">
                  {invitation.email}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Role
                </p>

                <p className="font-medium">
                  {invitation.role}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Expires
                </p>

                <p className="font-medium">
                  {formatDate(invitation.expires_at)}
                </p>
              </div>
            </div>

            <div className="mt-8 flex justify-end gap-3">
              <Button
                className="w-auto"
                onClick={onReject}
                disabled={loading}
              >
                Reject
              </Button>

              <Button
                className="w-auto"
                onClick={onAccept}
                disabled={loading}
              >
                {loading
                  ? "Please wait..."
                  : "Accept"}
              </Button>
            </div>
          </>
        );

      case "ACCEPTED":
        return (
          <p className="text-green-600 font-medium">
            This invitation has already been accepted.
          </p>
        );

      case "REJECTED":
        return (
          <p className="text-red-600 font-medium">
            This invitation has already been rejected.
          </p>
        );

      case "REVOKED":
        return (
          <p className="text-red-600 font-medium">
            This invitation has been revoked.
          </p>
        );

      case "EXPIRED":
        return (
          <p className="text-orange-600 font-medium">
            This invitation has expired.
          </p>
        );

      default:
        return (
          <p>Invalid invitation.</p>
        );
    }
  };

  return (
    <div className="mx-auto mt-20 w-full max-w-lg rounded-lg border border-slate-200 bg-white p-8 shadow">
      <h1 className="text-3xl font-bold">
        FlowBoard
      </h1>

      <p className="mt-2 text-slate-500">
        Workspace Invitation
      </p>

      <div className="mt-8">
        {renderContent()}
      </div>
    </div>
  );
}

export default InvitationCard;