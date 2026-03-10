# 🌌 Semantic Guardrails (Distilled Core)

[cite_start]**Semantic Guardrails** es una implementación optimizada y destilada del motor **LSV Engine**[cite: 571]. [cite_start]Este núcleo se enfoca exclusivamente en la **aritmética vectorial de alta fidelidad** y la **seguridad semántica**, eliminando la complejidad de navegación para priorizar la lógica pura de espacios latentes[cite: 92, 118].

## 🏗️ Arquitectura de Cómputo

[cite_start]El sistema utiliza un pipeline de proyección en tiempo real para transformar dimensiones abstractas en coordenadas euclidianas[cite: 573, 580].

* [cite_start]**Neural Core**: BGE-M3 (1024D) para una captura semántica profunda[cite: 591, 762].
* [cite_start]**Shadow Projector**: Regresor MLP entrenado sobre UMAP para proyecciones de baja latencia (<10ms)[cite: 16, 734].
* [cite_start]**Vector Vault**: LanceDB para almacenamiento vectorial serverless[cite: 4, 32, 575].
* [cite_start]**Context Vault**: SQLite para la gestión de metadatos y diccionarios soberanos[cite: 37, 688].



## 📋 Stack Tecnológico

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **API** | FastAPI | [cite_start]Servidor de inferencia asíncrono[cite: 3]. |
| **Engine** | LanceDB | [cite_start]Base de datos de vectores (CrystalVault)[cite: 4]. |
| **Metadata** | SQLite | [cite_start]Capa de contexto semántico (ContextVault)[cite: 37]. |
| **Geometry** | UMAP + Sklearn | [cite_start]Reducción de dimensionalidad y Shadow Projection[cite: 727, 728]. |
| **Frontend** | React + Three.js | [cite_start]Visualización 3D reactiva y HUD[cite: 6, 7]. |

## 🚀 Despliegue Rápido (Guardrail Protocol)

1.  **Entorno**: Crear y activar `sg_env`.
2.  **Bootstrap**:
    ```bash
    chmod +x bootstrap.sh
    ./bootstrap.sh
    ```
3.  **Hidratación**:
    ```bash
    python3 backend/ingest_vocab.py
    ```

## 🧪 Operaciones de Ejemplo

[cite_start]El sistema está diseñado para resolver analogías complejas mediante manipulación directa de tensores[cite: 599]:
* [cite_start]**Operación**: `Rey - Hombre + Mujer = Reina`[cite: 118].
* [cite_start]**Espacio de Manifiesto**: Coordenadas normalizadas en cubo `[0, 300]`[cite: 39, 107].

---
*Built for the Future of Semantic Security.*