import numpy as np
import pandas as pd
import streamlit as st
from mlxtend.frequent_patterns import apriori, association_rules

st.title("Association Rule Mining App (Apriori)")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    st.write("Raw Data")
    st.dataframe(df.head())

    st.write("Parameters")
    min_support = st.slider("Minimum Support", 0.01, 1.0, 0.2)
    min_confidence = st.slider("Minimum Confidence", 0.01, 1.0, 0.5)

    st.write("Preprocessing Data")
    if st.checkbox("Data already one-hot encoded"):
        basket = df
    else:
        transactions = df.iloc[:, 0].dropna().astype(str).apply(lambda x: x.split(","))
        all_items = sorted(set(item.strip() for sublist in transactions for item in sublist))
        basket = pd.DataFrame(0, index=range(len(transactions)), columns=all_items)

        for i, transaction in enumerate(transactions):
            for item in transaction:
                basket.loc[i, item.strip()] = 1

    st.dataframe(basket.head())

    st.write("Frequent Itemsets")
    frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True)
    st.dataframe(frequent_itemsets)

    st.write("Association Rules")
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)

    if not rules.empty:
        rules["rule"] = rules.apply(
            lambda row: f"{', '.join(row['antecedents'])} → {', '.join(row['consequents'])}",
            axis=1
        )

        st.dataframe(rules[["rule", "support", "confidence", "lift"]].sort_values(by="lift", ascending=False))
    else:
        st.warning("No rules found. Try lowering thresholds.")