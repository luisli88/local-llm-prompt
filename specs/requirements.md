# Especificación: Stack LLM Local para Desarrollo (RTX 2070 + Ubuntu 25.10)

## 1. Requisitos funcionales

### RF-01: Inferencia GPU acelerada
- **Descripción**: Ejecutar modelos 7B-8B con rendimiento interactivo (>15 tokens/s)
- **Hardware**: RTX 2070 SUPER 8GB mínimo
- **Formatos**: GGUF Q4_K_M / Q5_K_M
- **Modelos objetivo**: Qwen2.5-Coder-7B, DeepSeek-Coder-6.7B, Mistral-7B-Instruct

### RF-02: API compatible OpenAI
- **Descripción**: Endpoint `/v1/chat/completions` para integración VSCode/Kilo Code
- **Protocolo**: HTTP JSON (OpenAI spec)
- **Autenticación**: API key opcional (dummy si se requiere)
- **Puertos**: 11434 (Ollama default)

### RF-04: Gestión de Estado Persistente
- **Descripción**: Tracking automático del estado de modelos y versiones instaladas
- **Base de datos**: SQLite local (.models.db)
- **Sincronización**: Estado real de contenedores vs base de datos
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
- **Estado**: Detiene contenedores temporalmente durante actualización

## 2. Requisitos no funcionales

### RNF-01: Performance
| Métrica | Valor mínimo | Modelo referencia |
|---------|-------------|------------------|
| Tokens/s | 20+ | 7B Q4 (Qwen2.5-Coder) |
| Time-to-first-token | <2s | Contexto 2k tokens |
| Latencia respuesta | <500ms | Single request |

### RNF-02: Disponibilidad
- **Uptime**: 100% cuando contenedor activo
- **Recuperación**: `docker compose up -d` (<30s desde apagado)

### RNF-03: Portabilidad
- **OS**: Ubuntu 24.04/25.10 (CUDA 12.x)
- **Docker**: Multi-arch (x86_64)
- **Volúmenes**: Persistentes (~/.ollama/models)

## 3. Arquitectura técnica

```
┌─────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────┐
│ VSCode/Kilo │───▶│ Terminal App │───▶│ Ollama APIs │───▶│ llama.cpp │
│ (OpenAI API) │ │ (main.sh) │ │ (Multi-container) │ │ (CUDA) │
└─────────────────┘ └──────────┬──────────┘ └──────────┬──────────┘ └──────────┬───────┘
│ │ │ │
├────────────▼────────┼────────▼─────────┼────────▼─────────┼────────▼────────┤
│ Scripts Ocultos │ │ Contenedor Qwen │ │ Contenedor DeepSeek │ │ Contenedor Mistral │
│ (.scripts/) │ │ 7B Code │ │ 6.7B Technical │ │ 7B Docs │
└─────────────────────┘ └─────────────────┘ └──────────────────┘ └─────────────────┘
                              │
                       ┌──────▼──────┐
                       │ RTX 2070 SUPER │
                       │ 8GB VRAM │
                       └───────────────┘
```

### Componentes principales:
- **Terminal App (main.sh/main.py)**: Interfaz principal con menú interactivo y sincronización automática
- **Scripts Ocultos (.scripts/)**: Automatización de instalación, gestión y model_manager.sh
- **Base de Datos SQLite (.models.db)**: Persistencia de estado y versiones de modelos
- **Contenedores Ollama**: Modelos especializados por función con estado sincronizado
- **Validación Automática**: Chequeo de dependencias y estado de contenedores al iniciar

## 4. Configuración Docker Compose

```
version: '3.8'
services:
  ollama-qwen:
    image: ollama/ollama:latest
    container_name: ollama-qwen
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_NUM_GPU_LAYERS=35
      - OLLAMA_MAX_LOADED_MODELS=1
    shm_size: 8gb

  ollama-deepseek:
    image: ollama/ollama:latest
    container_name: ollama-deepseek
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    ports:
      - "11435:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_NUM_GPU_LAYERS=35
      - OLLAMA_MAX_LOADED_MODELS=1
    shm_size: 8gb

  ollama-mistral:
    image: ollama/ollama:latest
    container_name: ollama-mistral
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    ports:
      - "11436:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_NUM_GPU_LAYERS=35
      - OLLAMA_MAX_LOADED_MODELS=1
    shm_size: 8gb

volumes:
  ollama_models:
```


## 4. Interfaz de Usuario y Gestión

### IU-01: App de Terminal Interactiva
- **Descripción**: Interfaz de línea de comandos con menú para todas las operaciones
- **Archivo principal**: `main.sh`
- **Validación automática**: Chequeo de dependencias al iniciar
- **Gestión de actualizaciones**: Detección y oferta de actualización de componentes desactualizados

### IU-02: Menú de Operaciones
- **Validar Instalación**: Verificación completa de dependencias y estado
- **Instalar Stack**: Setup automático de Docker, NVIDIA CTK y configuración
- **Activar Modelo**: Selección y activación de modelo específico
- **Desactivar Modelo**: Selección y parada de modelo específico
- **Desactivar Stack Completo**: Apagado total y liberación de recursos

### IU-03: Scripts Ocultos
- **Ubicación**: Carpeta `.scripts/` (oculta al usuario)
- **Acceso**: Solo a través de la app principal
- **Funciones**: Automatización de instalación, validación y gestión

## 5. Modelos recomendados (priorizados)

| Prioridad | Modelo | Tamaño disco | VRAM Q4 | Tokens/s estimado | Uso principal |
|-----------|--------|-------------|---------|-------------------|---------------|
| 1 | Qwen2.5-Coder-7B-Instruct-Q4_K_M | ~5GB | 6.5GB | 25-35 | Code completion |
| 2 | DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M | ~6GB | 7GB | 20-30 | Technical reasoning |
| 3 | Mistral-7B-Instruct-v0.3-Q4_K_M | ~4.5GB | 6GB | 30-40 | Docs/architecture |

## 6. Comandos de operación

### Interfaz Principal

```bash
# Ejecutar la app de terminal
./main.sh
```

La app proporciona un menú interactivo con las siguientes opciones:

1. **Validar Instalación**: Verifica estado de dependencias y ofrece actualizaciones
2. **Instalar Stack**: Setup completo automatizado
3. **Activar Modelo**: Selecciona modelo a activar (Qwen/DeepSeek/Mistral)
4. **Desactivar Modelo**: Selecciona modelo a detener
5. **Desactivar Stack Completo**: Apaga todo y libera recursos

### Configuración Kilo Code

**Para Code Completion:**
- Provider: Custom OpenAI
- Base URL: http://localhost:11434/v1
- Model: qwen2.5-coder:7b-instruct-q4_K_M
- API Key: ollama

**Para Technical Reasoning:**
- Provider: Custom OpenAI
- Base URL: http://localhost:11435/v1
- Model: qwen2.5-coder:7b-instruct-q4_K_M
- API Key: ollama

**Para Technical Reasoning:**
- Provider: Custom OpenAI
- Base URL: http://localhost:11435/v1
- Model: deepseek-coder-v2-lite-instruct-q4_K_M
- API Key: ollama

**Para Docs/Architecture:**
- Provider: Custom OpenAI
- Base URL: http://localhost:11436/v1
- Model: mistral:7b-instruct-v0.3-q4_K_M
- API Key: ollama

### Apagado gaming

```bash
# Apagar todos
docker compose down

# O apagar individualmente
docker compose down ollama-qwen
docker compose down ollama-deepseek
docker compose down ollama-mistral

# Verificar VRAM libre
nvidia-smi
```

## 7. Métricas de éxito

- ✅ `docker run --gpus all nvidia/cuda:12.4.0-base nvidia-smi` OK
- ✅ `curl http://localhost:11434/api/generate` (Qwen) responde
- ✅ `curl http://localhost:11435/api/generate` (DeepSeek) responde
- ✅ `curl http://localhost:11436/api/generate` (Mistral) responde
- ✅ Kilo Code autocompleta código en <1s (cambiar endpoint según tarea)
- ✅ `docker compose down` libera 100% VRAM en <10s

