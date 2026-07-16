import { FcGoogle } from "react-icons/fc";
import Button from "../../../components/ui/Button";

function GoogleButton({ onClick }) {
  return (
    <Button
      variant="secondary"
      type="button"
      onClick={onClick}
      className="gap-3"
    >
      <FcGoogle size={22} />
      <span>Continue with Google</span>
    </Button>
  );
}

export default GoogleButton;