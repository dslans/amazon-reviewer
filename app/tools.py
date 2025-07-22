
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from typing import Optional

websearch = DuckDuckGoSearchRun()
tools = [websearch]