# Arquitectura Simplificada: Ollama Local Nativo

```mermaid
graph TB
    subgraph "Host Ubuntu 25.10"
        A[NVIDIA Driver<br/>580.95 + CUDA 13.0]
        B[Ollama Local<br/>Instalado nativamente]
        C[RTX 2070 SUPER<br/>8GB VRAM]
    end

    subgraph "Interfaz de Usuario"
        D[Terminal App<br/>main.py]
        E[Scripts Ocultos<br/>.scripts/]
    end

    subgraph "Configuración Local"
        L[Config YAML<br/>.llm-config.yml<br/>Modelos + Prioridades]
    end

    subgraph "Ollama Runtime Local"
        F["Ollama Service<br/>Modelos cargados dinámicamente"]
    end

    subgraph "Integraciones Desarrollo"
        J[VSCode + Kilo Code<br/>OpenAI API Client]
        K[CLI Tools<br/>ollama CLI]
    end

    D -->|ollama pull/list/rm| F
    D -->|Lee configuración| L
    E -->|Setup inicial| B
    A -->|GPU Runtime| B
    C -->|VRAM Directa| I
    L -->|Config modelos| D
    F -->|HTTP API 11434| J
    F -->|CLI directo| K

    style A fill:#e1f5fe
    style C fill:#fff3e0
    style D fill:#c8e6c9
    style L fill:#fff9c4
    style F fill:#e8f5e8
```

## Arquitectura Simplificada: Ollama Local

### ✅ Ventajas de Ollama Local Nativo
- **Mínimo Overhead**: Sin Docker = ~50MB RAM vs 200MB+ contenedor
- **Arranque Instantáneo**: 3-5s vs 10-15s contenedor
- **GPU Directa**: Mejor afinidad con RTX 2070 SUPER
- **Simplicidad**: Un comando `ollama pull/rm` directo
- **Desarrollo Fluido**: Perfecto para iteración rápida

### 🔄 Gestión de Modelos Directa
```
App Python → CLI Directo → ollama pull qwen2.5-coder:7b
                        → ollama list
                        → ollama stop deepseek-coder
```

### 📋 Configuración Externa (YAML)
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
    category: "coding"
  deepseek:
    name: "deepseek-coder:latest"
    description: "Technical reasoning and analysis"
    category: "reasoning"
  mistral:
    name: "mistral:latest"
    description: "Documentation and architecture"
    category: "general"
```

### 🛠️ Componentes Simplificados

#### 1. **OllamaManager** (ollama_manager.py)
- **Responsabilidades**: Gestión directa de Ollama CLI + actualizaciones automáticas
- **Métodos**:
  - `pull_model()`, `list_models()`, `remove_model()`
  - `get_running_models()`, `stop_model()`
  - `get_vram_usage()`, `check_model_updates()`
  - `update_model_if_available()` - Actualización automática

#### 2. **ConfigManager** (config_manager.py)
- **Responsabilidades**: Carga configuración YAML
- **Funciones**: Validación, prioridades, metadata modelos

#### 3. **CLI Interface** (cli.py)
- **Responsabilidades**: Menú interactivo simplificado
- **Características**: Estado real-time, progress bars

### 🚀 Setup Inicial Simplificado
```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Instalar app Python
pip install -r requirements.txt

# 3. Ejecutar
python main.py
```

### 📊 Comparativa Final

| Aspecto | Ollama Local ✅ | Single Container | Multi Container |
|---------|-----------------|------------------|----------------|
| **Overhead RAM** | ~50MB | ~200MB | ~600MB |
| **Arranque** | 3-5s | 10-15s | 30-45s |
| **GPU Affinity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Simplicidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Desarrollo** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

**Conclusión**: Para desarrollo local con RTX 2070 SUPER, **Ollama Local Nativo** es la arquitectura óptima.

