Especificaciones relevantes para LLM local
| Componente | Especificación | Relevancia para LLM |
|---|---|---|
| CPU | AMD Ryzen 5 3600XT (6C/12T) | Alimenta GPU + tareas auxiliares (preprocesamiento, Docker) |
| GPU | NVIDIA RTX 2070 SUPER (8GB GDDR6) | Principal bottleneck: soporta 7B Q4-Q5, 8B Q4, algunos 13B Q3 |
| RAM | 32GB DDR4 2666MHz | Suficiente para sistema + Docker + contexto moderado |
| Almacenamiento | 1TB NVMe (EXT4) + 512GB NVMe | Espacio amplio para múltiples modelos (7B ~4-8GB cada uno) |
| OS | Ubuntu 25.10 (Questing Quokka) | Soporte completo CUDA 12.x + Docker |

Capacidades prácticas:
Modelos 7B Q4/Q5: rendimiento fluido (~20-40 tokens/s)
Modelos 8B Q4: aceptable (~15-30 tokens/s)
Modelos 13B: solo Q3 agresivo, lento para uso interactivo
​