# utils_imagenes.py
# Helpers para manejar fotos en Novedades/Eventos: o bien una URL externa,
# o un archivo subido por el usuario (se guarda como data-URI base64 en la BD).

import base64

MAX_BYTES = 2 * 1024 * 1024  # 2 MB, límite razonable para guardar en una columna TEXT


def archivo_a_data_uri(uploaded_file):
    """
    Recibe un objeto de st.file_uploader y devuelve un data-URI listo para
    usar en un <img src="..."> o None si supera el límite de tamaño.
    """
    if uploaded_file is None:
        return None
    contenido = uploaded_file.getvalue()
    if len(contenido) > MAX_BYTES:
        return None
    b64 = base64.b64encode(contenido).decode("utf-8")
    mime = uploaded_file.type or "image/png"
    return f"data:{mime};base64,{b64}"


def resolver_foto(uploaded_file, url_texto):
    """
    Prioriza el archivo subido; si no hay archivo, usa la URL pegada (si no está vacía).
    Devuelve el valor a guardar en la columna `foto`, o None.
    """
    data_uri = archivo_a_data_uri(uploaded_file)
    if data_uri:
        return data_uri
    if url_texto and url_texto.strip():
        return url_texto.strip()
    return None
