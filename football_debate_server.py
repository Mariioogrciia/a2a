import os
import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface

from agent_framework import Agent
from agent_framework.a2a import A2AExecutor
from agent_framework.openai import OpenAIChatClient
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from starlette.applications import Starlette

load_dotenv()

def main():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([endpoint, api_key, deployment]):
        print("Please configure AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_DEPLOYMENT_NAME in .env")
        return

    # Create Azure OpenAI client
    async_client = AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2025-03-01-preview"
    )
    
    chat_client = OpenAIChatClient(
        async_client=async_client,
        model=deployment
    )

    public_agent_card = AgentCard(
        name="Classic Football Historian",
        description="A legendary football historian specializing in classic eras (Ajax's Cruyff, Sacchi's Milan, Brazil '70, etc.)",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[AgentInterface(url="http://localhost:5001/", protocol_binding="JSONRPC")],
        skills=[],
    )

    instructions = """
    Eres el "Historiador Clásico de Fútbol". Tienes un profundo conocimiento de la historia del fútbol, 
    particularmente de eras clásicas como el Ajax de Johan Cruyff, el AC Milan de Arrigo Sacchi y el Brasil de 1970.
    Cuando te hablen de equipos o tácticas modernas, debes rebatirlos agresivamente argumentando cómo los sistemas 
    clásicos eran superiores o cómo anularían a los modernos. Hablas con la autoridad, pasión y cierta arrogancia 
    de un analista veterano en un podcast de debate acalorado, convencido de que el fútbol ya se perfeccionó en el pasado.
    RESPONDE SIEMPRE EN ESPAÑOL. Sé directo, menciona a los jugadores o tácticas del otro analista y destrúyelos o compáralos.
    """

    agent = Agent(
        client=chat_client,
        name="Classic Football Historian",
        instructions=instructions,
    )

    request_handler = DefaultRequestHandler(
        agent_executor=A2AExecutor(agent),
        task_store=InMemoryTaskStore(),
        agent_card=public_agent_card,
    )

    server = Starlette(
        routes=[
            *create_agent_card_routes(public_agent_card),
            *create_jsonrpc_routes(request_handler, "/"),
        ]
    )

    print("Starting A2A Server (Classic Football Historian) on port 5001...")
    uvicorn.run(server, host="0.0.0.0", port=5001)

if __name__ == "__main__":
    main()
