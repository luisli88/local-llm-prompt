# 🤖 LLM Stack Manager - Local Native

**Gestor inteligente de modelos LLM para desarrollo local con RTX 2070 SUPER**

Herramienta especializada para ejecutar y gestionar modelos de lenguaje grandes (LLM) en hardware local optimizado, diseñada específicamente para el flujo de trabajo de desarrollo de software con IA asistida.

## 🎯 Objetivo del Proyecto

**Proporcionar una experiencia fluida de desarrollo con IA local** que permita:

- 🚀 **Iteración rápida**: Activar/desactivar modelos instantáneamente sin afectar otras tareas
- 🎮 **Compatibilidad gaming**: Liberar VRAM completa cuando no se usa IA
- 💻 **Desarrollo continuo**: Mantenimiento de rendimiento en codificación, debugging y testing
- 🔧 **Control total**: Gestión granular de recursos GPU/CPU sin abstracciones complejas

### 💡 Caso de Uso Principal

**Desarrollador que necesita IA asistida** pero también juega videojuegos y ejecuta tareas intensivas de desarrollo en una RTX 2070 SUPER con 8GB VRAM.

**Problema resuelto**: La mayoría de herramientas LLM requieren contenedores Docker pesados o gestión manual compleja que interfiere con otros usos del sistema.

## 🖥️ Entorno de Desarrollo

### Hardware Objetivo
- **GPU**: NVIDIA RTX 2070 SUPER (8GB GDDR6)
- **CPU**: AMD Ryzen 5 3600XT (6 núcleos, 12 hilos)
- **RAM**: 32GB DDR4 2666MHz
- **Almacenamiento**: 1TB NVMe SSD (EXT4)

### Software Base
- **OS**: Ubuntu 25.10 (Questing Quokka)
- **Kernel**: Linux 6.17+
- **NVIDIA Drivers**: 580.95+
- **CUDA**: 13.0+
- **Ollama**: Latest stable (instalado nativamente)

### Configuración Optimizada
```bash
# GPU Memory: 8GB total, ~6.5GB disponibles para modelos
# Recomendación: Máximo 2 modelos simultáneos
# Modelos objetivo: 7B parameters Q4_K_M quantization
```

## ✅ Estado del Proyecto

**🟡 VERSIÓN DE PRUEBAS** - Versión 0.0.1 con arquitectura simplificada

### 🎯 Características Técnicas Implementadas
- ✅ **Arquitectura nativa**: Ollama sin contenedores Docker
- ✅ **Gestión VRAM inteligente**: Límites automáticos y liberación
- ✅ **Configuración externa**: Modelos definidos en YAML
- ✅ **Interfaz CLI moderna**: Rich library con UX fluida
- ✅ **Actualizaciones automáticas**: Detección y aplicación de updates
- ✅ **Testing completo**: 50+ pruebas unitarias (>95% cobertura)

## 🚀 Características Técnicas

### 🤖 Motor de IA
- **Ollama Nativo**: Ejecución directa sin contenedores Docker
- **API Compatible OpenAI**: Endpoint `/v1/chat/completions` para integración IDE
- **Modelos Optimizados**: Quantización Q4_K_M para RTX 2070 SUPER
- **Gestión de Memoria**: Control granular de VRAM GPU

### 🎯 Gestión Inteligente de Recursos
- **Límites VRAM**: Máximo 2 modelos simultáneos (8GB RTX 2070)
- **Activación bajo demanda**: Modelos cargados solo cuando se necesitan
- **Liberación automática**: Stop de modelos inactivos para gaming/desarrollo
- **Monitoreo real-time**: Estado de GPU, CPU y memoria

### ⚙️ Configuración Declarativa
- **YAML Externo**: Modelos definidos en `config/models.yml`
- **Sin base de datos**: Configuración como código, versionable
- **Validación automática**: Verificación de configuración al inicio
- **Hot-reload**: Cambios aplicados sin reiniciar

### 🎨 Experiencia de Usuario
- **CLI Moderna**: Rich library con colores, tablas y progreso visual
- **Menús Interactivos**: Navegación intuitiva con indicadores visuales
- **Feedback inmediato**: Estados, progreso y errores claramente comunicados
- **Manejo de errores**: Recuperación automática y mensajes informativos

## 📋 Requisitos del Sistema

Esta aplicación soporta **Linux (NVIDIA + CUDA)** y **macOS Apple Silicon (Metal)** como plataformas equivalentes con la misma arquitectura base.

### Requisitos Base (Ambas Plataformas)

- **Python**: 3.11+ con venv
- **Ollama**: Última versión estable (instalación nativa)
- **Dependencias Python**: Especificadas en `requirements.txt`

La instalación y comportamiento en tiempo de ejecución están unificados y centralizados en la aplicación Python (`lib/main.py`).

### Especificaciones por Plataforma

#### Linux (NVIDIA + CUDA)
- **NVIDIA Drivers**: 580.95+ recomendado
- **CUDA**: 13.0+
- **Optimización**: Quantización Q4_K_M para modelos de 7B parameters
- **Gestión VRAM**: Máximo 2 modelos simultáneos (recomendado para GPUs de 8GB)

#### macOS Apple Silicon (M1/M2/M3/M4+)
- **Metal**: Aceleración integrada automática
- **Memoria unificada**: Ajusta `max_loaded_models` según memoria disponible
- **Configuración**: Perfiles específicos en `config/app.yml` y `config/models.yml`
- **Recomendación**: Preferir 1 modelo grande o múltiples pequeños según RAM disponible

---

### Instalación de Ollama y Dependencias

El launcher `./llm-stack` maneja solo el entorno virtual Python. Para instalar Ollama y dependencias:

1. **Opción automática**: Ejecuta `./llm-stack` y selecciona "Instalar Dependencias" (opción 2)
2. **Opción manual**: Instala Ollama según tu plataforma desde https://ollama.ai

Alternativamente, export `LLM_SKIP_INSTALL=1` antes de ejecutar `./llm-stack` para omitir pasos de instalación interactiva.

### Verificación de Requisitos

```bash
# Validación automática
./llm-stack  # Selecciona opción 1: "🔍 Validar Instalación Completa"

# Verificación manual
python3 --version          # Verificar Python 3.11+
ollama --version           # Verificar Ollama instalado
```

El sistema detecta automáticamente tu plataforma y ofrece recomendaciones específicas de modelos y límites de memoria.

### Dependencias Python

```txt
rich>=13.7.0        # CLI moderna
pyyaml>=6.0.0       # Configuración YAML
requests>=2.31.0    # APIs HTTP
pytest>=7.0.0       # Testing (opcional)
```

---

> **Consejo de Memoria**: 
> - **Linux/NVIDIA**: Monitorea con `nvidia-smi` durante uso intensivo
> - **macOS Apple Silicon**: La memoria es unificada; ajusta límites en `config/app.yml` según disponibilidad

## 🛠️ Instalación y Configuración

### Instalación (3 pasos simples)
```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd local-llm-prompt

# 2. Hacer ejecutable el script launcher
chmod +x llm-stack

# 3. Ejecutar (configura todo automáticamente)
./llm-stack
```

**¡Eso es todo!** El launcher script automáticamente:
- ✅ Verifica Python 3.8+
- ✅ Crea entorno virtual (.venv)
- ✅ Instala dependencias Python
- ✅ Crea configuración inicial
- ✅ Inicia la aplicación

### Verificación
```bash
# Ejecutar verificación automática
./llm-stack
# Seleccionar opción 1: "🔍 Validar Instalación Completa"
```

## 🎯 Guía de Uso

### Flujo de Trabajo Típico

#### 1. **Inicio de Sesión de Desarrollo**
```bash
# Desde el directorio del proyecto
cd local-llm-prompt

# Iniciar aplicación (maneja venv automáticamente)
./llm-stack
```

#### 2. **Verificar Estado del Sistema**
```
Selecciona una opción [1/2/3/4/5/6/7/8/0]: 7

📊 Estado del Sistema
Componente          Estado          Detalle
Servicio Ollama     ✅ Activo       http://localhost:11434
Modelos Instalados  📦 3            Corriendo: 1
VRAM RTX 2070       🧠 4GB / 8GB    Máx: 2 modelos
```

#### 3. **Activar Modelo para Trabajo**
```
Selecciona una opción [1/2/3/4/5/6/7/8/0]: 3

🟢 Activación Inteligente de Modelo
Modelos disponibles en configuración:
  1. qwen: qwen2.5-coder:latest - Code completion and programming
  2. deepseek: deepseek-coder:latest - Technical reasoning and analysis
  3. mistral: mistral:latest - Documentation and architecture

Selecciona modelo para activar: 1
¿Activar qwen2.5-coder:latest? [y/N]: y

📥 Modelo qwen2.5-coder:latest no instalado, descargando...
🧪 Activando modelo: qwen2.5-coder:latest
✅ Modelo qwen2.5-coder:latest activado exitosamente
💡 El modelo está listo para usar en VSCode/Kilo Code
```

#### 4. **Trabajar con IA en el IDE**
- Abrir VSCode/Kilo Code
- Configurar provider: Custom OpenAI
- Base URL: `http://localhost:11434/v1`
- Model: `qwen2.5-coder:latest`
- API Key: `ollama`

#### 5. **Liberar Recursos para Gaming/Testing**
```
Selecciona una opción [1/2/3/4/5/6/7/8/0]: 4

🛑 Desactivando Modelo
Modelos activos:
  1. qwen2.5-coder:latest

Selecciona modelo para desactivar: 1
¿Desactivar qwen2.5-coder:latest y liberar VRAM? [y/N]: y

✅ Modelo qwen2.5-coder:latest desactivado
💾 VRAM liberada para gaming o otros modelos
```

### Modelos Optimizados para RTX 2070 SUPER

| Modelo | Comando | VRAM | Uso Principal | Estado |
|--------|---------|------|---------------|--------|
| **Qwen2.5-Coder-7B** | `qwen` | ~5GB | Code completion | ✅ Recomendado |
| **DeepSeek-Coder-V2-Lite** | `deepseek` | ~6.5GB | Technical reasoning | ✅ Recomendado |
| **Mistral-7B-Instruct** | `mistral` | ~4.5GB | Documentation | ⚠️ Solo si VRAM libre |

### ⚠️ Límites de Hardware
- **Máximo 2 modelos simultáneos** en RTX 2070 SUPER 8GB
- **Liberar VRAM antes de gaming** para rendimiento óptimo
- **Monitorear temperatura GPU** durante uso intensivo

## 🏗️ Arquitectura Técnica

### Diseño Simplificado
```
Usuario → CLI Rich → ConfigManager → OllamaManager → Ollama CLI → GPU
```

### Componentes Core

#### 🤖 OllamaManager
**Responsabilidad**: Interfaz directa con Ollama CLI
- ✅ Gestión de modelos (pull, run, stop, rm)
- ✅ Control de VRAM y límites automáticos
- ✅ Detección de actualizaciones desde registry
- ✅ Monitoreo de estado GPU/CPU

#### ⚙️ ConfigManager
**Responsabilidad**: Configuración externa YAML
- ✅ Carga de `config/models.yml` y `config/app.yml`
- ✅ Validación de configuración y modelos
- ✅ Creación automática de archivos por defecto
- ✅ Sin base de datos, configuración como código

#### 🎨 CLI Interface
**Responsabilidad**: UX moderna y navegación
- ✅ Menús interactivos con Rich library
- ✅ Estados visuales y progreso de operaciones
- ✅ Manejo de errores y recuperación automática
- ✅ Feedback inmediato para todas las operaciones

### Configuración Declarativa

```yaml
# config/models.yml
global:
  ollama_host: "http://localhost:11434"
  max_loaded_models: 2
  auto_stop_inactive: true

models:
  qwen:
    name: "qwen2.5-coder:latest"
    description: "Code completion and programming"
  deepseek:
    name: "deepseek-coder:latest"
    description: "Technical reasoning and analysis"
```

## 🧪 Calidad y Testing

### Suite de Pruebas Completa
```bash
# Ejecutar todas las pruebas
pytest lib/__tests__/ -v

# Con reporte de cobertura
pytest lib/__tests__/ --cov=lib --cov-report=html
```

**📊 Métricas**: 50+ pruebas unitarias, >95% cobertura, mocks completos

### Componentes Testeados
- ✅ **ConfigManager**: Carga YAML, validación, configuración por defecto
- ✅ **OllamaManager**: Gestión modelos, VRAM, actualizaciones automáticas
- ✅ **CLI Interface**: UX, navegación, manejo de errores
- ✅ **Integración**: Workflows completos end-to-end

## 📁 Estructura del Proyecto

```
local-llm-prompt/
├── config/                 # ⚙️ Configuración externa
│   ├── models.yml         # Modelos disponibles
│   └── app.yml           # Configuración aplicación
├── lib/                   # 📦 Código fuente
│   ├── main.py           # 🚀 CLI principal
│   ├── config_manager.py # ⚙️ Gestión YAML
│   ├── ollama_manager.py # 🤖 Cliente Ollama
│   └── __tests__/        # 🧪 Tests unitarios
├── specs/                # 📋 Documentación técnica
├── requirements.txt      # 📦 Dependencias
└── README.md            # 📖 Esta guía
```

## ⚙️ Configuración Kilo Code / VSCode

Después de activar un modelo, configúralo en tu IDE:

**Configuración OpenAI Compatible:**
- **Provider**: Custom OpenAI
- **Base URL**: `http://localhost:11434/v1`
- **API Key**: `ollama`
- **Model**: Nombre del modelo activado (ej: `qwen2.5-coder:latest`)

## 🚨 Troubleshooting

### Problemas Comunes

**Ollama no responde:**
```bash
# Verificar servicio
ollama list

# Reiniciar si es necesario
ollama serve
```

**Modelo no carga:**
```bash
# Verificar VRAM disponible
nvidia-smi

# Detener otros modelos
./llm-stack  # Opción 4 (Desactivar Modelo)
```

**Configuración corrupta:**
```bash
# Resetear configuración
rm -rf config/
./llm-stack  # Recreará archivos automáticamente
```

## 🎯 Próximos Pasos

### **Inicio Rápido**
1. **Clonar**: `git clone <repo> && cd local-llm-prompt`
2. **Ejecutar**: `chmod +x llm-stack && ./llm-stack`
3. **¡Listo!** Todo se configura automáticamente

### **🔮 Expansión Futura: macOS Apple Silicon**
Próxima versión incluirá soporte completo para MacBook Pro/Max con chips M1/M2/M3/M4, expandiendo el alcance a ~30% del mercado de desarrollo.

## 💡 Consejos para RTX 2070 SUPER

- **Máximo 2 modelos simultáneos** (8GB VRAM límite)
- **Liberar VRAM para gaming** deteniendo modelos activos
- **Monitorear temperatura** durante uso intensivo
- **Actualizaciones automáticas** disponibles en el menú

---

**🚀 ¡Listo para desarrollo fluido con IA local!**

**🔮 Próxima expansión: Soporte macOS Apple Silicon** 🍎