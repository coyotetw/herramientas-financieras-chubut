# Actualización — Herramientas Financieras Chubut

## Qué cambió — Carrusel de Novedades + Eventos (última actualización)

**Modularización de estilos**: todo el CSS se mudó a `styles.py`. `app.py` ahora hace `from styles import CSS` y `st.markdown(CSS, ...)` en una sola línea. No cambió nada visual, solo quedó más prolijo para editar.

**Carrusel de Novedades** (tab Actividades, arriba de todo): nueva tabla `novedades_carrusel` con foto (opcional, subida o URL), texto (obligatorio), link (opcional) y fecha de evento (opcional, solo informativa). Se mueve solo cada 6 segundos y tiene flechas "← Anterior" / "Siguiente →" para navegar manualmente. Lectura libre para todos; alta/edición/borrado solo con PIN admin, en el desplegable "⚙️ Administrar novedades del carrusel".

**Próximos eventos / Eventos realizados** (debajo del carrusel, dos columnas): nueva tabla `eventos`, separada de la del carrusel — foto (opcional), fecha de evento (obligatoria), texto (obligatorio), link (opcional). La separación entre "próximos" y "realizados" se calcula sola comparando la fecha de cada evento con la fecha de hoy, no hace falta marcarlo a mano. Mismo esquema de permisos: lectura libre, alta/edición/borrado con PIN, en "⚙️ Administrar eventos".

**Carga de fotos**: en ambos formularios podés subir un archivo desde la compu o pegar una URL — lo que completes tiene prioridad el archivo subido. Las fotos subidas se guardan como base64 directamente en la base de datos (límite 2 MB por imagen).

**Archivos nuevos/modificados en esta vuelta**:
- `styles.py` — nuevo, todo el CSS
- `utils_imagenes.py` — nuevo, helper para resolver fotos (archivo o URL)
- `app.py` — actualizado (tab Actividades reescrita)
- `db.py` — actualizado (tablas `novedades_carrusel` y `eventos` + CRUD)

Las tablas nuevas se crean solas la primera vez que la app arranca después de subir estos cambios — no hace falta correr nada a mano para esta parte.

---

## Qué cambió (actualización anterior)

1. **Consulta CUIT**: ahora es de a un CUIT por vez (antes hasta 5 en lote). Cada consulta se guarda en la tabla `consultas_cuit` de tu base Postgres. Si volvés a consultar el mismo CUIT, te avisa cuándo fue la primera vez y cuántas veces lo consultaste, y actualiza los datos. Hay un historial abajo de la consulta con todo lo revisado.

2. **Mapa de Actores** (nueva sección): tabla `mapa_actores` con Nombre, Apellido, Mail, Teléfono, Organismo, Observaciones. Cualquiera puede ver y agregar contactos. Editar y borrar requieren PIN de administrador.

3. **Legislación** (nueva sección): tabla `legislacion`, cargada inicialmente desde tu Excel "Marco Normativo - Guía para Promoción de Inversiones" (30 normativas). Filtros por Sector, Provincia y Estado. Se corrigieron automáticamente algunos valores de la columna Estado que eran notas internas de revisión (`Ale???`, `Mirko(??)`, etc.) — quedaron como "A verificar"; y un typo en Sector (`Presca` → `Pesca`). El Excel normalizado queda como respaldo (`legislacion_normalizada.xlsx`).

   Pendiente: conectar esta sección en vivo al Google Sheets — la planilla dio error 403 incluso con el link en "Cualquiera con el enlace", lo que sugiere una política de Google Workspace que bloquea el acceso anónimo. Por ahora la fuente de verdad es la base de datos, cargada una vez desde el Excel.

4. **Raíz Emprendedora**: deja de ser visible para todos. Ahora solo aparece en el menú (y se puede abrir) cuando ingresás el PIN de administrador. El resto de la app (Actividades, Programas, Créditos, Calendario, Observatorio) sigue público, sin cambios.

5. **Acceso administrador**: un PIN numérico simple, guardado como variable de entorno `ADMIN_PIN`. Mientras no ingreses el PIN, no ves Raíz Emprendedora ni los botones de editar/borrar en Mapa de Actores. El control de acceso está en `st.session_state`, así que se resetea si recargás la página o pasa un tiempo sin actividad.

## Archivos en este paquete

- `app.py` — la app completa actualizada
- `styles.py` — **nuevo**: todo el CSS, separado de la lógica
- `utils_imagenes.py` — **nuevo**: helper para fotos (archivo subido o URL)
- `modulo_cuit.py` — actualizado: `MAX_CUITS = 1`, nueva función `procesar_uno()`
- `db.py` — actualizado: acceso a las 5 tablas (consultas_cuit, mapa_actores, legislacion, novedades_carrusel, eventos)
- `cargar_legislacion.py` — script para cargar el Excel de legislación a la base (correr una sola vez)
- `legislacion_normalizada.xlsx` — Excel de respaldo con las correcciones aplicadas
- `requirements.txt` — actualizado (agrega `psycopg2-binary`, `altair`)

## Pasos para desplegar

### 1) Subir los archivos a GitHub
Reemplazá en tu repo `herramientas-financieras-chubut`:
- `app.py`
- `modulo_cuit.py`
- `requirements.txt`

Y agregá como archivos nuevos:
- `db.py`
- `cargar_legislacion.py`

### 2) Agregar la variable de entorno ADMIN_PIN en Render
En Render → tu Web Service → **Environment** → agregá:
```
ADMIN_PIN = (elegí un PIN de 4 a 6 dígitos)
```
La variable `DATABASE_URL` ya la tenés configurada de antes, no hace falta tocarla.

### 3) Cargar la legislación inicial en la base
Esto se corre **una sola vez**, desde tu máquina (no en Render):
```bash
pip install psycopg2-binary pandas openpyxl
export DATABASE_URL="postgresql://herramientas_chubut_db_user:..."   # la misma de Render
python cargar_legislacion.py Marco_Normativo_Guia_para_Promocion_de_Inversiones.xlsx
```
Esto crea automáticamente la tabla `legislacion` (si no existe) y carga las 30 normativas. Si lo corrés de nuevo, borra y recarga todo (es idempotente).

### 4) Redeploy en Render
Una vez subidos los cambios a GitHub, Render redeploya solo (o hacés "Manual Deploy" → "Deploy latest commit").

Las tablas `consultas_cuit` (con las columnas nuevas) y `mapa_actores` se crean automáticamente la primera vez que la app arranca — no hace falta correr nada a mano para esas dos.

## Cosas para decidir más adelante

- Conexión en vivo de Legislación al Google Sheets (requiere resolver el 403 — probablemente con una Service Account, ya que el link público no está funcionando).
- Si querés que el PIN persista entre sesiones del navegador (cookie) en vez de resetearse al recargar, se puede agregar más adelante.
