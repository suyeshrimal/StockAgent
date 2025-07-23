from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from analysis.technical_analysis import technical_analysis
from analysis.recommendation import generate_recommendation
from langgraph.graph import StateGraph, START, END
from lang_graph.state import State
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

def create_analysis_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node("technical", technical_analysis)
    graph_builder.add_node("recommendation", generate_recommendation)

    # Define edges
    graph_builder.add_edge(START, "technical")
    graph_builder.add_edge("technical","recommendation")
    graph_builder.add_edge("recommendation", END)

    return graph_builder.compile()

class StockAdvisor:
    def __init__(self):
        self.llm = llm
        self.graph = create_analysis_graph()

    def analyze_stock(self, symbol):
        """Run complete stock analysis"""
        print(f"\nAnalyzing {symbol}")

        init_state: State = {
            "symbol": symbol,
            "llm": self.llm,
            "results": {}
        }

        final_state = self.graph.invoke(init_state)
        return final_state["results"]
    
def run_analysis(symbol: str):
    """Run stock analysis and print results"""
    advisor = StockAdvisor()
    results = advisor.analyze_stock(symbol)

    print(f"\n************* Stock Analysis Report for {symbol} **************")

    print("\n************* Technical Analysis **************")
    print(results["technical"]["analysis"])

    print("\n************* Final Recommendation **************")
    print(results["recommendation"])

    return results


run_analysis("SBL")