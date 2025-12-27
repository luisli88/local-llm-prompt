# Especificación: Stack LLM Local para Desarrollo (Linux x86_64 + macOS Apple Silicon)

## 1. Requisitos funcionales

### RF-01: Inferencia GPU acelerada
- **Descripción**: Ejecutar modelos 7B-8B con rendimiento interactivo (>15 tokens/s)
- **Hardware**: RTX 2070 SUPER 8GB mínimo
- **Formatos**: Modelos oficiales de Ollama
- **Modelos objetivo**: Qwen2.5-Coder-7B, DeepSeek-Coder-6.7B, Mistral-7B-Instruct (vía Ollama)

### RF-02: API compatible OpenAI
- **Descripción**: Endpoint `/v1/chat/completions` para integración VSCode/Kilo Code
- **Protocolo**: HTTP JSON (OpenAI spec)
- **Autenticación**: API key opcional (dummy si se requiere)
- **Puertos**: 11434 (Ollama default)

### RF-04: Gestión de Estado Persistente
- **Descripción**: Tracking automático del estado de modelos y versiones instaladas
- **Base de datos**: SQLite local (.models.db)
- **Sincronización**: Estado real de modelos locales vs registros de configuración
- **Funciones**: Activar/desactivar modelos, actualizar versiones, mostrar estado

### RF-05: Interfaz de Usuario Mejorada
- **Descripción**: Menú interactivo con información en tiempo real
- **Características**: 
  - Indicadores visuales de estado (● activo, ○ inactivo)
  - URLs de modelos activos
  - Versiones instaladas
  - Validación automática de dependencias

### RF-06: Actualización de Modelos
- **Descripción**: Pull automático de nuevas versiones desde Ollama registry
- **Alcance**: Modelo individual o actualización masiva
- **Estado**: Detiene el modelo en uso si está activo antes de actualizar

### RF-07: Gestión Inteligente de VRAM
- **Descripción**: Control automático de modelos cargados para GPU locales
- **Mecánica**:
  - Máximo 2 modelos simultáneos (configurable; por defecto 1 en Apple Silicon)
  - `ollama stop <model>` automático para liberar VRAM
  - Monitoreo simple de uso estimado de VRAM
  - Auto-stop de modelos inactivos

### RF-08: Detección Automática de Actualizaciones
- **Descripción**: Verificación automática de versiones más recientes disponibles
- **Mecánica**: Consulta API de Ollama registry vs versiones locales
- **Notificaciones**: Indicadores visuales en interfaz de usuario
- **Acciones**: Actualización manual o automática de modelos

## RF-09: Soporte macOS Apple Silicon (Opcional)
- **Descripción**: Ejecutar la aplicación de forma nativa en macOS con chips Apple Silicon (M1/M2/M3/M4)
- **Requisitos clave**:
  - **Memoria**: Soportar memoria unificada (ej. 24GB en MacBook Air M3)
  - **Backends**: Únicamente Ollama nativo
  - **Modelos**: Se usan los modelos publicados en el registry de Ollama
  - **Instalación**: La instalación de Ollama y dependencias se centraliza en la aplicación Python (`lib/main.py`). Ejecuta `./llm-stack` para iniciar la aplicación y elige la opción **"Instalar Dependencias"** (opción 2) para que la aplicación gestione la instalación en cualquier plataforma. No se requieren modos headless ni despliegues multi-contenedor.
- **Criterios de aceptación**:
  - La detección automática identifica `apple_m3` y aplica el perfil de memoria
  - Pruebas unitarias críticas pasan en macOS o en CI macOS runners
  - La aplicación indica la ausencia de Ollama y guía la instalación

## 2. Requisitos no funcionales

### RNF-01: Performance
| Métrica | Valor mínimo | Modelo referencia |
|---------|--------------|-------------------|
| Tokens/s | 20+ | 7B (Qwen2.5-Coder) |
| Time-to-first-token | <2s | Contexto 2k tokens |
| Latencia respuesta | <500ms | Petición simple |

### RNF-02: Disponibilidad
- **Uptime**: Ollama operativo mientras el servicio está activo
- **Recuperación**: `ollama serve` disponible en <30s tras arranque

### RNF-03: Portabilidad
- **OS**: Ubuntu 24.04/25.10 (CUDA 12.x) y macOS 14/15 en Apple Silicon
- **Arquitectura**: x86_64 (Linux) y arm64 (Apple Silicon)
- **Backend**: Ollama nativo
- **Volúmenes**: Persistentes (~/.ollama/models)

## 3. Arquitectura técnica

```
┌─────────────────┐   ┌─────────────────────┐   ┌────────────────────┐
│ VSCode/Kilo     │ → │ Terminal App (CLI)  │ → │ Ollama API (local) │
│ (OpenAI client) │   │ main.py / llm-stack │   │ /api/generate      │
└─────────────────┘   └─────────────────────┘   └────────────────────┘
```

### Componentes principales:
- **CLI (main.py/llm-stack)**: Menú interactivo para instalación de dependencias, activación y gestión de modelos
- **Ollama local**: Backend único soportado (Linux x86_64 con CUDA y macOS Apple Silicon con Metal)
- **Validación automática**: Chequeo de dependencias y estado de Ollama al iniciar

## 4. Interfaz de Usuario y Gestión

### IU-01: App de Terminal Interactiva
- **Descripción**: Interfaz de línea de comandos con menú para instalación de dependencias, activación y gestión de modelos
- **Archivo principal**: `llm-stack` (launcher) que ejecuta `lib/main.py`
- **Validación automática**: Chequeo de dependencias al iniciar
- **Gestión de actualizaciones**: Detección y oferta de actualización de modelos Ollama

### IU-02: Menú de Operaciones (actual)
- Validar Instalación
- Instalar Dependencias (Python + Ollama)
- Activar Modelo
- Desactivar Modelo
- Actualizar Modelos
- Verificar Actualizaciones
- Estado del Sistema
- Configuración

## 5. Modelos recomendados (priorizados)
| Prioridad | Modelo | Tamaño disco | VRAM estimada | Tokens/s estimado | Uso principal |
|-----------|--------|--------------|---------------|-------------------|---------------|
| 1 | Qwen2.5-Coder-7B-Instruct (Ollama) | ~5GB | 6.5GB | 25-35 | Code completion |
| 2 | DeepSeek-Coder-V2-Lite-Instruct (Ollama) | ~6GB | 7GB | 20-30 | Technical reasoning |
| 3 | Mistral-7B-Instruct (Ollama) | ~4.5GB | 6GB | 30-40 | Docs/architecture |

## 6. Comandos de operación

```bash
# Ejecutar la app de terminal (launcher)
./llm-stack
# o
python -m lib.main
```

Endpoints por defecto (Ollama local):
- Base URL: http://localhost:11434/v1
- Modelos: qwen2.5-coder:latest, deepseek-coder:latest, mistral:latest
- API Key: (no requerida por defecto)

## 7. Métricas de éxito

- ✅ `curl http://localhost:11434/api/generate` responde con cualquier modelo instalado
- ✅ Menú de instalación instala dependencias y Ollama en macOS/Linux
- ✅ Activar/actualizar modelos funciona desde la CLI sin pasos manuales adicionales



