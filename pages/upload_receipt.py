import streamlit as st
import pandas as pd
from datetime import datetime
import os
from app import process_receipt, categorize_items

st.sidebar.title("FinSight")
st.sidebar.page_link("app.py", label="Dashboard", icon="📊")
st.sidebar.page_link("pages/upload_receipt.py", label="Upload Receipt", icon="📄")
st.sidebar.page_link("pages/ai_insights.py", label="AI Insights", icon="💡")

st.title("📄 Upload Receipt")

def process_image(image_path):
    """Process the uploaded or captured image"""
    try:
        # Process the receipt
        items = process_receipt(image_path)
        if items:
            # Categorize items
            categorized_items = categorize_items(items)
            
            # Create a unique key for this batch of items
            batch_key = f"receipt_batch_{datetime.now().timestamp()}"
            
            # Store the batch in session state
            if 'receipt_batches' not in st.session_state:
                st.session_state.receipt_batches = {}
            
            st.session_state.receipt_batches[batch_key] = categorized_items
            
            # Display results
            st.success("Receipt processed successfully!")
            
            # Display data editor for the newly added items
            edited_df = st.data_editor(
                pd.DataFrame(categorized_items),
                column_config={
                    "Name": st.column_config.TextColumn("Name"),
                    "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                    "Date": st.column_config.DateColumn("Date"),
                    "Category": st.column_config.SelectboxColumn(
                        "Category",
                        options=["Groceries", "Snacks", "Household", "Subscriptions", "Other"]
                    ),
                    "Want or Need": st.column_config.SelectboxColumn(
                        "Want or Need",
                        options=["Want", "Need"]
                    )
                },
                num_rows="dynamic",
                key=batch_key
            )
            
            # Update the batch in session state with edited data
            st.session_state.receipt_batches[batch_key] = edited_df.to_dict('records')
            
            # Update the main receipts data
            st.session_state.receipts_data = []
            for batch in st.session_state.receipt_batches.values():
                st.session_state.receipts_data.extend(batch)
            
            # Clean up temporary file
            os.remove(image_path)
        else:
            st.error("No items found in the receipt. Please try again with a clearer image.")
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        # Clean up temporary file even if there's an error
        if os.path.exists(image_path):
            os.remove(image_path)

# Create tabs for different upload methods
upload_method = st.radio("Choose upload method:", ["File Upload", "Camera"])

if upload_method == "File Upload":
    uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp_receipt.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())
        process_image("temp_receipt.jpg")
else:
    # Camera input
    img_file_buffer = st.camera_input("Take a picture of your receipt")
    if img_file_buffer is not None:
        # Save the captured image temporarily
        with open("temp_receipt.jpg", "wb") as f:
            f.write(img_file_buffer.getbuffer())
        process_image("temp_receipt.jpg")

# Display all receipts in a single editor if there are any
if st.session_state.receipts_data:
    # Count unique receipts (assuming each receipt has at least one item)
    receipt_count = len(st.session_state.receipt_batches) if 'receipt_batches' in st.session_state else 1
    
    if receipt_count > 1:
        st.subheader("All Receipts")
        all_receipts_df = st.data_editor(
            pd.DataFrame(st.session_state.receipts_data),
            column_config={
                "Name": st.column_config.TextColumn("Name"),
                "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "Date": st.column_config.DateColumn("Date"),
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    options=["Groceries", "Snacks", "Household", "Subscriptions", "Other"]
                ),
                "Want or Need": st.column_config.SelectboxColumn(
                    "Want or Need",
                    options=["Want", "Need"]
                )
            },
            num_rows="dynamic",
            key="all_receipts_editor"
        )
        
        # Update session state with all edited data
        st.session_state.receipts_data = all_receipts_df.to_dict('records') 