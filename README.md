# Práctica de Sistemas Multi-Agente: Comunicación A2A (Agent-to-Agent) y Protocolo MCP

## Objetivo de la Práctica
El objetivo de este proyecto es ilustrar la implementación de un sistema distribuido de agentes autónomos que se comunican entre sí mediante un protocolo estandarizado (A2A) y el Model Context Protocol (MCP). El escenario desarrollado simula un debate futbolístico interactivo entre dos entidades de Inteligencia Artificial con roles contrapuestos: un analista táctico moderno (que actúa como cliente) y un historiador clásico del fútbol (que opera como servidor). Adicionalmente, el proyecto integra herramientas MCP desplegadas en Azure para potenciar a los agentes con capacidades de búsqueda en tiempo real (Wikipedia, DuckDuckGo) y un cliente MCP de GitHub.

Este documento detalla la arquitectura global, el diseño lógico de los nodos y el flujo de ejecución necesario para replicar el experimento.

---

## Arquitectura del Sistema

El proyecto se divide en componentes principales que interactúan a través de una red local (JSON-RPC) y la nube (Azure Functions / MCP). Toda la inferencia cognitiva está respaldada por los servicios de **Azure OpenAI**.

### 1. El Nodo Servidor A2A (`football_debate_server.py`)
El servidor expone de forma pasiva a un agente conversacional. Su propósito es mantenerse a la escucha y emitir respuestas cuando un cliente externo inicie una comunicación.

*   **Infraestructura Web**: Utiliza **Starlette** (un framework asíncrono) gestionado mediante **Uvicorn**, exponiendo el servicio en el puerto local `5001`.
*   **Manifiesto del Agente (Agent Card)**: El servidor expone públicamente un contrato o metadatos técnicos (`AgentCard`). Esto habilita el paradigma de descubrimiento de servicios (*Service Discovery*).
*   **Delimitación del Comportamiento (System Prompt)**: El agente tiene inyectadas instrucciones sistémicas estrictas. Su directiva es actuar con la personalidad de un analista veterano, defendiendo tácticas históricas.
*   **A2AExecutor**: Intercepta la petición de red entrante, la empaqueta como una consulta válida para el modelo subyacente (LLM) y devuelve la respuesta estructurada de vuelta al cliente.

### 2. El Nodo Cliente A2A (`football_debate_client.py`)
El cliente es el nodo activo de la arquitectura. Se encarga de iniciar la simulación, generar la premisa del debate y orquestar la llamada de red hacia el servidor.

*   **Generación Local**: Instancia localmente a su propio agente ("Modern Football Analyst").
*   **Descubrimiento de Red (A2ACardResolver)**: Contacta al servidor para extraer el manifiesto (`AgentCard`) y validar que el "Historiador Clásico" está en línea.
*   **Invocación Remota y Recepción**: Transmite el debate al servidor y espera la resolución del modelo remoto.

### 3. Servidor MCP en Azure (`azure_mcp_server/`)
Este es un servidor compatible con el protocolo MCP (Model Context Protocol) hospedado en la nube usando **Azure Functions** y su extensión nativa `@app.mcp_tool_trigger`.
Ofrece tres herramientas remotas (tools) que pueden ser consumidas por cualquier cliente MCP (como la aplicación de escritorio Claude, Cline, o el MCP Inspector web):
1.  **analisis_tactico_avanzado**: Simula y analiza un partido entre dos equipos de fútbol.
2.  **buscar_wikipedia_futbol**: Busca en Wikipedia información sobre un equipo de fútbol.
3.  **obtener_noticias_equipo**: Busca las últimas noticias reales en internet sobre un equipo usando DuckDuckGo.

### 4. Cliente MCP de GitHub (`mcp/github_client.py`)
Un script local que demuestra cómo inicializar una sesión MCP como cliente para conectarse al servidor oficial `@modelcontextprotocol/server-github` vía `stdio`, permitiendo interactuar con repositorios y herramientas de GitHub.

---

## Requisitos Previos e Instalación

Para ejecutar este entorno distribuido, es necesario aislar las dependencias utilizando un entorno virtual de Python.

```bash
# 1. Crear y activar un entorno virtual (recomendado)
python -m venv .venv
# En Windows (Powershell):
.\.venv\Scripts\activate

# 2. Instalar las dependencias
pip install -r requirements.txt
pip install -r azure_mcp_server/requirements.txt
```

### Configuración de Credenciales (`.env`)
El archivo oculto `.env` en la raíz del proyecto debe contener:

```ini
# Azure OpenAI Settings
AZURE_OPENAI_ENDPOINT="https://<TU_RECURSO>.openai.azure.com/"
AZURE_OPENAI_API_KEY="<TU_API_KEY_AQUI>"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini"

# Azure Function Auth (Para testear el servidor MCP remoto)
AZURE_FUNCTION_KEY="<TU_MASTER_KEY_DE_LA_FUNCION_AQUI>"

# GitHub MCP Server
GITHUB_PERSONAL_ACCESS_TOKEN="<TU_TOKEN_DE_GITHUB>"

# A2A Configuration
A2A_AGENT_HOST="http://localhost:5001/"
```

---

## Instrucciones de Ejecución

### Probar el Debate A2A Local
1. En una terminal, ejecuta el servidor: `python football_debate_server.py`
2. En otra terminal, lanza el cliente: `python football_debate_client.py`

### Probar el Servidor MCP en Azure
El servidor MCP ya está desplegado en Azure Functions. Puedes interactuar con él usando el script de prueba local o la interfaz oficial del Inspector:

**Test Local mediante Script Python:**
```bash
cd azure_mcp_server
python test_azure_client.py
```

**Test visual mediante MCP Inspector (Interfaz Web):**
```bash
npx @modelcontextprotocol/inspector
```
*En la web que se abrirá, selecciona la pestaña "SSE" e introduce la URL de tu Azure Function terminada en `/runtime/webhooks/mcp/sse?code=TU_CLAVE`.*
