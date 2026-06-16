# Práctica de Sistemas Multi-Agente: Comunicación A2A (Agent-to-Agent)

## Objetivo de la Práctica
El objetivo de este proyecto es ilustrar la implementación de un sistema distribuido de agentes autónomos que se comunican entre sí mediante un protocolo estandarizado (A2A). El escenario desarrollado simula un debate futbolístico interactivo entre dos entidades de Inteligencia Artificial con roles contrapuestos: un analista táctico moderno (que actúa como cliente) y un historiador clásico del fútbol (que opera como servidor).

Este documento detalla la arquitectura global, el diseño lógico de ambos nodos y el flujo de ejecución necesario para replicar el experimento.

---

## Arquitectura del Sistema

El proyecto se divide en dos componentes principales que interactúan a través de una red local utilizando el protocolo **JSON-RPC** sobre **HTTP**. Toda la inferencia cognitiva está respaldada por los servicios de **Azure OpenAI**.

### 1. El Nodo Servidor (`football_debate_server.py`)
El servidor expone de forma pasiva a un agente conversacional. Su propósito es mantenerse a la escucha y emitir respuestas cuando un cliente externo inicie una comunicación.

*   **Infraestructura Web**: Utiliza **Starlette** (un framework asíncrono) gestionado mediante **Uvicorn**, exponiendo el servicio en el puerto local `5001`.
*   **Manifiesto del Agente (Agent Card)**: El servidor expone públicamente un contrato o metadatos técnicos (`AgentCard`). Esto habilita el paradigma de descubrimiento de servicios (*Service Discovery*); cualquier cliente puede consultar esta tarjeta para confirmar que el agente ("Classic Football Historian") existe, verificar sus modos de entrada/salida, y determinar la ruta y protocolo de conexión correctos.
*   **Delimitación del Comportamiento (System Prompt)**: El agente tiene inyectadas instrucciones sistémicas estrictas. Su directiva es actuar con la personalidad de un analista veterano, defendiendo tácticas históricas (como el Ajax de Cruyff o el Milan de Sacchi) y debatiendo en español con un tono directo y agresivo frente al fútbol moderno.
*   **A2AExecutor**: Es el núcleo de procesamiento. Intercepta la petición de red entrante, la empaqueta como una consulta válida para el modelo subyacente (LLM) y devuelve la respuesta estructurada de vuelta al cliente.

### 2. El Nodo Cliente (`football_debate_client.py`)
El cliente es el nodo activo de la arquitectura. Se encarga de iniciar la simulación, generar la premisa del debate y orquestar la llamada de red hacia el servidor.

*   **Generación Local**: En la primera fase, el cliente instancia localmente a su propio agente ("Modern Football Analyst"). Se le suministra una pregunta semilla (*España 2010 vs Argentina 2022*) y este agente genera un primer argumento basado en métricas analíticas contemporáneas (posesión, xG, PPDA, presión alta).
*   **Descubrimiento de Red (A2ACardResolver)**: Una vez obtenida la base del debate, el script utiliza peticiones asíncronas HTTP (`httpx`) para contactar al servidor (`http://localhost:5001/`). Extrae el manifiesto (`AgentCard`) para validar que el "Historiador Clásico" está en línea y acepta la conexión.
*   **Invocación Remota**: Utilizando el envoltorio `A2AAgent`, el cliente compila la opinión previa del analista moderno y la transmite al servidor a través de la red, instándole a que la rebata directamente.
*   **Recepción y Renderizado**: El cliente suspende su ejecución principal esperando la resolución del modelo remoto. Al recibir el bloque de texto del servidor, finaliza la simulación imprimiendo el debate estructurado en la consola.

---

## Requisitos Previos e Instalación

Para ejecutar este entorno distribuido localmente, es necesario aislar las dependencias utilizando un entorno virtual de Python.

```bash
# 1. Crear y activar un entorno virtual (recomendado)
python -m venv .venv
# En Windows (Powershell):
.\.venv\Scripts\activate

# 2. Instalar las dependencias de red y frameworks
pip install -r requirements.txt
```

### Configuración de Credenciales (`.env`)
El sistema requiere autenticación obligatoria contra la API de Azure OpenAI. Debe existir un archivo oculto `.env` en la raíz del proyecto. Este archivo ha sido deliberadamente excluido del control de versiones (`.gitignore`) por estándares críticos de seguridad. Su estructura interna debe ser la siguiente:

```ini
# Azure OpenAI Settings
AZURE_OPENAI_ENDPOINT="https://<TU_RECURSO>.openai.azure.com/"
AZURE_OPENAI_API_KEY="<TU_API_KEY_AQUI>"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini" # o la versión de tu despliegue

# A2A Configuration
A2A_AGENT_HOST="http://localhost:5001/"
```
*(Nota técnica: Es imperativo que la URI configurada en `AZURE_OPENAI_ENDPOINT` apunte a la base del recurso y no termine en el sufijo `/openai/v1`, garantizando así la correcta interoperabilidad con la API de Respuestas del SDK de Python).*

---

## Instrucciones de Ejecución

La naturaleza distribuida de esta práctica exige la ejecución concurrente de ambos nodos en terminales independientes.

### Paso 1: Inicializar el Nodo Servidor
Abra una primera terminal, asegúrese de tener activado el entorno virtual (`.venv`) y ejecute el servicio base:
```bash
python football_debate_server.py
```
*Salida esperada:* El proceso indicará por consola que el servidor ha sido levantado correctamente (`Starting A2A Server...`) en el puerto 5001. La terminal debe mantenerse abierta.

### Paso 2: Lanzar el Nodo Cliente e Iniciar el Debate
Abra una **segunda terminal** paralela, active de nuevo el entorno virtual, y lance el script cliente:
```bash
python football_debate_client.py
```
*Salida esperada:* 
1. El bloque presentará la pregunta inicial del debate.
2. El Agente Local (Analista Moderno) procesará e imprimirá su análisis completo.
3. El sistema notificará el éxito en el descubrimiento de red y la conexión remota hacia el servidor A2A.
4. El Agente Remoto (Historiador Clásico) devolverá su contraargumento, finalizando la ejecución.
