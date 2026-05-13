import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import PondDetail from "./pages/PondDetail";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/estanque/:id" element={<PondDetail />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;