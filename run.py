from src.main_app import main
import logging

from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.chains.graph_qa.base import GraphQAChain
from langchain.chains.flare.base import FlareChain

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    main()
    
#Key : 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