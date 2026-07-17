function TopNavbar() {
  const user = JSON.parse(localStorage.getItem("user"));

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">

      <div>
        <h2 className="text-2xl font-bold text-slate-800">
          Welcome back, {user?.username} 👋
        </h2>

        <p className="text-sm text-slate-500">
          Manage your workspaces and tasks efficiently.
        </p>
      </div>

      <button className="flex items-center gap-3 rounded-lg px-4 py-2 transition hover:bg-slate-100">

        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 font-semibold text-white">
          {user?.username?.charAt(0).toUpperCase()}
        </div>

        <span className="font-medium text-slate-700">
          {user?.username}
        </span>

      </button>

    </header>
  );
}

export default TopNavbar;