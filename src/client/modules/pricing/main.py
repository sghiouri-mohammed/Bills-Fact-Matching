import streamlit as st

def main():
    st.header("Pricing Calculator")
    
    # Input widgets
    col1, col2 = st.columns(2)
    with col1:
        rows = st.number_input("Number of rows in CSV file", min_value=0, max_value=1000000)
    with col2:
        images = st.number_input("Number of receipt images", min_value=0, max_value=1000)
    
    # Pricing calculations
    row_cost = rows * 0.01
    image_cost = images * 0.40
    
    # Apply discounts
    if rows > 300:
        row_cost *= 0.97  # 3% discount
    if images > 50:
        image_cost *= 0.50  # 50% discount
    
    # Display costs
    st.subheader("Cost Breakdown")
    col3, col4 = st.columns(2)
    with col3:
        st.metric("Row Processing Cost", f"€{row_cost:.2f}")
        st.metric("Image Processing Cost", f"€{image_cost:.2f}")
    with col4:
        st.metric("Total Cost", f"€{row_cost + image_cost:.2f}")
    
    # Pricing explanation
    st.subheader("Pricing Details")
    st.markdown("""
    - **Row Processing**: €0.01 per row
    - **Image Processing**: €0.40 per image
    - **Discounts**:
        - 3% discount on row processing for files with more than 300 rows
        - 50% discount on image processing for more than 50 images
    """)