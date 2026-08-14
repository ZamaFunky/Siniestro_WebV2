-- ============================================================
-- MIGRACION: TIPO DE CLIENTE
-- Particular / Aseguradora
-- No elimina datos existentes.
-- ============================================================
USE siniestro_web_v2;

SET @col_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'siniestros' AND COLUMN_NAME = 'tipo_cliente'
);
SET @sql := IF(@col_exists = 0,
  "ALTER TABLE siniestros ADD COLUMN tipo_cliente ENUM('particular','aseguradora') NOT NULL DEFAULT 'particular' AFTER nosiniestro",
  'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Registros existentes con aseguradora quedan como aseguradora.
UPDATE siniestros
SET tipo_cliente = CASE WHEN id_aseguradora IS NULL THEN 'particular' ELSE 'aseguradora' END;

-- Garantiza que particulares no conserven una aseguradora.
UPDATE siniestros SET id_aseguradora = NULL WHERE tipo_cliente = 'particular';

CREATE INDEX IF NOT EXISTS idx_tipo_cliente ON siniestros(tipo_cliente);
