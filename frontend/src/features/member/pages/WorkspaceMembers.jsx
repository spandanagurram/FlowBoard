import { useEffect, useState } from "react";
import {
  ArrowLeft,
  UserPlus,
} from "lucide-react";
import {
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";

import DashboardLayout from "../../../layouts/DashboardLayout";
import Button from "../../../components/ui/Button";
import MemberList from "../components/MemberList";
import PendingInvitationList from "../components/PendingInvitationList";
import { getWorkspaceMembers, changeMemberRole, transferOwnership } from "../../../api/member";
import { getErrorMessage } from "../../../utils/error";
import InviteMemberModal from "../components/InviteMemberModal";
import {
  createInvitation,
  getPendingInvitations,
  revokeInvitation,
} from "../../../api/invitation";
import ChangeRoleModal from "../components/ChangeRoleModal";
import TransferOwnershipModal from "../components/TransferOwnershipModal";

function WorkspaceMembers() {
  const navigate = useNavigate();
  const location = useLocation();
  const { workspaceId } = useParams();
  const [currentUserId] = useState(
    () => JSON.parse(localStorage.getItem("user"))?.id
  );

  const workspaceName =
    location.state?.workspaceName || "Workspace";

  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pendingInvitations, setPendingInvitations] = useState([]);
  const [pendingInvitationsLoading, setPendingInvitationsLoading] = useState(true);
  const [currentUserRole, setCurrentUserRole] = useState("");
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [selectedTransferMember, setSelectedTransferMember] = useState(null);

  useEffect(() => {
    fetchMembers();
    fetchPendingInvitations();
  }, [workspaceId]);

  const fetchMembers = async () => {
    try {
      setLoading(true);

      const data = await getWorkspaceMembers(workspaceId);
      setCurrentUserRole(data.current_user_role);
      setMembers(data.members);

    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (values) => {
    try {
      await createInvitation(workspaceId, values);

      alert("Invitation sent successfully.");

      await fetchPendingInvitations();
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
      throw error;
    }
  };

  async function fetchPendingInvitations() {
    try {
      setPendingInvitationsLoading(true);

      const data = await getPendingInvitations(workspaceId);
      setPendingInvitations(data);
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    } finally {
      setPendingInvitationsLoading(false);
    }
  }

  const handleRevokeInvitation = async (invitationId) => {
    try {
      await revokeInvitation(invitationId);

      alert("Invitation revoked successfully.");

      await fetchPendingInvitations();
    } catch (error) {
      console.error(error);
      alert(getErrorMessage(error));
    }
  };

  const openRoleModal = (member) => {
  setSelectedMember(member);
  setShowRoleModal(true);
  };

  const closeRoleModal = () => {
    setSelectedMember(null);
    setShowRoleModal(false);
  };

  const handleRoleUpdate = async (
    userId,
    role
  ) => {
    try {
      await changeMemberRole(
        workspaceId,
        userId,
        { role }
      );

      alert("Role updated successfully.");

      await fetchMembers();

    } catch (error) {
      alert(getErrorMessage(error));
    }
  };

  const openTransferModal = (member) => {
    setSelectedTransferMember(member);
    setShowTransferModal(true);
  };

  const closeTransferModal = () => {
    setSelectedTransferMember(null);
    setShowTransferModal(false);
  };

  const handleTransferOwnership = async (
    userId
  ) => {
    try {
      await transferOwnership(
        workspaceId,
        {
          user_id: userId,
        }
      );

      alert(
        "Workspace ownership transferred successfully."
      );

      await fetchMembers();

    } catch (error) {
      alert(getErrorMessage(error));
      throw error;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <Button
          className="w-auto flex items-center gap-2"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft size={18} />
          Back
        </Button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">
              {workspaceName}
            </h1>

            <p className="text-slate-500 mt-1">
              Members
            </p>
          </div>

          {(currentUserRole === "OWNER" ||
            currentUserRole === "ADMIN") && (
            <Button
              className="w-auto flex items-center gap-2"
              onClick={() => setShowInviteModal(true)}
            >
              <UserPlus size={18} />
              Invite Member
            </Button>
          )}
        </div>

        {loading ? (
          <p>Loading members...</p>
        ) : (
          <MemberList members={members} 
            currentUserRole={currentUserRole}
            onRemove={fetchMembers}
            onChangeRole={openRoleModal}
            onTransferOwnership={openTransferModal}
         />
        )}

        <div>
          <h2 className="text-xl font-semibold mb-4">
            Pending Invitations
          </h2>

          {pendingInvitationsLoading ? (
            <p>Loading pending invitations...</p>
          ) : (
            <PendingInvitationList
              invitations={pendingInvitations}
              currentUserRole={currentUserRole}
              currentUserId={currentUserId}
              onRevoke={handleRevokeInvitation}
            />
          )}
        </div>
      </div>
      <InviteMemberModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        onInvite={handleInvite}
        currentUserRole={currentUserRole}
      />
      <ChangeRoleModal
        isOpen={showRoleModal}
        onClose={closeRoleModal}
        member={selectedMember}
        currentUserRole={currentUserRole}
        onUpdate={handleRoleUpdate}
      />
      <TransferOwnershipModal
        isOpen={showTransferModal}
        onClose={closeTransferModal}
        member={selectedTransferMember}
        onTransfer={handleTransferOwnership}
      />
    </DashboardLayout>
  );
}

export default WorkspaceMembers;
