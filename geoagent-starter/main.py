from agents.spatial_navigator import agent_executor
from tools.gis_operations import reproject

def run_geospatial_task(prompt_text: str):
    # The key "input" MUST match the {input} placeholder in your PromptTemplate
    try:
        response = agent_executor.invoke({
            "messages": [("user", "Check the CRS of data/new_meter_readings.geojson")]
        })
        
        final_message = response["messages"][-1]
        
        print("\n✅ AGENT RESPONSE:")
        print(final_message.content)
    except KeyError as e:
        print(f"❌ Error: Missing input key in dictionary: {e}")
    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    # Test it with a real GIS scenario
    reproject("./data/test_web_mercator.geojson", "EPSG:4326")
    # run_geospatial_task("Check the CRS of ./data/new_meter_readings.geojson and re-project to 4326 if needed.")