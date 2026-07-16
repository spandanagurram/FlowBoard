function Card({ children, className = "" }) {
  return (
    <div
      className={`
        w-full
        max-w-md
        rounded-2xl
        bg-white
        p-8
        shadow-lg
        ${className}
      `}
    >
      {children}
    </div>
  );
}

export default Card;