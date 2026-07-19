import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import InvitationCard from "../components/InvitationCard";
import {
  acceptInvitation,
  getInvitation,
  rejectInvitation,
} from "../../../api/invitation";
import { getErrorMessage } from "../../../utils/error";

function InvitationPage() {
  const { token } = useParams();

  const navigate = useNavigate();

  const [invitation, setInvitation] = useState(null);

  const [loading, setLoading] = useState(true);

  const [actionLoading, setActionLoading] = useState(false);

  const fetchInvitation = async () => {
    try {
      const data = await getInvitation(token);

      setInvitation(data);
    } catch (error) {
      alert(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvitation();
  }, [token]);

  const ensureLoggedIn = () => {
    const accessToken = localStorage.getItem("access");
    console.log("accessToken =", accessToken);

    if (accessToken) {
      return true;
    }
    console.log("redirecting to login page with redirectTo =", `/invitations/${token}`);

    navigate("/login", {
      state: {
        redirectTo: `/invitations/${token}`,
      },
    });

    return false;
  };

  const handleAccept = async () => {
    if (!ensureLoggedIn()) {
      return;
    }

    try {
      setActionLoading(true);

      await acceptInvitation(token);

      alert("Invitation accepted.");

      navigate("/dashboard");
    } catch (error) {
      alert(getErrorMessage(error));

      fetchInvitation();
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!ensureLoggedIn()) {
      return;
    }

    try {
      setActionLoading(true);

      await rejectInvitation(token);

      alert("Invitation rejected.");

      fetchInvitation();
    } catch (error) {
      alert(getErrorMessage(error));

      fetchInvitation();
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center">
        Loading invitation...
      </div>
    );
  }

  if (!invitation) {
    return (
      <div className="p-8 text-center">
        Invitation not found.
      </div>
    );
  }

  return (
    <InvitationCard
      invitation={invitation}
      loading={actionLoading}
      onAccept={handleAccept}
      onReject={handleReject}
    />
  );
}

export default InvitationPage;