import { LayoutGrid } from "lucide-react";

function Logo({ size = "md" }) {
  const sizes = {
    sm: {
      icon: 18,
      iconPadding: "p-2",
      text: "text-xl",
    },
    md: {
      icon: 22,
      iconPadding: "p-2.5",
      text: "text-2xl",
    },
    lg: {
      icon: 28,
      iconPadding: "p-3",
      text: "text-3xl",
    },
  };

  const currentSize = sizes[size];

  return (
    <div className="flex items-center justify-center gap-3">
      <div
        className={`rounded-xl bg-blue-600 text-white ${currentSize.iconPadding}`}
      >
        <LayoutGrid size={currentSize.icon} strokeWidth={2.5} />
      </div>

      <h1 className={`${currentSize.text} font-bold tracking-tight`}>
        <span className="text-blue-600">Flow</span>
        <span className="text-slate-900">Board</span>
      </h1>
    </div>
  );
}

export default Logo;