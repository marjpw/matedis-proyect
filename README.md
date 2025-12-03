# 🗜️ Compresor Huffman - Aplicación Web Interactiva

Una aplicación web moderna para compresión y descompresión de archivos usando el **algoritmo de Huffman**, con una interfaz visual premium y análisis detallado de compresión.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.2-green.svg)

## ✨ Características

- 📊 **Análisis de Archivos**: Calcula frecuencias, entropía de Shannon y visualiza el árbol de Huffman
- ⚡ **Compresión Rápida**: Comprime archivos usando codificación de Huffman
- 🔓 **Descompresión**: Recupera archivos comprimidos a su estado original
- 📈 **Comparación con gzip**: Compara el rendimiento con gzip
- 🎨 **Interfaz Moderna**: Diseño oscuro premium con animaciones suaves
- 📱 **Responsive**: Funciona perfectamente en desktop y móvil
- 🧪 **Tests Completos**: Suite de tests unitarios con pytest

## 🎯 Algoritmo de Huffman

El algoritmo de Huffman es una técnica de compresión sin pérdida que asigna códigos de longitud variable a símbolos basándose en sus frecuencias. Los símbolos más frecuentes reciben códigos más cortos, logrando compresión eficiente.

**Pasos del algoritmo:**

1. Construir tabla de frecuencias de los símbolos
2. Crear un árbol binario donde las hojas son los símbolos
3. Generar códigos binarios recorriendo el árbol
4. Codificar los datos usando los códigos generados

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto:**

   ```bash
   cd matedisProyect
   ```

2. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**

   ```bash
   python app.py
   ```

4. **Abrir en el navegador:**
   ```
   http://localhost:8000
   ```

## 📖 Uso

### Interfaz Web

1. **Cargar un archivo:**

   - Arrastra un archivo a la zona de drop o haz clic para seleccionar
   - También puedes usar el botón "Demo" para cargar un ejemplo

2. **Analizar:**

   - Haz clic en "📊 Analizar" para ver estadísticas y el árbol de Huffman
   - Visualiza la entropía, frecuencias y estructura del árbol

3. **Comprimir:**

   - Haz clic en "⚡ Comprimir" para generar archivo `.huff`
   - El archivo se descarga automáticamente
   - Verás comparación con gzip y tiempo de ejecución

4. **Descomprimir:**
   - Carga un archivo `.huff` previamente comprimido
   - Haz clic en "🔓 Descomprimir" para recuperar el original

### API REST

La aplicación expone los siguientes endpoints:

#### `POST /api/analyze`

Analiza un archivo y retorna estadísticas.

**Request:**

```bash
curl -X POST -F "file=@documento.txt" http://localhost:8000/api/analyze
```

**Response:**

```json
{
  "frequencies": {"65": 10, "66": 5, ...},
  "entropy": 4.5234,
  "tree": {...},
  "original_size": 1024
}
```

#### `POST /api/compress`

Comprime un archivo.

**Request:**

```bash
curl -X POST -F "file=@documento.txt" http://localhost:8000/api/compress -O -J
```

**Response:**
Archivo binario `.huff` + header `X-Comp-Stats` con estadísticas

#### `POST /api/decompress`

Descomprime un archivo .huff.

**Request:**

```bash
curl -X POST -F "file=@documento.txt.huff" http://localhost:8000/api/decompress -O -J
```

**Response:**
Archivo binario descomprimido

## 🧪 Tests

Ejecutar los tests unitarios:

```bash
# Ejecutar todos los tests
pytest test/test_huffman.py -v

# Ejecutar con cobertura
pytest test/test_huffman.py --cov=huffman --cov-report=html

# Ejecutar un test específico
pytest test/test_huffman.py::TestHuffmanCoder::test_compress_decompress_basic -v
```

Los tests cubren:

- ✅ Construcción del árbol de Huffman
- ✅ Generación de códigos
- ✅ Compresión y descompresión
- ✅ Casos edge (archivo vacío, un solo carácter, etc.)
- ✅ Manejo de errores
- ✅ Operaciones de bits (BitReader/BitWriter)

## 📁 Estructura del Proyecto

```
matedisProyect/
├── app.py                    # Servidor Flask (backend)
├── requirements.txt          # Dependencias Python
├── README.md                 # Este archivo
├── huffman/                  # Módulo de compresión
│   ├── __init__.py
│   ├── huffman.py           # Algoritmo de Huffman
│   └── utils.py             # Utilidades (BitIO, metadata)
├── static/                   # Frontend
│   ├── index.html           # Interfaz web
│   ├── app.js               # Lógica del cliente
│   └── styles.css           # Estilos (dark mode)
└── test/                    # Tests unitarios
    └── test_huffman.py      # Suite de tests
```

## 🎨 Características de la UI

- **Tema Oscuro Premium**: Paleta de colores moderna con degradados
- **Glassmorphism**: Efectos de vidrio esmerilado en elementos
- **Animaciones Suaves**: Transiciones y micro-animaciones
- **Notificaciones**: Sistema de alertas con feedback visual
- **Indicadores de Progreso**: Barras animadas durante operaciones
- **Visualización del Árbol**: Canvas interactivo que muestra la estructura del árbol de Huffman
- **Responsive Design**: Adaptable a cualquier tamaño de pantalla

## 📊 Rendimiento

### Tasas de Compresión Típicas

| Tipo de Archivo   | Ratio de Compresión | Comentario           |
| ----------------- | ------------------- | -------------------- |
| Texto repetitivo  | 50-70%              | Excelente compresión |
| Texto normal      | 30-50%              | Buena compresión     |
| Código fuente     | 40-60%              | Buena compresión     |
| Archivos binarios | 10-30%              | Compresión moderada  |
| Ya comprimidos    | 0% o negativo       | No efectivo          |

**Nota**: Huffman funciona mejor con datos que tienen distribución no uniforme de símbolos.

## 🔧 Configuración

### Límites del Servidor

En `app.py`:

```python
MAX_FILE_SIZE = 750 * 1024 * 1024  # 750 MB por defecto
```

### Puerto del Servidor

```python
app.run(debug=True, port=8000)  # Cambiar puerto aquí
```

## 🌟 Comparación: Huffman vs gzip

| Aspecto        | Huffman                  | gzip                    |
| -------------- | ------------------------ | ----------------------- |
| **Algoritmo**  | Solo Huffman             | LZ77 + Huffman          |
| **Velocidad**  | Rápido                   | Más lento               |
| **Ratio**      | Bueno                    | Mejor                   |
| **Mejor Para** | Educación, datos simples | Producción, uso general |

**gzip** generalmente logra mejor compresión porque combina LZ77 (elimina redundancia) con Huffman. Esta implementación es principalmente educativa y muestra cómo funciona Huffman de forma aislada.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autor

Desarrollado como proyecto educativo para demostrar el algoritmo de compresión de Huffman.

## 🙏 Agradecimientos

- David A. Huffman por el algoritmo de compresión (1952)
- Claude Shannon por la teoría de la información
- La comunidad de Python y Flask

---

**¡Disfruta comprimiendo! 🎉**
