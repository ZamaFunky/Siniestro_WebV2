USE siniestro_web_v2;
ALTER TABLE siniestros ADD COLUMN orden INT NOT NULL DEFAULT 0 AFTER nosiniestro;
ALTER TABLE siniestros ADD COLUMN fecha_estatus_taller DATE NULL AFTER estatus_taller;
ALTER TABLE siniestros MODIFY COLUMN estatus_taller ENUM('valuacion','autorizacion','reserva','esperando_piezas','citar','citado','colission') NOT NULL DEFAULT 'valuacion';
UPDATE siniestros SET fecha_estatus_taller=COALESCE(fecha_estatus_taller,fecha_actualizacion,CURDATE()) WHERE fecha_estatus_taller IS NULL;
