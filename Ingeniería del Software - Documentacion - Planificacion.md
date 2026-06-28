![][image1]

Universidad Nacional Experimental De Guayana

Vicerrectorado Académico

Coordinación General De Pregrado

Ingeniería En Informática

Materia: Ingeniería del Software, Sección N2

**\[DRAFT\]** 

**PLAN DE IMPLEMENTACIÓN DE ENDPOINTS**

**API REST · CMMS** 

**GEMA**

| Docente: \-  |    |
| :---- | ----- |

Ciudad Guayana, Junio de 2026

## **TABLA DE ASIGNACIÓN**

| \# | Recurso (Entidad) | Tabla Asociada | Sprint | RUTA BASE | Asignado A |
| :---: | ----- | ----- | :---: | ----- | ----- |
| 1 | Reportes de Fallas — FailureReport (\*ReporteFalla\*) | \`reportes\_fallas\` | Sprint 3 | \`/v1/empresas/{empresa\_id}/reportes-fallas\` | Rinaldi Giovanni |
| 2 | Órdenes de Trabajo — WorkOrder (\*OrdenTrabajo\*) | \`ordenes\_trabajo\` | Sprint 3 | \`/v1/empresas/{empresa\_id}/ordenes-trabajo\` | Miserol Jose |
| 3 | Intervenciones Técnicas — TechnicalIntervention (\*IntervencionTecnica\*) | \`intervenciones\_tecnicas\` | Sprint 3 | \`/v1/empresas/{empresa\_id}/ordenes-trabajo/{ot\_id}/intervenciones\` | Alburquerque *Sheen* |
| 4 | Consumo de Repuestos — UsedPart (\*RepuestoUtilizado\*) | \`repuestos\_utilizados\` | Sprint 3 | \`/v1/empresas/{empresa\_id}/ordenes-trabajo/{ot\_id}/intervenciones/{intervencion\_id}/repuestos-utilizados\` | Antoima Mariangel |
| 5 | Historial de Estados (Activos) — AssetStateLog (\*LogEstadoActivo\*) | \`logs\_estados\_activos\` | Sprint 3 | \`/v1/empresas/{empresa\_id}/activos/{activo\_id}/historial-estados\` | Guarema Saniurka |
| 6 | Proveedores — Supplier (\*Proveedor\*) | \`proveedores\` | Sprint 4 | \`/v1/empresas/{empresa\_id}/proveedores\` | Cesar Reyes |
| 7 | Categorías de Catálogo — ArticleCategory (\*CategoriaArticulo\*) | \`categorias\_articulos\` | Sprint 4 | \`/v1/empresas/{empresa\_id}/catalogo/categorias\` | Angel Gonzalez  |
| 8 | Artículos de Catálogo — CatalogArticle (\*ArticuloCatalogo\*) | \`articulos\_catalogo\` | Sprint 4 | \`/v1/empresas/{empresa\_id}/catalogo/articulos\` | Glihanny Sotillo |
| 9 | Inventario (Repuestos) — InventoryPart (\*InventarioRepuesto\*) | \`inventario\_repuestos\` | Sprint 4 | \`/v1/empresas/{empresa\_id}/inventario\` | Angel Gonzalez |
| 10 | Movimientos de Inventario — InventoryEntry (\*EntradaInventario\*) | \`entradas\_inventario\` | Sprint 4 | \`/v1/empresas/{empresa\_id}/inventario/{repuesto\_id}/movimientos\` |  |
| 11 | Planes de Mantenimiento — MaintenancePlan (\*PlanMantenimiento\*) | \`planes\_mantenimiento\` | Sprint 4 | \`/v1/empresas/{empresa\_id}/planes-mantenimiento\` |  |
| 12 | Ejecuciones de Planes — PlanExecution (\*PlanEjecucion\*) | \`planes\_ejecuciones\` | Sprint 4 | \`/v1/empresas/{empresa\_id}/planes-mantenimiento/{plan\_id}/ejecuciones\` |  |
| 13 | Planes de Suscripción (SaaS) — SubscriptionPlan (\*PlanSuscripcion\*) | \`planes\_suscripcion\` | Sprint 5 | \`/v1/planes\` | Mauricio Leal  |
| 14 | Usuarios (Administración) — User (\*Usuario\*) | \`usuarios\` | Sprint 5 | \`/v1/empresas/{empresa\_id}/usuarios\` | Miguelangel Leonet |
| 15 | Auditoría del Sistema — SystemAudit (\*AuditoriaSistema\*) | \`auditorias\_sistema\` | Sprint 5 | \`/v1/empresas/{empresa\_id}/auditorias\` | Franklyn Quintero  |

## **SPRINT 3: ÓRDENES DE TRABAJO**

*Módulo completo de OTs: apertura, asignación de técnicos, sesiones de intervención, consumo de repuestos, cierre técnico y validación gerencial. Pruebas funcionales en Staging.*

### **1\. REPORTES DE FALLAS**

Entidad asociada: \`FailureReport\` (\*ReporteFalla\*) — Tabla: \`reportes\_fallas\`

Rama de git: feature/failure-report

**RUTA BASE: \`/v1/empresas/{empresa\_id}/reportes-fallas\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Lista reportes con filtros por estado, prioridad y activo. | \`mantenimiento:view\` |
| POST | \`/\` | Crea un reporte (activo, descripción, prioridad). | \`mantenimiento:create\` |
| GET | \`/{reporte\_id}\` | Devuelve el detalle del reporte y la orden de trabajo generada, si existe. | \`mantenimiento:view\` |
| PATCH | \`/{reporte\_id}\` | Cambia el estado del reporte. | \`mantenimiento:edit\` |
| DELETE | \`/{reporte\_id}\` | Elimina el reporte si su estado es \`pendiente\`. | \`mantenimiento:delete\` |

### **2\. ÓRDENES DE TRABAJO (OT)**

Entidad asociada: \`WorkOrder\` (\*OrdenTrabajo\*) — Tablas: \`ordenes\_trabajo\`, \`tecnicos\_ordenes\_trabajo\`, \`logs\_estados\_ordenes\_trabajo\`

Rama de git: feature/work-order

**RUTA BASE: \`/v1/empresas/{empresa\_id}/ordenes-trabajo\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Lista órdenes con filtros por estado, tipo, técnico y fechas. | \`mantenimiento:view\` |
| POST | \`/\` | Crea una orden (activo, tipo, supervisor, descripción, costo estimado). | \`mantenimiento:create\` |
| GET | \`/{ot\_id}\` | Devuelve el detalle con intervenciones y repuestos consumidos. | \`mantenimiento:view\` |
| PATCH | \`/{ot\_id}\` | Actualiza campos mientras la orden no esté cerrada ni cancelada. | \`mantenimiento:edit\` |
| DELETE | \`/{ot\_id}\` | Elimina la orden si su estado es \`abierta\`. | \`mantenimiento:delete\` |
| POST | \`/{ot\_id}/asignar-tecnico\` | Asigna un técnico a la orden. | \`mantenimiento:edit\` |
| DELETE | \`/{ot\_id}/remover-tecnico\` | Remueve un técnico asignado. | \`mantenimiento:edit\` |
| POST | \`/{ot\_id}/validar\` | Registra firma digital: \`validado\_por\_id\` y fecha de validación. | \`mantenimiento:edit\` |
| GET | \`/{ot\_id}/historial-estados\` | Lista cambios de estado con motivo, usuario y fecha. | \`mantenimiento:view\` |

### **3\. INTERVENCIONES TÉCNICAS**

Entidad asociada: \`TechnicalIntervention\` (\*IntervencionTecnica\*) — Tabla: \`intervenciones\_tecnicas\`

Rama de git: feature/technical-intervention

**RUTA BASE: \`/v1/empresas/{empresa\_id}/ordenes-trabajo/{ot\_id}/intervenciones\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Lista intervenciones con horas-hombre totales. | \`mantenimiento:view\` |
| POST | \`/\` | Registra una intervención (técnico, fechas, horas, tareas realizadas). | \`mantenimiento:create\` |
| GET | \`/{intervencion\_id}\` | Devuelve el detalle y repuestos utilizados en la intervención. | \`mantenimiento:view\` |
| PATCH | \`/{intervencion\_id}\` | Edita la intervención si la orden no está cerrada. | \`mantenimiento:edit\` |
| DELETE | \`/{intervencion\_id}\` | Elimina la intervención. | \`mantenimiento:delete\` |

### **4\. CONSUMO DE REPUESTOS (EN INTERVENCIÓN) — USEDPART (\*REPUESTOUTILIZADO\*)**

Entidad asociada: \`UsedPart\` (\*RepuestoUtilizado\*) — Tabla: \`repuestos\_utilizados\`

Rama de git: feature/used-part

**RUTA BASE: \`/v1/empresas/{empresa\_id}/ordenes-trabajo/{ot\_id}/intervenciones/{intervencion\_id}/repuestos-utilizados\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Lista repuestos con precio histórico y subtotales. | \`mantenimiento:view\` | \`inventario:view\` |
| POST | \`/\` | Registra consumo y descuenta stock del inventario. | \`mantenimiento:edit\` | \`inventario:edit\` |
| GET | \`/{repuesto\_id}\` | Devuelve el detalle del consumo. | \`mantenimiento:view\` |
| PATCH | \`/{repuesto\_id}\` | Corrige cantidad y ajusta el movimiento de inventario correspondiente. | \`mantenimiento:edit\` |
| DELETE | \`/{repuesto\_id}\` | Revierte el consumo y restaura el stock. | \`mantenimiento:delete\` |

### **5\. HISTORIAL DE ESTADOS (ACTIVOS) — ASSETSTATELOG (\*LOGESTADOACTIVO\*)**

Entidad asociada: \`AssetStateLog\` (\*LogEstadoActivo\*) — Tabla: \`logs\_estados\_activos\`

Rama de git: feature/asset-state-log

**RUTA BASE: \`/v1/empresas/{empresa\_id}/activos/{activo\_id}/historial-estados\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Trazabilidad de estados del activo. | \`activos:view\` |

## **SPRINT 4: INVENTARIO Y MANTENIMIENTO PREVENTIVO**

*Gestión de repuestos con entradas trazadas, proveedores y alertas de stock crítico. Planes de mantenimiento preventivo con generación automática de alertas por intervalo de días.*

### **1\. PROVEEDORES — SUPPLIER (\*PROVEEDOR\*)**

Entidad asociada: \`Supplier\` (\*Proveedor\*) — Tabla: \`proveedores\`

Rama de git: feature/supplier

**RUTA BASE: \`/v1/empresas/{empresa\_id}/proveedores\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Lista proveedores con búsqueda por nombre o RIF. | \`administracion:view\` |
| POST | \`/\` | Registra un proveedor (nombre, RIF, teléfono, email, contacto). | \`administracion:create\` |
| GET | \`/{proveedor\_id}\` | Devuelve el detalle del proveedor. | \`administracion:view\` |
| PATCH | \`/{proveedor\_id}\` | Actualiza datos de contacto. | \`administracion:edit\` |
| DELETE | \`/{proveedor\_id}\` | Elimina el proveedor si no tiene repuestos de inventario asociados. | \`administracion:delete\` |

### **2\. CATÁLOGO MAESTRO — ARTICLE CATEGORY (\*CATEGORÍA ARTÍCULO\*) / CATALOGARTICLE (\*ARTÍCULO CATALOGO\*)**

Entidades asociadas: \`ArticleCategory\` (\*CategoriaArticulo\* — Tabla: \`categorias\_articulos\`), \`CatalogArticle\` (\*ArticuloCatalogo\* — Tabla: \`articulos\_catalogo\`)

Rama de git: feature/article-category

**RUTA BASE:**

* Categorías: \`/v1/empresas/{empresa\_id}/catalogo/categorias\`

* Artículos: \`/v1/empresas/{empresa\_id}/catalogo/articulos\`

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/catalogo/categorias\` | Lista categorías con conteo de artículos asociados. | \`administracion:view\` |
| POST | \`/catalogo/categorias\` | Crea una categoría (nombre y descripción). | \`administracion:create\` |
| GET | \`/catalogo/categorias/{categoria\_id}\` | Devuelve el detalle de la categoría. | \`administracion:view\` |
| PATCH | \`/catalogo/categorias/{categoria\_id}\` | Actualiza nombre o descripción. | \`administracion:edit\` |
| DELETE | \`/catalogo/categorias/{categoria\_id}\` | Elimina la categoría si no tiene artículos asociados. | \`administracion:delete\` |
| GET | \`/catalogo/articulos\` | Lista artículos con filtro opcional por \`categoria\_id\`. | \`administracion:view\` |
| POST | \`/catalogo/articulos\` | Crea un artículo (nombre, categoría opcional, fabricante, modelo, unidad de medida). | \`administracion:create\` |
| GET | \`/catalogo/articulos/{articulo\_id}\` | Devuelve el detalle del artículo. | \`administracion:view\` |
| PATCH | \`/catalogo/articulos/{articulo\_id}\` | Actualiza los datos del artículo. | \`administracion:edit\` |
| DELETE | \`/catalogo/articulos/{articulo\_id}\` | Elimina el artículo si no tiene activos ni repuestos vinculados. | \`administracion:delete\` |

### **3\. GESTIÓN DE INVENTARIO Y ALERTAS — INVENTORYPART (\*INVENTARIOREPUESTO\*) / INVENTORYENTRY (\*ENTRADAINVENTARIO\*)**

Entidades asociadas: \`InventoryPart\` (\*InventarioRepuesto\* — Tabla: \`inventario\_repuestos\`), \`InventoryEntry\` (\*EntradaInventario\* — Tabla: \`entradas\_inventario\`)

Rama de git: feature/inventory-part

**RUTA BASE: \`/v1/empresas/{empresa\_id}/inventario\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Lista repuestos con alertas de stock bajo y filtros. | \`inventario:view\` |
| POST | \`/\` | Agrega un repuesto (artículo, proveedor, stock, mínimo, precio, moneda). | \`inventario:create\` |
| GET | \`/{repuesto\_id}\` | Devuelve la ficha con stock actual, mínimo y ubicación. | \`inventario:view\` |
| PATCH | \`/{repuesto\_id}\` | Actualiza precio, stock mínimo, proveedor o ubicación. | \`inventario:edit\` |
| DELETE | \`/{repuesto\_id}\` | Elimina el repuesto si \`stock\_actual\` es 0 y no tiene movimientos. | \`inventario:delete\` |
| GET | \`/{repuesto\_id}/movimientos\` | Lista movimientos con tipo, cantidad, fecha y orden relacionada. | \`inventario:view\` |
| POST | \`/{repuesto\_id}/movimientos\` | Registra un movimiento manual (entrada o salida). | \`inventario:create\` |
| GET | \`/{repuesto\_id}/movimientos/{movimiento\_id}\` | Devuelve el detalle de un movimiento. | \`inventario:view\` |

### **4\. PLANES DE MANTENIMIENTO PREVENTIVO — MAINTENANCE PLAN (\*PLAN MANTENIMIENTO\*) / PLAN EXECUTION (\*PLAN EJECUCIÓN\*)**

Entidades asociadas: \`MaintenancePlan\` (\*PlanMantenimiento\* — Tabla: \`planes\_mantenimiento\`), \`PlanExecution\` (\*PlanEjecucion\* — Tabla: \`planes\_ejecuciones\`)

Rama de git: feature/maintenance-plan

**RUTA BASE:**

* Planes: \`/v1/empresas/{empresa\_id}/planes-mantenimiento\`

* Ejecuciones: \`/v1/empresas/{empresa\_id}/planes-mantenimiento/{plan\_id}/ejecuciones\`

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/planes-mantenimiento\` | Lista planes con indicador de urgencia (7 días o menos). | \`mantenimiento:view\` |
| POST | \`/planes-mantenimiento\` | Crea un plan (nombre, activo, tipo, intervalo en días, próxima ejecución, técnico responsable). | \`mantenimiento:create\` |
| GET | \`/planes-mantenimiento/{plan\_id}\` | Devuelve el detalle del plan y su historial de ejecuciones. | \`mantenimiento:view\` |
| PATCH | \`/planes-mantenimiento/{plan\_id}\` | Actualiza datos o activa/desactiva el plan. | \`mantenimiento:edit\` |
| DELETE | \`/planes-mantenimiento/{plan\_id}\` | Elimina el plan si no tiene ejecuciones registradas. | \`mantenimiento:delete\` |
| GET | \`/planes-mantenimiento/{plan\_id}/ejecuciones\` | Lista ejecuciones del plan con órdenes asociadas. | \`mantenimiento:view\` |
| POST | \`/planes-mantenimiento/{plan\_id}/ejecuciones\` | Registra una ejecución vinculada a una orden existente. | \`mantenimiento:create\` |
| GET | \`/planes-mantenimiento/{plan\_id}/ejecuciones/{ejecucion\_id}\` | Devuelve el detalle de una ejecución. | \`mantenimiento:view\` |

## **SPRINT 5: KPIS Y DASHBOARD GERENCIAL**

*Cálculo de MTBF y MTTR sobre datos operativos reales. Panel gerencial con métricas en tiempo real, administración de usuarios del tenant y auditorías.*

### **1\. PLANES DE SUSCRIPCIÓN (SUPER ADMIN) — SUBSCRIPTIONPLAN (\*PLANSUSCRIPCION\*)**

Entidad asociada: \`SubscriptionPlan\` (\*PlanSuscripcion\*) — Tabla: \`planes\_suscripcion\`

Rama de git: feature/plan-suscripcion

**RUTA BASE: \`/v1/planes\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Lista los planes de suscripción disponibles. | Super Admin |
| POST | \`/\` | Crea un plan con nombre, límites de activos y usuarios, y precio mensual. | Super Admin |
| GET | \`/{plan\_id}\` | Devuelve el detalle de un plan. | Super Admin |
| PATCH | \`/{plan\_id}\` | Actualiza límites, descripción o precio del plan. | Super Admin |
| DELETE | \`/{plan\_id}\` | Elimina un plan sin empresas activas suscritas. | Super Admin |

### **2\. ADMINISTRACIÓN DE USUARIOS — USER (\*USUARIO\*)**

Entidad asociada: \`User\` (\*Usuario\*) — Tabla: \`usuarios\`

Rama de git: feature/users

**RUTA BASE: \`/v1/empresas/{empresa\_id}/usuarios\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Lista usuarios con sus roles asignados. | \`administracion:view\` |
| POST | \`/\` | Crea un usuario con contraseña | \`administracion:create\` |
| GET | \`/{usuario\_id}\` | Devuelve perfil completo y roles del usuario. | \`administracion:view\` |
| PATCH | \`/{usuario\_id}\` | Actualiza datos personales o estado activo/inactivo. | \`administracion:edit\` |
| DELETE | \`/{usuario\_id}\` | Baja lógica (\`activo\` pasa a \`false\`). | \`administracion:delete\` |

### **3\. AUDITORÍA DEL SISTEMA — SYSTEMAUDIT (\*AUDITORIASISTEMA\*)**

Entidad asociada: \`SystemAudit\` (\*AuditoriaSistema\*) — Tabla: \`auditorias\_sistema\`

Rama de git: feature/system-audit

**RUTA BASE: \`/v1/empresas/{empresa\_id}/auditorias\`**

| Método | Ruta | Descripción | Permiso |
| :---: | ----- | ----- | ----- |
| GET | \`/\` | Lista entradas con filtros por usuario, acción y rango de fechas. | \`administracion:view\` |
| GET | \`/{auditoria\_id}\` | Devuelve el detalle completo de la entrada. | \`administracion:view\` |

### **4\. KPIS Y DASHBOARD (POR DISEÑAR)**

*Consumo analítico para cálculo de MTBF (Mean Time Between Failures) y MTTR (Mean Time To Repair) sobre activos y órdenes de trabajo cerradas.*

## **SPRINT 6: ESTABILIZACIÓN Y ENTREGA MVP**

*Corrección de bugs críticos detectados en Staging. Despliegue final en el servidor de producción del Ing. Oscar Cedeño. Entrega de manuales de usuario y documentación técnica.*

* \*No requiere nuevos endpoints.\*

* Enfoque en pruebas de regresión completas, optimización de consultas, y despliegue final en producción.

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGoAAABqCAMAAABj/zSlAAADAFBMVEVHcEwWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AWS6AAAAAAAAD4+86UAAAA/XRSTlMA1JsIT+gV+W/6uwQpnY+w/CLi6X0rKv79HwcB9Q/TFLkG8gNY1xcJ81Q5W77K3/vgeJdNQQtRpDr3ta3CVwLL590g+MjZUOPqHgwbXiEO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>