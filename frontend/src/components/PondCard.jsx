import { Link } from "react-router-dom";
import HealthGauge from "./HealthGauge";

function PondCard({ pond }) {
  const status = {
    verde: {
      label: "Estable",
      color: "#22c55e",
      bg: "#ecfdf5",
      border: "#bbf7d0",
      health: 92,
    },
    amarillo: {
      label: "Precaución",
      color: "#f59e0b",
      bg: "#fffbeb",
      border: "#fde68a",
      health: 67,
    },
    rojo: {
      label: "Crítico",
      color: "#ef4444",
      bg: "#fef2f2",
      border: "#fecaca",
      health: 38,
    },
  };

  const current = status[pond.estado];

  const metrics = [
    {
      key: "oxigeno",
      label: "Oxígeno disuelto",
      short: "OD",
      value: pond.oxigeno,
      unit: "mg/L",
      delta: Number(pond.deltas.oxigeno),
      icon: "💨",
      risk:
        Number(pond.deltas.oxigeno) < 0
          ? Math.abs(Number(pond.deltas.oxigeno)) * 4
          : 0,
    },
    {
      key: "temperatura",
      label: "Temperatura",
      short: "Temp.",
      value: pond.temperatura,
      unit: "°C",
      delta: Number(pond.deltas.temperatura),
      icon: "🌡",
      risk: Math.abs(Number(pond.deltas.temperatura)) * 2.5,
    },
    {
      key: "ph",
      label: "pH",
      short: "pH",
      value: pond.ph,
      unit: "",
      delta: Number(pond.deltas.ph),
      icon: "🧪",
      risk: Math.abs(Number(pond.deltas.ph)) * 5,
    },
    {
      key: "dureza",
      label: "Dureza",
      short: "Dureza",
      value: pond.dureza,
      unit: "ppm",
      delta: Number(pond.deltas.dureza),
      icon: "🪨",
      risk: Math.abs(Number(pond.deltas.dureza)) * 0.5,
    },
  ];

  const mainMetric = [...metrics].sort((a, b) => b.risk - a.risk)[0];
  const secondaryMetrics = metrics.filter(
    (metric) => metric.key !== mainMetric.key
  );

  return (
    <Link to={`/estanque/${pond.id}`} className="pond-link">
      <article
          className={`pond-card ${
            pond.estado === "rojo" ? "pond-card-alert" : ""
          }`}
>
        <div className="pond-card-header">
          <div>
            <span className="pond-eyebrow">Unidad multisensor</span>
            <h3>{pond.nombre}</h3>
            <p className="fish-type">{pond.tipo}</p>
          </div>

          <span
            className="status-pill"
            style={{
              color: current.color,
              background: current.bg,
              borderColor: current.border,
            }}
          >
            {current.label}
          </span>
        </div>

        <HealthGauge value={current.health} status={pond.estado} />

        <section className="featured-metric">
          <div>
            <span className="featured-label">
              {pond.estado === "verde"
                ? "Condición principal"
                : "Factor que requiere atención"}
            </span>

            <strong className="featured-name">
              {mainMetric.icon} {mainMetric.label}
            </strong>

            <b className="featured-value">
              {mainMetric.value}
              {mainMetric.unit && ` ${mainMetric.unit}`}
            </b>
          </div>

          <Delta value={mainMetric.delta} />
        </section>

        <section className="compact-metrics">
          {secondaryMetrics.map((metric) => (
            <div className="compact-metric" key={metric.key}>
              <span>{metric.short}</span>
              <strong>
                {metric.value}
                {metric.unit && ` ${metric.unit}`}
              </strong>
              <Delta value={metric.delta} mini />
            </div>
          ))}
        </section>

        {pond.alerta && (
          <div className="alert-chip">⚠ Atención requerida</div>
        )}
      </article>
    </Link>
  );
}

function Delta({ value, mini = false }) {
  const num = Number(value);
  const isDown = num < 0;
  const formatted = num > 0 ? `+${num}` : num;

  return (
    <span className={`delta ${isDown ? "down" : "up"} ${mini ? "mini" : ""}`}>
      {isDown ? "↘" : "↗"} {formatted}
    </span>
  );
}

export default PondCard;