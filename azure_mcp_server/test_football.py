import asyncio
import os
import sys
from dotenv import load_dotenv

# Fix unicode output in Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure we can import the agent_framework if it's local
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from function_app import buscar_wikipedia_futbol, obtener_noticias_equipo, analisis_tactico_avanzado

async def main():
    print("==================================================")
    print("   TEST DEL SERVIDOR MCP (CONECTADO A INTERNET)   ")
    print("==================================================")
    
    equipo_a = "Bayer Leverkusen"
    equipo_b = "Atalanta"
    
    print(f"\n[1] Probando Búsqueda en Wikipedia de '{equipo_a}'...")
    wiki_res = await buscar_wikipedia_futbol(equipo_a)
    print(f"Respuesta:\n{wiki_res[:500]}...\n")
    
    print(f"\n[2] Probando Búsqueda de Noticias Reales de '{equipo_b}'...")
    noticias_res = await obtener_noticias_equipo(equipo_b)
    print(f"Respuesta:\n{noticias_res}\n")
    
    print(f"\n[3] 🧠 Ejecutando Agente LLM Interno para el análisis táctico...")
    print(f"El agente está leyendo internet sobre {equipo_a} vs {equipo_b} ahora mismo...")
    analisis = await analisis_tactico_avanzado(equipo_a, equipo_b)
    
    print("\n--- CONCLUSIÓN DEL AGENTE ---")
    print(analisis)
    print("-----------------------------\n")

if __name__ == "__main__":
    asyncio.run(main())
