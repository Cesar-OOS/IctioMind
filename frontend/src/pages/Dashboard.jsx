import { useState, useEffect } from "react";
import Header from "../components/Header";
import PondCard from "../components/PondCard";
import KpiCard from "../components/KpiCard";
import CriticalBanner from "../components/CriticalBanner";

function Dashboard() {
  const [ponds, setPonds] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Hacemos UNA sola llamada al nuevo endpoint dinámico
        const response = await fetch(`http://127.0.0.1:8000/api/v1/dashboard-general`);
        const result = await response.json();
        
        if (result.status === "success") {
          const livePonds = result.estanques.map(est => {
            const preds = est.predicciones;
            const isDanger = est.color_grafica === "rojo";

            return {
              id: est.estanque_id,
              nombre: `Estanque ${est.estanque_id}`,
              tipo: est.especies, // ¡AQUÍ ESTÁN LAS ESPECIES REALES!
              estado: est.color_grafica, 
              temperatura: preds.temperatura,
              ph: preds.ph,
              oxigeno: preds.oxigeno,
              dureza: preds.dureza,
              alerta: isDanger,
              riesgo: 100 - est.salud_porcentaje,
              deltas: { temperatura: 0, ph: 0, oxigeno: 0, dureza: 0 } 
            };
          });

          setPonds(livePonds);
        }
      } catch (error) {
        console.error("Error cargando dashboard:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) return <><Header /><div style={{textAlign: "center", padding: "50px"}}>Sincronizando sensores... 📡</div></>;

  // Cálculos matemáticos del Dashboard
  const ordered = [...ponds].sort((a, b) => b.riesgo - a.riesgo);
  const criticalPond = ponds.find((pond) => pond.estado === "rojo");
  const totalPonds = ponds.length;
  const activeAlerts = ponds.filter((pond) => pond.alerta).length;
  const avgTemp = ponds.length ? (ponds.reduce((sum, pond) => sum + pond.temperatura, 0) / ponds.length).toFixed(1) : 0;
  const avgOxygen = ponds.length ? (ponds.reduce((sum, pond) => sum + pond.oxigeno, 0) / ponds.length).toFixed(1) : 0;

  return (
    <>
      <Header />
      {criticalPond && <CriticalBanner pond={criticalPond} />}

      <main style={{ padding: "18px 38px 38px", maxWidth: "1450px", margin: "0 auto" }}>
        <section className="dashboard-title">
          <div>
            <h2>Centro de Monitoreo</h2>
            <p>Supervisión inteligente de estanques en tiempo real</p>
          </div>
          <div className="online-chip">● Sistema en línea (IA Activa)</div>
        </section>

        <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: "20px", marginBottom: "24px" }}>
          <KpiCard title="Estanques activos" value={totalPonds} subtitle="Sensores sincronizados" icon="🐟" tone="blue" />
          <KpiCard title="Alertas activas" value={activeAlerts} subtitle="Requieren revisión" icon="🚨" tone={activeAlerts > 0 ? "red" : "green"} />
          <KpiCard title="Temp. Promedio (Predicha)" value={`${avgTemp}°C`} subtitle="Promedio general" icon="🌡️" tone="yellow" />
          <KpiCard title="Oxígeno (Predicho)" value={`${avgOxygen} mg/L`} subtitle="Oxígeno disuelto" icon="💨" tone="green" />
        </section>

        <section>
          <div className="section-row">
            <h3>Estado predictivo por estanque</h3>
            <small>Generado por IctioMind IA hace unos segundos</small>
          </div>
          <div className="pond-grid">
            {ordered.map((pond) => (
              <PondCard key={pond.id} pond={pond} />
            ))}
          </div>
        </section>
      </main>
    </>
  );
}

export default Dashboard;