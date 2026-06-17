import asyncio
import os
import sys

import httpx
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent
from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()

async def main():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    a2a_agent_host = os.getenv("A2A_AGENT_HOST", "http://localhost:5001/")
    
    if not all([endpoint, api_key, deployment]):
        print("Please configure AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_DEPLOYMENT_NAME in .env")
        return

    # Create Azure OpenAI client for the local agent (Modern Analyst)
    async_client = AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2025-03-01-preview"
    )
    
    chat_client = OpenAIChatClient(
        async_client=async_client,
        model=deployment
    )

    modern_instructions = """
    You are the Modern Football Analyst. You analyze football using contemporary tactics, 
    advanced metrics (xG, PPDA), high pressing, and the coaching styles of Pep Guardiola, 
    Jürgen Klopp, or modern tacticians. You focus on physical conditioning, positional play (Juego de Posición), 
    and tactical flexibility. 
    You are participating in a podcast debate. Provide a concise, highly analytical modern perspective.
    """

    modern_analyst = Agent(
        client=chat_client,
        name="Modern Football Analyst",
        instructions=modern_instructions
    )

    # User's question
    user_query = "¿Cómo le iría a la España de 2010 contra la Argentina de 2022?"
    print(f"🎙️ **[Host]**: Bienvenidos al Podcast de Debate Táctico. Hoy tenemos una gran pregunta:\n")
    print(f"   \"{user_query}\"\n")
    print("--------------------------------------------------------------------------------")

    print(f"🤖 **[{modern_analyst.name}]** está analizando la situación...\n")
    
    # 1. Get Modern Analyst response
    modern_response = await modern_analyst.run(user_query)
    print(f"**{modern_analyst.name}**: {modern_response.text}\n")
    print("--------------------------------------------------------------------------------")
    
    # 2. Connect to the Classic Historian via A2A
    print(f"🔌 Conectando con el Servidor A2A (Historiador Clásico) en {a2a_agent_host} ...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            resolver = A2ACardResolver(httpx_client=http_client, base_url=a2a_agent_host)
            agent_card = await resolver.get_agent_card()
            print(f"✅ Agente encontrado: {agent_card.name} - {agent_card.description}\n")

        async with A2AAgent(
            name=agent_card.name,
            description=agent_card.description,
            agent_card=agent_card,
            url=a2a_agent_host,
        ) as a2a_historian:
            
            # Formulate the prompt for the historian
            historian_prompt = f"""
            En nuestro podcast de debate de fútbol, el Analista Moderno acaba de decir esto sobre la siguiente pregunta: "{user_query}"
            
            Opinión del Analista Moderno:
            "{modern_response.text}"
            
            Como Historiador Clásico del Fútbol, responde directamente a su análisis. Rebate sus puntos utilizando ejemplos 
            de sistemas tácticos del pasado (como el Ajax de Cruyff o el Milan de Sacchi). ¿Estás de acuerdo con él o 
            crees que está equivocado? ¡Defiende el fútbol clásico!
            """
            
            print(f"🗣️ **[{agent_card.name}]** está respondiendo al debate...\n")
            
            # Get the A2A agent's response without streaming
            historian_response = await a2a_historian.run(historian_prompt)
            print(f"**{agent_card.name}**: {historian_response.text}\n")
            print("--------------------------------------------------------------------------------")
            print("🎙️ **[Host]**: ¡Excelente debate! Gracias a ambos expertos. ¡Hasta la próxima!")

    except httpx.ConnectError:
        print(f"❌ Error de conexión: No se pudo contactar al agente A2A en {a2a_agent_host}.")
        print("Asegúrate de que 'football_debate_server.py' esté ejecutándose en otra terminal.")

if __name__ == "__main__":
    asyncio.run(main())
