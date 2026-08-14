USE siniestro_web_v2;

-- Migración segura para BD existentes. No borra registros.
SET @db = DATABASE();

SET @has_orden = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='siniestros' AND COLUMN_NAME='orden');
SET @sql = IF(@has_orden=0, 'ALTER TABLE siniestros ADD COLUMN orden INT NOT NULL DEFAULT 0 AFTER nosiniestro', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @has_estatus = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='siniestros' AND COLUMN_NAME='estatus_taller');
SET @sql = IF(@has_estatus=0, "ALTER TABLE siniestros ADD COLUMN estatus_taller ENUM('valuacion','autorizacion','reserva','esperando_piezas','citar','citado','colission') NOT NULL DEFAULT 'valuacion' AFTER telefono", 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @has_fecha = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=@db AND TABLE_NAME='siniestros' AND COLUMN_NAME='fecha_estatus_taller');
SET @sql = IF(@has_fecha=0, 'ALTER TABLE siniestros ADD COLUMN fecha_estatus_taller DATE NULL AFTER estatus_taller', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

UPDATE siniestros SET fecha_estatus_taller = COALESCE(fecha_estatus_taller, fecha_actualizacion, CURDATE()) WHERE fecha_estatus_taller IS NULL;

CREATE INDEX IF NOT EXISTS idx_orden ON siniestros(orden);
CREATE INDEX IF NOT EXISTS idx_estatus_taller ON siniestros(estatus_taller);
