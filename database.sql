-- ============================================================
-- BASE DE DATOS: SINIESTRO_WEB_V2
-- Sistema de Gestión de Siniestros
-- ============================================================

DROP DATABASE IF EXISTS siniestro_web_v2;

CREATE DATABASE siniestro_web_v2
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE siniestro_web_v2;


-- ============================================================
-- TABLA: ASEGURADORAS
-- ============================================================

CREATE TABLE aseguradoras (
    id_aseguradora INT AUTO_INCREMENT PRIMARY KEY,

    nombre VARCHAR(100) NOT NULL UNIQUE,

    activo BOOLEAN NOT NULL DEFAULT TRUE
);


-- ============================================================
-- TABLA: SINIESTROS
-- ============================================================

CREATE TABLE siniestros (
    id_siniestro INT AUTO_INCREMENT PRIMARY KEY,

    -- Número de siniestro
    nosiniestro VARCHAR(50) NOT NULL UNIQUE,

    -- Tipo de cliente: particular o aseguradora
    tipo_cliente ENUM('particular','aseguradora') NOT NULL DEFAULT 'particular',

    -- Orden del siniestro dentro del tablero
    orden INT NOT NULL DEFAULT 0,

    -- Información del vehículo
    modelo VARCHAR(100) NOT NULL,

    color VARCHAR(50) NOT NULL,

    placas VARCHAR(20) NOT NULL,

    -- Fecha de actualización
    fecha_actualizacion DATE NOT NULL,

    -- Aseguradora
    id_aseguradora INT NULL,

    -- Costos
    refacciones DECIMAL(12,2) NOT NULL DEFAULT 0.00,

    mano_obra DECIMAL(12,2) NOT NULL DEFAULT 0.00,

    -- Teléfono del cliente
    telefono VARCHAR(20) NULL,

    -- Estado del vehículo dentro del taller
    estatus_taller ENUM(
        'valuacion',
        'autorizacion',
        'reserva',
        'esperando_piezas',
        'citar',
        'citado',
        'colission'
    ) NOT NULL DEFAULT 'valuacion',

    -- Fecha desde la que cuenta la etapa actual
    fecha_estatus_taller DATE NOT NULL DEFAULT (CURRENT_DATE),

    -- Indica si el vehículo ya terminó
    terminado BOOLEAN NOT NULL DEFAULT FALSE,

    -- Fechas del registro
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    -- Relación con aseguradoras
    CONSTRAINT fk_siniestro_aseguradora
        FOREIGN KEY (id_aseguradora)
        REFERENCES aseguradoras(id_aseguradora)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);


-- ============================================================
-- TABLA: COMENTARIOS
-- ============================================================

CREATE TABLE comentarios (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,

    id_siniestro INT NOT NULL,

    comentario TEXT NOT NULL,

    fecha_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_comentario_siniestro
        FOREIGN KEY (id_siniestro)
        REFERENCES siniestros(id_siniestro)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- ÍNDICES
-- ============================================================

CREATE INDEX idx_nosiniestro
ON siniestros(nosiniestro);

CREATE INDEX idx_orden
ON siniestros(orden);

CREATE INDEX idx_placas
ON siniestros(placas);

CREATE INDEX idx_modelo
ON siniestros(modelo);

CREATE INDEX idx_fecha_actualizacion
ON siniestros(fecha_actualizacion);

CREATE INDEX idx_aseguradora
ON siniestros(id_aseguradora);

CREATE INDEX idx_tipo_cliente
ON siniestros(tipo_cliente);

CREATE INDEX idx_fecha_estatus_taller
ON siniestros(fecha_estatus_taller);

CREATE INDEX idx_terminado
ON siniestros(terminado);

CREATE INDEX idx_estatus_taller
ON siniestros(estatus_taller);


-- ============================================================
-- ASEGURADORAS INICIALES
-- ============================================================

INSERT INTO aseguradoras (nombre) VALUES
('AXA'),
('GNP'),
('Qualitas'),
('HDI'),
('Chubb'),
('Mapfre'),
('Zurich'),
('ABA'),
('Banorte'),
('Afirme'),
('Otra');


-- ============================================================
-- PROCEDIMIENTO: REGISTRAR SINIESTRO
-- ============================================================

DELIMITER //

CREATE PROCEDURE registrar_siniestro(
    IN p_nosiniestro VARCHAR(50),
    IN p_tipo_cliente VARCHAR(20),
    IN p_orden INT,
    IN p_modelo VARCHAR(100),
    IN p_color VARCHAR(50),
    IN p_placas VARCHAR(20),
    IN p_fecha_actualizacion DATE,
    IN p_id_aseguradora INT,
    IN p_refacciones DECIMAL(12,2),
    IN p_mano_obra DECIMAL(12,2),
    IN p_telefono VARCHAR(20),
    IN p_estatus VARCHAR(30)
)
BEGIN
    INSERT INTO siniestros (
        nosiniestro, tipo_cliente, orden, modelo, color, placas,
        fecha_actualizacion, id_aseguradora, refacciones, mano_obra,
        telefono, estatus_taller, fecha_estatus_taller
    )
    VALUES (
        p_nosiniestro,
        COALESCE(p_tipo_cliente, 'particular'),
        COALESCE(p_orden, 0),
        p_modelo,
        p_color,
        p_placas,
        COALESCE(p_fecha_actualizacion, CURDATE()),
        CASE WHEN COALESCE(p_tipo_cliente, 'particular') = 'aseguradora' THEN p_id_aseguradora ELSE NULL END,
        COALESCE(p_refacciones, 0),
        COALESCE(p_mano_obra, 0),
        p_telefono,
        COALESCE(p_estatus, 'valuacion'),
        COALESCE(p_fecha_actualizacion, CURDATE())
    );
END //

DELIMITER ;


-- ============================================================
-- PROCEDIMIENTO: ACTUALIZAR SINIESTRO
-- ============================================================

DELIMITER //

CREATE PROCEDURE actualizar_siniestro(
    IN p_nosiniestro VARCHAR(50),
    IN p_tipo_cliente VARCHAR(20),
    IN p_orden INT,
    IN p_modelo VARCHAR(100),
    IN p_color VARCHAR(50),
    IN p_placas VARCHAR(20),
    IN p_id_aseguradora INT,
    IN p_refacciones DECIMAL(12,2),
    IN p_mano_obra DECIMAL(12,2),
    IN p_telefono VARCHAR(20),
    IN p_estatus VARCHAR(30)
)
BEGIN
    UPDATE siniestros
    SET
        tipo_cliente = COALESCE(p_tipo_cliente, tipo_cliente),
        orden = COALESCE(p_orden, 0),
        modelo = p_modelo,
        color = p_color,
        placas = p_placas,
        id_aseguradora = CASE
            WHEN COALESCE(p_tipo_cliente, tipo_cliente) = 'aseguradora'
            THEN p_id_aseguradora
            ELSE NULL
        END,
        refacciones = COALESCE(p_refacciones, 0),
        mano_obra = COALESCE(p_mano_obra, 0),
        telefono = p_telefono,
        estatus_taller = COALESCE(p_estatus, estatus_taller),
        fecha_actualizacion = CURDATE(),
        fecha_estatus_taller = CASE
            WHEN p_estatus IS NOT NULL AND p_estatus <> estatus_taller THEN CURDATE()
            ELSE fecha_estatus_taller
        END
    WHERE nosiniestro = p_nosiniestro;
END //

DELIMITER ;


-- ============================================================
-- PROCEDIMIENTO: ACTUALIZAR ORDEN
-- ============================================================

DELIMITER //

CREATE PROCEDURE actualizar_orden(
    IN p_nosiniestro VARCHAR(50),
    IN p_orden INT
)
BEGIN

    UPDATE siniestros

    SET
        orden = p_orden

    WHERE nosiniestro = p_nosiniestro;

END //

DELIMITER ;


-- ============================================================
-- PROCEDIMIENTO: ACTUALIZAR ESTATUS
-- ============================================================

DELIMITER //

CREATE PROCEDURE actualizar_estatus(
    IN p_nosiniestro VARCHAR(50),
    IN p_estatus VARCHAR(30)
)
BEGIN

    UPDATE siniestros
    SET
        estatus_taller = p_estatus,
        fecha_estatus_taller = CASE
            WHEN estatus_taller <> p_estatus THEN CURDATE()
            ELSE fecha_estatus_taller
        END,
        fecha_actualizacion = CURDATE()
    WHERE nosiniestro = p_nosiniestro;

END //

DELIMITER ;


-- ============================================================
-- PROCEDIMIENTO: MARCAR COMO TERMINADO
-- ============================================================

DELIMITER //

CREATE PROCEDURE terminar_siniestro(
    IN p_nosiniestro VARCHAR(50)
)
BEGIN

    UPDATE siniestros

    SET
        terminado = TRUE,
        fecha_actualizacion = CURDATE()

    WHERE nosiniestro = p_nosiniestro;

END //

DELIMITER ;


-- ============================================================
-- PROCEDIMIENTO: ELIMINAR SINIESTRO
-- ============================================================

DELIMITER //

CREATE PROCEDURE eliminar_siniestro(
    IN p_nosiniestro VARCHAR(50)
)
BEGIN

    DELETE FROM siniestros

    WHERE nosiniestro = p_nosiniestro;

END //

DELIMITER ;


-- ============================================================
-- PROCEDIMIENTO: BUSCAR SINIESTRO
-- ============================================================

DELIMITER //

CREATE PROCEDURE buscar_siniestro(
    IN p_nosiniestro VARCHAR(50)
)
BEGIN

    SELECT
        s.id_siniestro,

        s.nosiniestro,

        s.tipo_cliente,

        s.orden,

        s.modelo,

        s.color,

        s.placas,

        s.fecha_actualizacion,

        a.nombre AS aseguradora,

        s.refacciones,

        s.mano_obra,

        (s.refacciones + s.mano_obra) AS total,

        s.telefono,

        s.estatus_taller,

        s.fecha_estatus_taller,

        s.terminado,

        s.fecha_creacion,

        s.fecha_modificacion

    FROM siniestros s

    LEFT JOIN aseguradoras a
        ON s.id_aseguradora = a.id_aseguradora

    WHERE s.nosiniestro = p_nosiniestro;

END //

DELIMITER ;


-- ============================================================
-- PROCEDIMIENTO: LISTAR TODOS LOS SINIESTROS
-- ============================================================

DELIMITER //

CREATE PROCEDURE listar_siniestros()
BEGIN

    SELECT
        s.id_siniestro,

        s.nosiniestro,

        s.tipo_cliente,

        s.orden,

        s.modelo,

        s.color,

        s.placas,

        s.fecha_actualizacion,

        a.nombre AS aseguradora,

        s.refacciones,

        s.mano_obra,

        (s.refacciones + s.mano_obra) AS total,

        s.telefono,

        s.estatus_taller,

        s.fecha_estatus_taller,

        s.terminado,

        s.fecha_creacion,

        s.fecha_modificacion

    FROM siniestros s

    LEFT JOIN aseguradoras a
        ON s.id_aseguradora = a.id_aseguradora

    ORDER BY
        s.orden ASC,
        s.id_siniestro ASC;

END //

DELIMITER ;


-- ============================================================
-- VISTA GENERAL DE SINIESTROS
-- ============================================================

CREATE VIEW vista_siniestros AS

SELECT
    s.id_siniestro,

    s.nosiniestro AS 'No. Siniestro',

    s.tipo_cliente AS 'Tipo Cliente',

    s.orden AS 'Orden',

    s.modelo AS 'Modelo',

    s.color AS 'Color',

    s.placas AS 'Placas',

    a.nombre AS 'Aseguradora',

    s.fecha_actualizacion AS 'Última Actualización',

    s.refacciones AS 'Refacciones',

    s.mano_obra AS 'Mano de Obra',

    (s.refacciones + s.mano_obra) AS 'Total',

    s.telefono AS 'Teléfono',

    s.estatus_taller AS 'Estatus Taller',

    s.fecha_estatus_taller AS 'Fecha Etapa',

    CASE
        WHEN s.tipo_cliente = 'particular' THEN 'Particular'
        ELSE COALESCE(a.nombre, 'Sin aseguradora')
    END AS 'Cliente / Aseguradora',

    s.terminado AS 'Terminado',

    s.fecha_creacion AS 'Fecha Creación',

    s.fecha_modificacion AS 'Fecha Modificación'

FROM siniestros s

LEFT JOIN aseguradoras a
    ON s.id_aseguradora = a.id_aseguradora;


-- ============================================================
-- DATOS DE PRUEBA
-- ============================================================

INSERT INTO siniestros (
    nosiniestro,
    tipo_cliente,
    orden,
    modelo,
    color,
    placas,
    fecha_actualizacion,
    id_aseguradora,
    refacciones,
    mano_obra,
    telefono,
    estatus_taller,
    fecha_estatus_taller,
    terminado
)
VALUES
(
    'SIN-001',
    'aseguradora',
    1,
    'Mazda 3',
    'Rojo',
    'ABC-123',
    CURDATE(),
    1,
    1500.00,
    800.00,
    '4271234567',
    'valuacion',
    CURDATE(),
    FALSE
),

(
    'SIN-002',
    'aseguradora',
    2,
    'Mazda CX-5',
    'Blanco',
    'DEF-456',
    CURDATE(),
    3,
    3500.00,
    1200.00,
    '4279876543',
    'autorizacion',
    CURDATE(),
    FALSE
),

(
    'SIN-003',
    'particular',
    3,
    'Mazda CX-30',
    'Gris',
    'GHI-789',
    CURDATE(),
    2,
    2800.00,
    1500.00,
    '4274567890',
    'reserva',
    CURDATE(),
    FALSE
);


-- ============================================================
-- COMENTARIOS DE PRUEBA
-- ============================================================

INSERT INTO comentarios (
    id_siniestro,
    comentario
)
VALUES
(
    1,
    'El vehículo se encuentra en proceso de reparación. Se están esperando las refacciones correspondientes.'
),

(
    2,
    'Siniestro enviado a autorización por parte de la aseguradora.'
),

(
    3,
    'Vehículo reservado para ingreso al taller.'
);


-- ============================================================
-- CONSULTA FINAL
-- ============================================================

SELECT *
FROM vista_siniestros
ORDER BY `Orden` ASC;


-- ============================================================
-- CONSULTAS ÚTILES
-- ============================================================

-- Ver todos los siniestros ordenados
SELECT *
FROM siniestros
ORDER BY orden ASC;


-- Ver solamente los siniestros activos
SELECT *
FROM siniestros
WHERE terminado = FALSE
ORDER BY orden ASC;


-- Ver siniestros por estatus
SELECT *
FROM siniestros
WHERE estatus_taller = 'valuacion'
ORDER BY orden ASC;


-- Ver comentarios de un siniestro
SELECT
    c.id_comentario,
    c.id_siniestro,
    s.nosiniestro,
    c.comentario,
    c.fecha_comentario
FROM comentarios c
INNER JOIN siniestros s
    ON c.id_siniestro = s.id_siniestro
ORDER BY c.fecha_comentario DESC;


-- Ver costo total de cada siniestro
SELECT
    nosiniestro,
    orden,
    modelo,
    refacciones,
    mano_obra,
    (refacciones + mano_obra) AS total
FROM siniestros
ORDER BY orden ASC;