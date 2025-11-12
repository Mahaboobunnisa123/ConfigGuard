import streamlit as st
import yaml
import configparser
from configguard import compare_dicts, load_config
import json
import os

# Page configuration
st.set_page_config(
    page_title="ConfigGuard - Configuration Validator",
    page_icon="⚙️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        text-align: center;
        color: #555;
        margin-bottom: 30px;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📋 About")
    st.write("ConfigGuard helps you validate configuration consistency by comparing two files.")
    
    st.markdown("### 📦 Supported Formats:")
    st.write("• YAML (.yaml, .yml)")
    st.write("• INI (.ini)")
    
    st.markdown("### ✨ Features:")
    st.write("• Detects missing keys")
    st.write("• Finds extra keys")
    st.write("• Identifies mismatched values")
    st.write("• Download reports as text or JSON")
    
    st.markdown("---")
    st.markdown("**Created for:** Deployment Validation & Debugging")

# Main header
st.markdown('<p class="main-header">⚙️ ConfigGuard - Configuration Validator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Compare YAML/INI configuration files and identify inconsistencies</p>', unsafe_allow_html=True)

# Upload section with balanced columns
st.markdown("## 📁 Upload Configuration Files")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Configuration File 1 (Base)")
    file1 = st.file_uploader(
        "Choose first config file",
        type=['yaml', 'yml', 'ini'],
        key="file1",
        help="Upload your base configuration file"
    )
    if file1:
        st.success(f"✅ Loaded: {file1.name}")

with col2:
    st.markdown("### Configuration File 2 (Compare Against)")
    file2 = st.file_uploader(
        "Choose second config file",
        type=['yaml', 'yml', 'ini'],
        key="file2",
        help="Upload the configuration file to compare"
    )
    if file2:
        st.success(f"✅ Loaded: {file2.name}")

st.markdown("---")

# Comparison logic
if file1 and file2:
    try:
        # Save uploaded files temporarily
        with open("temp_file1.yaml", "wb") as f:
            f.write(file1.getbuffer())
        with open("temp_file2.yaml", "wb") as f:
            f.write(file2.getbuffer())
        
        # Load configurations
        config1 = load_config("temp_file1.yaml")
        config2 = load_config("temp_file2.yaml")
        
        # Compare
        report = compare_dicts(config1, config2)
        
        # Display metrics
        st.markdown("## 📊 Comparison Summary")
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            missing_count = len(str(report['missing_keys']))
            st.metric("Missing Keys", missing_count, delta=None)
        
        with metric_col2:
            extra_count = len(str(report['extra_keys']))
            st.metric("Extra Keys", extra_count, delta=None)
        
        with metric_col3:
            mismatch_count = len(str(report['mismatched_values']))
            st.metric("Mismatched Values", mismatch_count, delta=None)
        
        st.markdown("---")
        
        # Display detailed results in tabs
        st.markdown("## 🔍 Detailed Results")
        
        tab1, tab2, tab3 = st.tabs(["❌ Missing Keys", "➕ Extra Keys", "⚠️ Mismatched Values"])
        
        with tab1:
            if report['missing_keys']:
                st.json(report['missing_keys'])
            else:
                st.info("✅ No missing keys found")
        
        with tab2:
            if report['extra_keys']:
                st.json(report['extra_keys'])
            else:
                st.info("✅ No extra keys found")
        
        with tab3:
            if report['mismatched_values']:
                st.json(report['mismatched_values'])
            else:
                st.info("✅ No mismatched values found")
        
        st.markdown("---")
        
        # Download section
        st.markdown("## 💾 Download Report")
        
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            # Text format
            text_report = f"""ConfigGuard Comparison Report
================================

Missing Keys:
{report['missing_keys']}

Extra Keys:
{report['extra_keys']}

Mismatched Values:
{report['mismatched_values']}
"""
            st.download_button(
                label="📄 Download as TXT",
                data=text_report,
                file_name="configguard_report.txt",
                mime="text/plain"
            )
        
        with download_col2:
            # JSON format
            json_report = json.dumps(report, indent=2)
            st.download_button(
                label="📋 Download as JSON",
                data=json_report,
                file_name="configguard_report.json",
                mime="application/json"
            )
        
        # Clean up temp files
        os.remove("temp_file1.yaml")
        os.remove("temp_file2.yaml")
        
    except Exception as e:
        st.error(f"❌ Error comparing files: {str(e)}")
        st.exception(e)

else:
    # Example usage section when no files uploaded
    st.markdown("## 📚 Example Usage")
    
    example_col1, example_col2 = st.columns(2)
    
    with example_col1:
        st.markdown("### Sample File 1 (sample1.yaml)")
        st.code("""database:
  host: localhost
  port: 3306
  user: admin
  password: secret""", language="yaml")
    
    with example_col2:
        st.markdown("### Sample File 2 (sample2.yaml)")
        st.code("""database:
  host: localhost
  port: 5432
  user: admin
  engine: postgres""", language="yaml")
    
    st.info("👆 Upload two configuration files above to start comparison")
