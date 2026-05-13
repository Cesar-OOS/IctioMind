function KpiCard({ title, value, subtitle, icon, tone = "blue" }) {
  const tones = {
    blue: {
      bg: "#eff6ff",
      color: "#1b396a",
      border: "#bfdbfe",
    },
    green: {
      bg: "#ecfdf5",
      color: "#15803d",
      border: "#bbf7d0",
    },
    red: {
      bg: "#fef2f2",
      color: "#b91c1c",
      border: "#fecaca",
    },
    yellow: {
      bg: "#fefce8",
      color: "#a16207",
      border: "#fde68a",
    },
  };

  return (
    <div
      style={{
        background: "white",
        border: `1px solid ${tones[tone].border}`,
        borderRadius: "18px",
        padding: "20px",
        boxShadow: "0 12px 28px rgba(15, 23, 42, 0.08)",
      }}
    >
      <div
        style={{
          width: "44px",
          height: "44px",
          borderRadius: "14px",
          background: tones[tone].bg,
          color: tones[tone].color,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "22px",
          marginBottom: "14px",
        }}
      >
        {icon}
      </div>

      <p
        style={{
          margin: 0,
          color: "#6b7280",
          fontSize: "14px",
          fontWeight: "600",
        }}
      >
        {title}
      </p>

      <h3
        style={{
          margin: "6px 0",
          fontSize: "30px",
          color: "#111827",
        }}
      >
        {value}
      </h3>

      <small style={{ color: "#6b7280" }}>{subtitle}</small>
    </div>
  );
}

export default KpiCard;