-- Prueba técnica | Analista 3 – Servicios de Nómina a Empleados
-- Autor: Shamuel Steven Molina Duque

-- Estas consultas fueron ejecutadas desde Python utilizando DuckDB, 
-- un motor SQL ligero y eficiente, ideal para entornos locales y ejercicios analíticos. 
-- Sin embargo, la sintaxis empleada es completamente compatible con Impala, 
-- lo que permite su uso directo en la LZ del banco para consultas a gran escala.

-- ============================================================
-- Limpieza de tablas fuente

WITH horas_extras_limpia AS (
    SELECT DISTINCT 
        id_empleado, 
        fecha, 
        tipo_hora, 
        cantidad_horas
    FROM horas_extras
    WHERE id_empleado IS NOT NULL 
      AND fecha IS NOT NULL
),

empleados_limpia AS (
    SELECT DISTINCT 
        id_empleado, 
        fecha_ingreso, 
        nombre, 
        tipo_contrato, 
        salario_basico
    FROM empleados
    WHERE id_empleado IS NOT NULL
),

deducciones_limpia AS (
    SELECT DISTINCT 
        id_empleado, 
        concepto, 
        valor
    FROM deducciones
    WHERE id_empleado IS NOT NULL 
      AND concepto IS NOT NULL
),

bonificaciones_limpia AS (
    SELECT DISTINCT 
        id_empleado, 
        concepto, 
        valor
    FROM bonificaciones
    WHERE id_empleado IS NOT NULL 
      AND concepto IS NOT NULL
)

-- ============================================================
-- Creación de la tabla final: nomina

CREATE TABLE nomina AS
SELECT 
    e.id_empleado,
    e.nombre,
    e.fecha_ingreso,
    e.tipo_contrato,
    e.salario_basico,

    he.fecha AS fecha_hora_extra,
    he.tipo_hora,
    he.cantidad_horas,

    d.concepto AS concepto_deduccion,
    d.valor AS valor_deduccion,

    b.concepto AS concepto_bonificacion,
    b.valor AS valor_bonificacion

FROM empleados_limpia e

LEFT JOIN horas_extras_limpia he 
    ON e.id_empleado = he.id_empleado

LEFT JOIN deducciones_limpia d 
    ON e.id_empleado = d.id_empleado

LEFT JOIN bonificaciones_limpia b 
    ON e.id_empleado = b.id_empleado;
