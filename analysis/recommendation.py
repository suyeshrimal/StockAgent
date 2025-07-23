from langchain import PromptTemplate
from langchain.chains import LLMChain
from lang_graph.state import State

def generate_recommendation(state: State) -> State:
    """Node for final recommendation"""
    symbol = state["symbol"]
    llm = state["llm"]
    results = state["results"]

    prompt = PromptTemplate.from_template("""
            You are a financial analyst reviewing the technical analysis for stock symbol **{symbol}**.

            Technical Analysis:
            {technical}

            Based on this analysis, provide a final investment recommendation with the following structure:

            1. **Recommendation:** Choose one of [Strong Buy, Buy, Hold, Sell, Strong Sell].
            2. **Confidence Score:** A number from 0-100% representing how confident you are in this recommendation based on the technical indicators provided.
            3. **Key Reasons:** List 2-3 concise reasons supporting your recommendation.
            4. **Risk Factors:** Mention any known risks or uncertainties that could impact the outcome.
            5. **Target Price Range:** Provide a reasonable short-to-mid-term price range (e.g., over the next few weeks), based on the analysis.

            Make the output clear, structured, and suitable for a trader or investor making decisions.
            """)

    chain = LLMChain(llm=llm, prompt=prompt)
    final_recommendation = chain.run(
        symbol=symbol,
        technical=results["technical"]["analysis"],
    )

    state["results"]["recommendation"] = final_recommendation
    return state