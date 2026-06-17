import os
import json
import asyncio
import azure.functions as func
from dotenv import load_dotenv

import wikipedia
from duckduckgo_search import DDGS

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI

load_dotenv()

# Configurar idioma de Wikipedia
wikipedia.set_lang("es")

app = func.FunctionApp()

# ============================================================================
# Tool 1: Buscar en Wikipedia sobre fútbol
# ============================================================================
@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="buscar_wikipedia_futbol",
    description="Busca en Wikipedia información sobre un equipo de fútbol, su historia o tácticas.",
    tool_properties='[{"propertyName": "consulta", "propertyType": "string", "description": "El término de búsqueda sobre fútbol (equipo, jugador, competición, etc.)"}]'
)
def buscar_wikipedia_futbol(context) -> str:
    request = json.loads(context)
    args = request.get("arguments", request) if isinstance(request, dict) else request
    consulta = args.get("consulta", "") if isinstance(args, dict) else ""
    try:
        resultados = wikipedia.search(consulta + " futbol club equipo")
        if not resultados:
            return json.dumps({"result": f"No se encontró nada en Wikipedia para: {consulta}"})
            
        pagina = wikipedia.page(resultados[0])
        return json.dumps({"result": f"Resumen de '{pagina.title}':\n{pagina.summary[:1500]}..."})
    except Exception as e:
        return json.dumps({"result": f"Error buscando en Wikipedia: {str(e)}"})


# ============================================================================
# Tool 2: Obtener noticias de un equipo
# ============================================================================
@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="obtener_noticias_equipo",
    description="Busca las últimas noticias reales en internet sobre un equipo usando DuckDuckGo.",
    tool_properties='[{"propertyName": "equipo", "propertyType": "string", "description": "El nombre del equipo de fútbol del que buscar noticias"}]'
)
def obtener_noticias_equipo(context) -> str:
    request = json.loads(context)
    args = request.get("arguments", request) if isinstance(request, dict) else request
    equipo = args.get("equipo", "") if isinstance(args, dict) else ""
    try:
        resultados = DDGS().news(equipo + " futbol", max_results=3)
        if not resultados:
            return json.dumps({"result": f"No hay noticias recientes para {equipo}."})
            
        noticias_str = f"Últimas noticias de {equipo}:\n"
        for r in resultados:
            noticias_str += f"- {r.get('title', 'Sin título')} ({r.get('source', 'Desconocido')}): {r.get('body', '')}\n"
        return json.dumps({"result": noticias_str})
    except Exception as e:
        return json.dumps({"result": f"Error buscando noticias: {str(e)}"})


# ============================================================================
# Tool 3: Análisis táctico avanzado con agente LLM
# ============================================================================
@app.mcp_tool_trigger(
    arg_name="context",
    tool_name="analisis_tactico_avanzado",
    description="Usa un Agente de IA interno y búsquedas en internet para analizar a fondo un partido entre dos equipos de fútbol. Genera estadísticas realistas y análisis táctico.",
    tool_properties='[{"propertyName": "equipo_a", "propertyType": "string", "description": "El nombre del primer equipo"}, {"propertyName": "equipo_b", "propertyType": "string", "description": "El nombre del segundo equipo"}]'
)
def analisis_tactico_avanzado(context) -> str:
    try:
        request = json.loads(context)
        args = request.get("arguments", request) if isinstance(request, dict) else request
        equipo_a = args.get("equipo_a", "") if isinstance(args, dict) else ""
        equipo_b = args.get("equipo_b", "") if isinstance(args, dict) else ""
        
        # Run the async logic synchronously since MCP tool triggers are sync
        try:
            result = asyncio.run(_analisis_tactico_async(equipo_a, equipo_b))
            return json.dumps({"result": result})
        except RuntimeError:
            # If there's already a running event loop, use nest_asyncio or create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _analisis_tactico_async(equipo_a, equipo_b))
                result = future.result()
            return json.dumps({"result": result})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return json.dumps({"result": f"Global Error in analisis_tactico_avanzado: {str(e)}\nTraceback: {tb}\nContext received: {context}"})


async def _analisis_tactico_async(equipo_a: str, equipo_b: str) -> str:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([endpoint, api_key, deployment]):
        return "Error: Faltan credenciales de Azure OpenAI en la configuración de la Function App."
        
    async_client = AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2025-03-01-preview"
    )
    
    chat_client = OpenAIChatClient(async_client=async_client, model=deployment)
    
    analista = Agent(
        client=chat_client,
        name="Analista Táctico Real",
        instructions=(
            "Eres un experto analista y simulador de partidos de fútbol. Tu tarea es predecir "
            "un partido entre dos equipos basándote en su historia y su actualidad. "
            "DEBES generar un cuadro de estadísticas finales del partido inventado pero extremadamente realista "
            "que incluya:\n"
            "- Resultado Final\n"
            "- Posesión (%)\n"
            "- Tiros Totales\n"
            "- Tiros a Puerta\n"
            "- Córners\n"
            "- Porcentaje de Pases Completados\n"
            "- Grandes Ocasiones\n"
            "- xG (Goles Esperados)\n\n"
            "Justifica brevemente estas estadísticas con un análisis táctico."
        )
    )
    
    # Obtener info real de Wikipedia y noticias
    info_a_wiki = _buscar_wikipedia_sync(equipo_a)
    info_b_wiki = _buscar_wikipedia_sync(equipo_b)
    info_a_noticias = _obtener_noticias_sync(equipo_a)
    info_b_noticias = _obtener_noticias_sync(equipo_b)
    
    prompt = f"""
    Simula un partido entre {equipo_a} y {equipo_b}.
    
    AUNQUE LOS DATOS DE ABAJO SEAN ERRORES O ESTÉN VACÍOS, ESTÁS OBLIGADO a generar la simulación usando EXACTAMENTE LOS NOMBRES: {equipo_a} y {equipo_b}. NO inventes otros equipos.
    
    Aquí tienes la información real extraída de internet:
    
    [DATOS DE {equipo_a.upper()}]
    Wikipedia: {info_a_wiki}
    Noticias Recientes: {info_a_noticias}
    
    [DATOS DE {equipo_b.upper()}]
    Wikipedia: {info_b_wiki}
    Noticias Recientes: {info_b_noticias}
    
    Genera el marcador final, las estadísticas completas del partido 
    (posesión, tiros, xG, pases, etc.) en un formato claro (como una tabla o lista) y añade un análisis táctico 
    explicando cómo se llegó a ese resultado.
    """
    
    try:
        respuesta = await analista.run(prompt)
        
        # Inyectamos los datos reales recopilados al final del resultado para que podamos debugear qué está pasando con las IPs de Azure
        debug_info = f"\n\n---\n**[DEBUG INFO - Datos extraídos desde Azure]**\n"
        debug_info += f"- **RAW CONTEXT**: {context}\n"
        debug_info += f"- **Wiki {equipo_a}**: {info_a_wiki[:100]}...\n"
        debug_info += f"- **Noticias {equipo_a}**: {info_a_noticias[:100]}...\n"
        debug_info += f"- **Wiki {equipo_b}**: {info_b_wiki[:100]}...\n"
        debug_info += f"- **Noticias {equipo_b}**: {info_b_noticias[:100]}...\n"
        
        return respuesta.text + debug_info
    except Exception as e:
        return f"Error ejecutando el análisis LLM: {str(e)}\nContext era: {context}"


def _buscar_wikipedia_sync(consulta: str) -> str:
    """Synchronous helper for Wikipedia search."""
    try:
        resultados = wikipedia.search(consulta + " futbol club equipo")
        if not resultados:
            return f"No se encontró nada en Wikipedia para: {consulta}"
        pagina = wikipedia.page(resultados[0])
        return f"Resumen de '{pagina.title}':\n{pagina.summary[:1500]}..."
    except Exception as e:
        return f"Error buscando en Wikipedia: {str(e)}"


def _obtener_noticias_sync(equipo: str) -> str:
    """Synchronous helper for news search."""
    try:
        resultados = DDGS().news(equipo + " futbol", max_results=3)
        if not resultados:
            return f"No hay noticias recientes para {equipo}."
        noticias_str = f"Últimas noticias de {equipo}:\n"
        for r in resultados:
            noticias_str += f"- {r.get('title', 'Sin título')} ({r.get('source', 'Desconocido')}): {r.get('body', '')}\n"
        return noticias_str
    except Exception as e:
        return f"Error buscando noticias: {str(e)}"
