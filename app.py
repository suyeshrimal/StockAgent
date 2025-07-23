import streamlit as st
from lang_graph.graph_llm import run_analysis  
# Set page config
st.set_page_config(page_title="Stock Advisor", layout="wide")

st.title("Stock Technical Advisor (LLM-Powered)")
st.markdown("Enter a stock symbol (e.g., **GBIME**, **AAPL**, **TSLA**) to generate technical analysis and a recommendation.")

# User input
symbol = st.text_input("Stock Symbol", value="GBIME", max_chars=10)

if st.button("Analyze"):
    with st.spinner("Analyzing stock... please wait..."):
        try:
            results = run_analysis(symbol.upper())

            st.success(f"Analysis for {symbol.upper()} completed!")

            # Technical Analysis
            st.subheader("Technical Analysis")
            st.markdown(results["technical"]["analysis"])

            # Recommendation
            st.subheader("Final Recommendation")
            st.markdown(results["recommendation"])

        except Exception as e:
            st.error(f"An error occurred during analysis:\n\n{str(e)}")
