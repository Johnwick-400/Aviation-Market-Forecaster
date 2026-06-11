import asyncio
import os
import glob
import shutil
from langchain_ollama import ChatOllama
from pydantic import ConfigDict
from browser_use import Agent

class PatchedChatOllama(ChatOllama):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
    
    @property
    def provider(self):
        return "ollama"
        
    @property
    def model_name(self):
        return self.model

async def main():
    print("Initializing browser-use with local Qwen2.5-Coder model...")
    
    # Initialize the patched LLM
    llm = PatchedChatOllama(model="qwen2.5-coder:7b", temperature=0.0)
    
    task = (
        "Navigate to https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FMF . "
        "Find the field checkboxes on the page. "
        "Make sure the checkboxes next to 'PASSENGERS', 'ORIGIN', 'DEST', 'YEAR', and 'MONTH' are checked. "
        "Click the button labeled 'Download'. "
        "Wait 15 seconds for the download to finish."
    )
    
    agent = Agent(task=task, llm=llm)
    
    try:
        await agent.run()
    except Exception as e:
        print(f"Agent encountered an error: {e}")
    finally:
        print("Browser execution finished.")

if __name__ == "__main__":
    asyncio.run(main())
    
    downloads = os.path.expanduser("~/Downloads")
    files = glob.glob(os.path.join(downloads, "*.csv"))
    
    if files:
        latest = max(files, key=os.path.getctime)
        dest = "/home/pavan_veesam/poc-main/market-forecaster/data/raw/bts_t100.csv"
        shutil.move(latest, dest)
        print(f"✅ Successfully moved downloaded dataset {latest} to {dest}")
    else:
        print("⚠️ No CSV found in ~/Downloads.")