function HealthGauge({ value = 80, status = "verde" }) {
  const colors = {
    verde: "#22c55e",
    amarillo: "#f59e0b",
    rojo: "#ef4444",
  };

  const color = colors[status] || colors.verde;
  const clamped = Math.max(0, Math.min(100, value));

  const circumference = 235;
  const progress = (clamped / 100) * circumference;

  return (
    <div className="health-gauge">
      <svg viewBox="0 0 220 130" className="health-gauge-svg">
        <path
          d="M 35 100 A 75 75 0 0 1 185 100"
          className="gauge-track"
        />

        <path
          d="M 35 100 A 75 75 0 0 1 185 100"
          className="gauge-progress"
          stroke={color}
          strokeDasharray={`${progress} ${circumference}`}
        />

        <circle cx="110" cy="100" r="48" className="gauge-inner" />

        <text x="110" y="92" textAnchor="middle" className="gauge-number">
          {clamped}%
        </text>

        <text x="110" y="111" textAnchor="middle" className="gauge-label">
          Salud
        </text>
      </svg>
    </div>
  );
}

export default HealthGauge;