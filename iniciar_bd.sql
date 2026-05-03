DROP DATABASE IF EXISTS n8n_tuleto;
CREATE DATABASE n8n_tuleto;
USE n8n_tuleto;

CREATE TABLE catalogo_especies(
    id_especie INT AUTO_INCREMENT PRIMARY KEY,
    nombre_comun VARCHAR(50),
    temp_min DECIMAL(10,2),
    temp_max DECIMAL(10,2),
    oxigeno_min DECIMAL(10,2),
    ph_min DECIMAL(10,2),
    ph_max DECIMAL(10,2),
    dureza_min DECIMAL(10,2),
    dureza_max DECIMAL(10,2)
);

CREATE TABLE estanques(
    id_estanque INT AUTO_INCREMENT PRIMARY KEY,
    nombre_ubicacion VARCHAR(150),
    volumen_litros DECIMAL(10,2)
);

CREATE TABLE mantenimiento_estanques(
    num_mant INT AUTO_INCREMENT PRIMARY KEY,
    id_estanque INT,
    nombre_mantenimiento VARCHAR(40), 
    fecha_mantenimiento DATE, 
    FOREIGN KEY (id_estanque) REFERENCES estanques(id_estanque)
);

CREATE TABLE habitantes_estanques(
    id_estanque INT,
    id_especie INT,
    fecha_ingreso DATE,
    PRIMARY KEY (id_estanque, id_especie),
    FOREIGN KEY (id_estanque) REFERENCES estanques(id_estanque),
    FOREIGN KEY (id_especie) REFERENCES catalogo_especies(id_especie)
);

CREATE TABLE sensores_inventario(
    id_sensor INT PRIMARY KEY,
    id_estanque_actual INT,
    posicion_relativa VARCHAR(50),
    FOREIGN KEY (id_estanque_actual) REFERENCES estanques(id_estanque)
);

CREATE TABLE lecturas_telemetria(
    id_lectura INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora DATETIME,
    id_sensor INT,
    id_estanque INT,
    temperatura DECIMAL(10,2),
    oxigeno_disuelto DECIMAL(10,2),
    ph DECIMAL(10,2),
    dureza DECIMAL(10,2),
    CONSTRAINT fk_lectura_estanque FOREIGN KEY (id_estanque) REFERENCES estanques(id_estanque),
    CONSTRAINT fk_lectura_sensor FOREIGN KEY (id_sensor) REFERENCES sensores_inventario(id_sensor)
);

CREATE TABLE pronosticos_clima(
    id_pronostico INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora_registro DATETIME,
    fecha_hora_objetivo DATETIME,
    temp_ambiente_esperada DECIMAL(10,2),
    probabilidad_lluvia INT,
    alertas_meteorologicas VARCHAR(150)
);

-- Creación de los índices
CREATE INDEX idx_estanque_fecha ON lecturas_telemetria (id_estanque, fecha_hora);
CREATE INDEX idx_especies ON catalogo_especies(nombre_comun);
CREATE INDEX idx_clima_objetivo ON pronosticos_clima (fecha_hora_objetivo);