import os
import pandas as pd
import streamlit as st

from product import ProductDescriptionOptimizer, DEFAULT_PROMPT

st.title("Product Description Optimizer")

api_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
instructions = st.text_area("LLM Instructions", value=DEFAULT_PROMPT, height=300)


uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None and st.button("Generate"):
    df = pd.read_csv(uploaded_file)


    optimizer = ProductDescriptionOptimizer(
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
        input_column=df.columns[0],


        output_column="Opdateret produkttekst",
        system_prompt=instructions,
    )

    progress_bar = st.progress(0)
    new_texts = []
    total_rows = len(df)
    for i, text in enumerate(df[optimizer.input_column]):
        new_texts.append(optimizer.generate_seo_text(text))
        progress_bar.progress(int((i + 1) / total_rows * 100))
    df[optimizer.output_column] = new_texts
    processed = df


    csv = processed.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Download updated CSV",
        csv,
        file_name="updated_products.csv",
        mime="text/csv",
    )


