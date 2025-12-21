# Especificaciones relevantes para LLM local
| Componente | Especificación | Relevancia para LLM |
|---|---|---|
| CPU | AMD Ryzen 5 3600XT (6C/12T) | Alimenta GPU + tareas auxiliares (preprocesamiento, Docker) |
| GPU | NVIDIA RTX 2070 SUPER (8GB GDDR6) | Principal bottleneck: soporta 7B Q4-Q5, 8B Q4, algunos 13B Q3 |
| RAM | 32GB DDR4 2666MHz | Suficiente para sistema + Docker + contexto moderado |
| Almacenamiento | 1TB NVMe (EXT4) + 512GB NVMe | Espacio amplio para múltiples modelos (7B ~4-8GB cada uno) |
| OS | Ubuntu 25.10 (Questing Quokka) | Soporte completo CUDA 12.x + Docker |

## Capacidades VRAM para Arquitectura Single Container

### Estimaciones de Memoria por Modelo (Q4_K_M)
| Modelo | Tamaño Disco | VRAM Estimada | Tokens/s | Categoría |
|--------|-------------|---------------|----------|-----------|
| Qwen2.5-Coder | ~4.5GB | 5.0GB | 25-35 | Code Completion |
| DeepSeek-Coder | ~6GB | 6.5GB | 20-30 | Technical Reasoning |
| Mistral | ~4GB | 4.5GB | 30-40 | Documentation |

### Estrategias de Gestión VRAM
- **OLLAMA_MAX_LOADED_MODELS=3**: Máximo 3 modelos simultáneos
- **OLLAMA_KEEP_ALIVE=5m**: Auto-unload después de 5min inactividad
- **Prioridad**: Solo 1 modelo "primary" activo, otros en standby
- **Swap inteligente**: Activar modelo → desactivar de menor prioridad

### Capacidades por Escenario
| Escenario | Modelos Simultáneos | VRAM Total | Recomendación |
|-----------|-------------------|------------|---------------|
| **Code + Reasoning** | Qwen + DeepSeek | ~11.5GB | ⚠️ Límite (usar priority) |
| **Code Only** | Qwen solo | ~5GB | ✅ Óptimo |
| **All Three** | Qwen + DeepSeek + Mistral | ~16GB | ❌ Imposible |

### Recomendaciones Operativas
- **Uso típico**: 1 modelo activo + 2 en standby (OLLAMA_MAX_LOADED_MODELS=3)
- **Switching**: `ollama stop <model>` para liberar VRAM antes de activar otro
- **Monitoring**: `nvidia-smi` para verificar uso real vs estimado
- **Fallback**: Si VRAM insuficiente, usar local mode (menor overhead GPU)