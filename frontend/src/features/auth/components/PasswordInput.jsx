import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

import Input from "../../../components/ui/Input";

function PasswordInput(props) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <Input
      {...props}
      type={showPassword ? "text" : "password"}
      rightIcon={
        showPassword ? (
          <EyeOff size={20} />
        ) : (
          <Eye size={20} />
        )
      }
      onRightIconClick={() =>
        setShowPassword((current) => !current)
      }
    />
  );
}

export default PasswordInput;