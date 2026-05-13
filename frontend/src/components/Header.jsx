function Header() {
  return (
    <header
      style={{
        background: "linear-gradient(135deg,#10284d,#1b396a,#0f4c81)",
        color: "white",
        padding: "18px 34px",
        boxShadow: "0 10px 25px rgba(0,0,0,0.15)",
      }}
    >
      <div
        style={{
          maxWidth: "1450px",
          margin: "0 auto",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
          }}
        >
          <img
              src="/logo-ictiomind.png"
              alt="Logo IctioMind"
              style={{
                width: "76px",
                height: "76px",
                objectFit: "cover",
                objectPosition: "center",
                background: "white",
                borderRadius: "20px",
                padding: "0",
                boxShadow: "0 8px 20px rgba(0,0,0,0.25)",
              }}
            />

          <div>
            <h1
              style={{
                margin: 0,
                fontSize: "30px",
                fontWeight: "800",
                letterSpacing: "0.5px",
              }}
            >
              IctioMind
            </h1>

            <small style={{ opacity: 0.85 }}>
              Cerebro Predictivo Acuícola
            </small>
          </div>
        </div>

        <div
          style={{
            background: "rgba(255,255,255,0.14)",
            padding: "10px 18px",
            borderRadius: "999px",
            fontWeight: "600",
          }}
        >
          TecNM Edition
        </div>
      </div>
    </header>
  );
}

export default Header;