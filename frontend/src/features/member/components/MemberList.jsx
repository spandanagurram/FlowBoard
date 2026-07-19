import MemberCard from "./MemberCard";

function MemberList({
  members,
  currentUserRole,
  onRemove,
  onChangeRole,
  onTransferOwnership,
}) {
  if (!members.length) {
    return (
      <p className="text-slate-500">
        No members found.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {members.map((member) => (
        <MemberCard
          key={member.id}
          member={member}
          currentUserRole={currentUserRole}
          onRemove={onRemove}
          onChangeRole={onChangeRole}
          onTransferOwnership={onTransferOwnership}
        />
      ))}
    </div>
  );
}

export default MemberList;