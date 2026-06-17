import asyncio
import sys
from mcp import ClientSession
from mcp.client.sse import sse_client

# Asegurar codificación utf-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

async def test():
    # URL del endpoint MCP de Azure Functions con la clave del sistema
    # El endpoint requiere autenticación: /runtime/webhooks/mcp/sse?code=<key>
    import os
    master_key = os.environ.get("AZURE_FUNCTION_KEY", "TU_CLAVE_AQUI")
    url = f"https://function-futbol-mcp.azurewebsites.net/runtime/webhooks/mcp/sse?code={master_key}"
    
    print("==========================================================")
    print(f" Conectando al servidor MCP en Azure...")
    print("==========================================================")
    
    try:
        async with sse_client(url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                print("\n[1] Inicializando sesión MCP...")
                await session.initialize()
                print("✅ Sesión inicializada con éxito.")
                
                print("\n[2] Obteniendo herramientas del servidor Azure...")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"🛠️  Herramienta: {tool.name}")
                    print(f"   Descripción: {tool.description}")
                
                print("\n[3] 🧠 Invocando 'analisis_tactico_avanzado' de manera remota...")
                print("Generando estadísticas reales en la nube para: Real Madrid vs Barcelona...")
                
                # Llamar a la herramienta de análisis táctico
                result = await session.call_tool(
                    "analisis_tactico_avanzado", 
                    {"equipo_a": "Real Madrid", "equipo_b": "Barcelona"}
                )
                
                print("\n📊 --- RESULTADO DESDE AZURE FUNCTION ---")
                print(result.content[0].text)
                print("-----------------------------------------\n")
                
    except Exception as e:
        import traceback
        print(f"\n❌ Error al conectar o ejecutar: {e}")
        traceback.print_exc()
        print("Tip: Verifica si la Azure Function ha terminado de arrancar (a veces tarda unos segundos el primer arranque).")

if __name__ == "__main__":
    asyncio.run(test())
