# Práctica de Sistemas Multi-Agente: Comunicación A2A (Agent-to-Agent)

## Objetivo de la Práctica
El objetivo de este proyecto es ilustrar la implementación de un sistema distribuido de agentes autónomos que se comunican entre sí mediante un protocolo estandarizado (A2A). El escenario desarrollado simula un debate futbolístico interactivo entre dos entidades con roles contrapuestos: un analista táctico moderno (que actúa como cliente) y un historiador clásico del fútbol (que opera como servidor).

El presente documento detalla la arquitectura, el diseño y el flujo de ejecución del componente servidor (`football_debate_server.py`).

## Arquitectura del Servidor

El servidor se encarga de exponer un agente conversacional a través de una interfaz HTTP utilizando el protocolo JSON-RPC. La infraestructura tecnológica se fundamenta en los siguientes componentes:
- **Framework Web asíncrono**: Starlette, servido mediante Uvicorn.
- **Motor de Inferencia LLM**: Azure OpenAI.
- **Framework de Agentes**: Librería `agent_framework`, empleando sus módulos específicos para el protocolo A2A.

### Análisis de Componentes y Flujo de Ejecución

El código fuente de `football_debate_server.py` sigue una estructura secuencial orientada a la configuración y despliegue del servicio. A continuación se desglosan sus etapas operativas.

#### 1. Inyección de Dependencias y Entorno
El sistema requiere credenciales de acceso para interactuar con los servicios cognitivos de Azure (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT_NAME`). Estas variables se inyectan en tiempo de ejecución utilizando el módulo `dotenv` para evitar exponer información sensible en el código fuente.

#### 2. Configuración del Cliente de Lenguaje
Se instancia la clase `AsyncAzureOpenAI` para establecer la conexión asíncrona con el proveedor del modelo. Posteriormente, este cliente nativo se encapsula dentro de `OpenAIChatClient`, una capa de abstracción del framework de agentes que estandariza las llamadas al modelo, permitiendo intercambiar el proveedor de IA subyacente si fuese necesario en futuras iteraciones.

#### 3. Definición del Manifiesto del Agente (Agent Card)
La estructura `AgentCard` funciona como un contrato público. Su propósito es exponer los metadatos y capacidades del agente para permitir el descubrimiento de red (service discovery).
Los campos declarados incluyen:
- **Identidad**: Nombre y descripción funcional del agente ("Classic Football Historian").
- **Capacidades de red**: Declaración de soporte para envío de respuestas parciales en tiempo real (*streaming*).
- **Interfaces**: Especificación del protocolo de comunicación (`JSONRPC`) y el punto de acceso (`http://localhost:5001/`).

#### 4. Delimitación del Comportamiento (System Prompt)
El comportamiento del agente se restringe mediante un conjunto de instrucciones del sistema. En este contexto, se fuerza al LLM a adoptar el rol de un analista veterano, especializado en equipos históricos como el Ajax de Cruyff o el Milan de Sacchi. Esta parametrización garantiza la coherencia de las respuestas generadas a lo largo de las interacciones y mantiene la lógica de negocio del debate.

#### 5. Orquestación y Manejo de Peticiones
La clase `DefaultRequestHandler` es el núcleo lógico del servidor HTTP. Se encarga de coordinar la entrada de datos con el modelo de lenguaje.
Requiere tres elementos para su inicialización:
- **A2AExecutor**: Un envoltorio que procesa la carga útil de la petición JSON-RPC y la redirige al objeto `Agent`.
- **Task Store**: Un sistema de almacenamiento volátil (`InMemoryTaskStore`) utilizado para llevar el control del estado y la ejecución de las tareas concurrentes.
- **Agent Card**: La referencia al manifiesto del agente para la validación de capacidades.

#### 6. Despliegue del Servidor Web
En la fase final, se inicializa la aplicación `Starlette`. Se le inyectan dos grupos de rutas de red:
- `create_agent_card_routes`: Un endpoint pasivo que sirve el manifiesto (`AgentCard`) a cualquier cliente que realice una petición de descubrimiento.
- `create_jsonrpc_routes`: El endpoint activo (mapeado a la raíz `/`) encargado de interceptar, decodificar y enrutar las peticiones JSON-RPC hacia el `RequestHandler`.

El bloqueo del hilo principal y la gestión del ciclo de eventos quedan delegados a `uvicorn`, exponiendo el servicio de manera ininterrumpida en el puerto definido.

## Instrucciones de Ejecución
Para iniciar el nodo servidor en un entorno de pruebas local, valide la existencia del archivo de configuración `.env` en la raíz del directorio y ejecute el script principal:

```bash
python football_debate_server.py
```
