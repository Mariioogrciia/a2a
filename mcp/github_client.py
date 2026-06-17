import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

async def main():
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not github_token or github_token == "YOUR_GITHUB_TOKEN_HERE":
        print("Please configure GITHUB_PERSONAL_ACCESS_TOKEN in .env")
        return

    # Parámetros para iniciar el servidor MCP de GitHub a través de npx    
    server_params = StdioServerParameters(
        command="npx.cmd",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
    )

    print("Iniciando conexión con el servidor MCP de GitHub...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Inicializar la conexión
                await session.initialize()
                print("✅ Conexión establecida con éxito.\n")
                
                # Listar herramientas disponibles
                print("Herramientas disponibles en el servidor GitHub:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Error al conectar con el servidor MCP de GitHub: {e}")

if __name__ == "__main__":
    asyncio.run(main())
