import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Alice's Test Dashboard", page_icon="✨")

st.title("✨ Alice's External Dashboard")
st.success("Wow! You successfully registered an external URL into the WeCarePeople Hub!")

st.write("Imagine this is a completely separate dashboard built by someone else on your team. It is running on an entirely different port (`8502`), but because of the Hub, it is seamlessly embedded here!")

# Add a fun dummy chart
df = pd.DataFrame({
    'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    'Awesome Points': [10, 25, 15, 40, 50]
})

fig = px.bar(df, x='Day', y='Awesome Points', title="Team Awesome Score")
st.plotly_chart(fig)

st.balloons()
