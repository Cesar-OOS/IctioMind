import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Thermometer, Droplets, Wind, Activity, CloudRain, Brain, ShieldAlert } from "lucide-react";
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import Header from "../components/Header";

function PondDetail() {
  const { id } = useParams();
  
  // Estados de React para manejar los datos del Backend
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Hook para conectarse a FastAPI al cargar la página
  useEffect(() => {
    const fetchAnalisis = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/v1/analisis-integral/${id}`);
        const result = await response.json();
        
        // Si el backend responde que faltan lecturas (status "info"), lo manejamos
        if (result.status === "info") {
          console.warn(result.mensaje);
        } else {
          setData(result);
        }
      } catch (error) {
        console.error("Error conectando al backend:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalisis();
  }, [id]);

  if (loading) {
    return (
      <><Header /><main className="detail-page"><h2 style={{textAlign: "center", marginTop: "50px"}}>Cargando Cerebro Predictivo... 🧠</h2></main></>
    );
  }

  if (!data) {
    return (
      <><Header /><main className="detail-page"><Link to="/" className="back-link"><ArrowLeft size={18} /> Volver</Link><h2>No hay suficientes datos históricos para este estanque.</h2></main></>
    );
  }

  // --- MAPEO DE DATOS DE LA IA AL FRONTEND ---
  const { diagnostico_ia, meteorologia, predicciones_futuras } = data;
  
  // Diccionario de colores (mantenemos el diseño de tu equipo)
  const statusColors = {
    verde: { color: "#22c55e", bg: "#ecfdf5", border: "#bbf7d0" },
    amarillo: { color: "#f59e0b", bg: "#fffbeb", border: "#fde68a" },
    rojo: { color: "#ef4444", bg: "#fef2f2", border: "#fecaca" },
  };

  const currentColor = statusColors[diagnostico_ia.color_sugerido] || statusColors.verde;
  const preds = diagnostico_ia.predicciones_futuras;
  const climaHoy = meteorologia.resumen_5_dias[0];

  // La gráfica ahora se alimenta 100% de la Base de Datos y la IA, no de datos sintéticos
  const history = diagnostico_ia.historial_grafica || [];

  return (
    <>
      <Header />
      <main className="detail-page">
        <Link to="/" className="back-link">
          <ArrowLeft size={18} /> Volver al centro de monitoreo
        </Link>

        <section className="detail-hero">
          <div>
            <span className="pond-eyebrow">Panel de telemetría y predicción</span>
            <h2>Estanque {data.id_estanque}</h2>
            <p>Diagnóstico gestionado por Inteligencia Artificial.</p>
          </div>

          <div
            className="detail-status"
            style={{ background: currentColor.bg, color: currentColor.color, borderColor: currentColor.border }}
          >
            <span style={{ background: currentColor.color, boxShadow: `0 0 16px ${currentColor.color}` }} />
            {diagnostico_ia.estado_salud}
          </div>
        </section>

        {/* Mostramos las PREDICCIONES FUTURAS en las tarjetas */}
        <section className="detail-grid">
          <MetricCard icon={<Thermometer />} title="Temperatura Predicha" value={`${preds.temperatura} °C`} delta="IA" trend={preds.temperatura > 30 ? "danger" : "up"} />
          <MetricCard icon={<Droplets />} title="pH Predicho" value={preds.ph} delta="IA" trend={preds.ph < 7 ? "down" : "up"} />
          <MetricCard icon={<Wind />} title="Oxígeno Predicho" value={`${preds.oxigeno} mg/L`} delta="IA" trend={preds.oxigeno < 5 ? "danger" : "up"} />
          <MetricCard icon={<Activity />} title="Dureza Predicha" value={`${preds.dureza} ppm`} delta="IA" trend="up" />
        </section>

        <section className="detail-layout">
          <article className="detail-panel chart-panel">
            <div className="panel-header">
              <div>
                <span className="pond-eyebrow">Histórico y Tendencia</span>
                <h3>Comportamiento de variables</h3>
              </div>
              <span className="update-chip">En vivo</span>
            </div>
            <div className="chart-box">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="hora" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip />
                  <Line type="monotone" dataKey="temp" stroke="#1b396a" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="oxigeno" stroke="#22c55e" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="ph" stroke="#f59e0b" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </article>

          <aside className="side-stack">
            <SideCard
              icon={<ShieldAlert />}
              title="Salud estimada por IA"
              content={`${diagnostico_ia.porcentaje_salud}% de estabilidad operativa.`}
              color={currentColor.color}
            />
            <SideCard
              icon={<CloudRain />}
              title="Clima Externo (Zacatepec)"
              content={`Máx: ${climaHoy.temp_max}°C. ${climaHoy.condiciones.join(", ")}. ${meteorologia.alerta_climatica ? "¡Alerta Meteorológica!" : ""}`}
              color={meteorologia.alerta_climatica ? "#ef4444" : "#1b396a"}
            />
            <SideCard
              icon={<Brain />}
              title="Recomendación IctioMind"
              content={diagnostico_ia.recomendacion}
              color="#0f4c81"
            />
          </aside>
        </section>
      </main>
    </>
  );
}

// Componentes internos (Sin cambios)
function MetricCard({ icon, title, value, delta, trend }) {
  const isDanger = trend === "danger";
  const isDown = trend === "down";
  const color = isDanger ? "#ef4444" : isDown ? "#f59e0b" : "#22c55e";
  const arrow = isDanger || isDown ? "↓" : "↑";
  return (
    <article className="metric-card">
      <div className="metric-icon">{icon}</div>
      <span>{title}</span>
      <strong>{value}</strong>
      <small style={{ color }}>{arrow} {delta}</small>
    </article>
  );
}

function SideCard({ icon, title, content, color }) {
  return (
    <article className="side-card">
      <div className="side-icon" style={{ color }}>{icon}</div>
      <h3>{title}</h3>
      <p style={{fontWeight: "500"}}>{content}</p>
    </article>
  );
}

export default PondDetail;