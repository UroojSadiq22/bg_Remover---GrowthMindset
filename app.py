import streamlit as st
from rembg import remove
from PIL import Image
import io
import os
import datetime
import pandas as pd
from streamlit_cropper import st_cropper

# Set page config
st.set_page_config(page_title="Background Remover", page_icon="🖼️", layout="centered")

# ✅ Directory for storing history images
HISTORY_DIR = "history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

HISTORY_LOG_FILE = "history_log.txt"

# ✅ Function to log removals with proper image path
def log_removal(original_name, processed_filename):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HISTORY_LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp},{original_name},{processed_filename}\n")

# ✅ Function to load history from the log file
def load_removal_history():
    try:
        history_df = pd.read_csv(HISTORY_LOG_FILE, names=["Timestamp", "Original Image", "Processed Image"])
        return history_df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamp", "Original Image", "Processed Image"])

# ✅ UI Title
st.title("🖼️ Background Remover with History & Editing")

# ✅ Upload Image
uploaded_file = st.file_uploader("📂 Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Open Image
    image = Image.open(uploaded_file)

    # ✅ Image Editing Options
    st.subheader("🛠️ Edit Image Before Processing")
    col1, col2 = st.columns(2)

    with col1:
        rotate_angle = st.slider("Rotate Image (°)", -180, 180, 0)

    with col2:
        # ✅ Crop Image
        cropped_image = st_cropper(image, aspect_ratio=None, box_color='red', key="cropper")

    # ✅ Apply Rotation AFTER cropping
    if rotate_angle:
        cropped_image = cropped_image.rotate(rotate_angle)

    # ✅ Convert Image to Bytes
    image_bytes = io.BytesIO()
    cropped_image.save(image_bytes, format="PNG")

    # ✅ Remove Background
    output_bytes = remove(image_bytes.getvalue())

    # ✅ Convert Bytes to Image
    output_image = Image.open(io.BytesIO(output_bytes))

    # ✅ Generate a unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    processed_filename = f"{timestamp}_processed.png"
    processed_filepath = os.path.join(HISTORY_DIR, processed_filename)

    # ✅ Save Processed Image
    output_image.save(processed_filepath)

    # ✅ Log the removal
    log_removal(uploaded_file.name, processed_filename)

    # ✅ Display Images Side by Side
    col1, col2 = st.columns(2)

    with col1:
        st.image(cropped_image, caption="🖼️ Edited Image", use_container_width=True)

    with col2:
        st.image(output_image, caption="🎨 Background Removed", use_container_width=True)

    # ✅ Download Button
    output_buffer = io.BytesIO()
    output_image.save(output_buffer, format="PNG")
    st.download_button(
        label="📥 Download Image",
        data=output_buffer.getvalue(),
        file_name="background_removed.png",
        mime="image/png"
    )

# ✅ Sidebar: History Section
st.sidebar.subheader("📂 Your History Records")

if st.sidebar.button("📜 View History", use_container_width=True):
    history_df = load_removal_history()
    if not history_df.empty:
        st.sidebar.dataframe(history_df, height=300)
        
        # ✅ Show history images
        for _, row in history_df.tail(5).iterrows():  # Show last 5 images
            processed_image_path = os.path.join(HISTORY_DIR, row["Processed Image"])
            if os.path.exists(processed_image_path):
                st.sidebar.image(processed_image_path, caption=row["Processed Image"], use_container_width=True)

            # ✅ Download history as CSV
        st.sidebar.download_button("📥 Download History", history_df.to_csv(index=False), "removal_history.csv", use_container_width=True)
    else:
        st.sidebar.error("⚠️ No history found!")

# ✅ Clear History
if st.sidebar.button("🗑️ Clear History", use_container_width=True):
    if os.path.exists(HISTORY_LOG_FILE):
        open(HISTORY_LOG_FILE, "w").close()
    
    # ✅ Remove all images in history folder
    for file in os.listdir(HISTORY_DIR):
        os.remove(os.path.join(HISTORY_DIR, file))
    
    st.sidebar.success("✅ History cleared!")
    st.rerun()