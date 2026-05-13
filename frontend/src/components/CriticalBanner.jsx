import { Link } from "react-router-dom";

function CriticalBanner({ pond }) {
  if (!pond) return null;

  return (
    <div className="critical-banner">
      <div>
        <strong>⚠ Alerta crítica</strong>
        <span>
          {pond.nombre}: Oxígeno disminuyendo rápidamente. Riesgo IA: {pond.riesgo}%
        </span>
      </div>

      <Link to={`/estanque/${pond.id}`}>Ver estanque</Link>
    </div>
  );
}

export default CriticalBanner;