import streamlit as st
import pandas as pd
import io
import os
import re

st.set_page_config(page_title="Rate Comparison Portal", layout="wide")

st.sidebar.title("📂 Portal Navigation")
page = st.sidebar.radio("Go to:", ["📊 Rate Comparison", "🧩 Smart Top Code Check"])

# ======================================================
# 📊 PAGE 1: RATE COMPARISON
# ======================================================
if page == "📊 Rate Comparison":
    st.title("📊 Rate Comparison Portal")

    old_file = st.file_uploader("📂 Upload OLD Rate File", type=["csv", "xlsx"])
    new_file = st.file_uploader("📂 Upload NEW Rate File", type=["csv", "xlsx"])

    if old_file and new_file:
        try:
            old_df = pd.read_csv(old_file) if old_file.name.endswith(".csv") else pd.read_excel(old_file)
            new_df = pd.read_csv(new_file) if new_file.name.endswith(".csv") else pd.read_excel(new_file)

            old_df.columns = old_df.columns.str.strip()
            new_df.columns = new_df.columns.str.strip()

            st.markdown("### 🔧 Select Columns to Compare")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**OLD File Columns**")
                old_code_col = st.selectbox("Select Code/Prefix Column (OLD)", old_df.columns, key="old_code")
                
            with col2:
                st.markdown("**NEW File Columns**")
                new_code_col = st.selectbox("Select Code/Prefix Column (NEW)", new_df.columns, key="new_code")
            
            st.markdown("---")
            st.markdown("### 📊 Select Rate Columns to Compare")
            st.markdown("*Select up to 3 rate pairs to compare*")
            
            # Rate pair 1
            col1, col2 = st.columns(2)
            with col1:
                old_rate1 = st.selectbox("OLD File - Rate 1", ["None"] + list(old_df.columns), key="old_rate1")
            with col2:
                new_rate1 = st.selectbox("NEW File - Rate 1", ["None"] + list(new_df.columns), key="new_rate1")
            
            # Rate pair 2
            col1, col2 = st.columns(2)
            with col1:
                old_rate2 = st.selectbox("OLD File - Rate 2 (Optional)", ["None"] + list(old_df.columns), key="old_rate2")
            with col2:
                new_rate2 = st.selectbox("NEW File - Rate 2 (Optional)", ["None"] + list(new_df.columns), key="new_rate2")
            
            # Rate pair 3
            col1, col2 = st.columns(2)
            with col1:
                old_rate3 = st.selectbox("OLD File - Rate 3 (Optional)", ["None"] + list(old_df.columns), key="old_rate3")
            with col2:
                new_rate3 = st.selectbox("NEW File - Rate 3 (Optional)", ["None"] + list(new_df.columns), key="new_rate3")

            if st.button("🚀 Compare Rates"):
                # Collect rate pairs
                rate_pairs = []
                if old_rate1 != "None" and new_rate1 != "None":
                    rate_pairs.append((old_rate1, new_rate1, "Rate 1"))
                if old_rate2 != "None" and new_rate2 != "None":
                    rate_pairs.append((old_rate2, new_rate2, "Rate 2"))
                if old_rate3 != "None" and new_rate3 != "None":
                    rate_pairs.append((old_rate3, new_rate3, "Rate 3"))
                
                if len(rate_pairs) == 0:
                    st.error("❌ Please select at least one rate pair to compare.")
                else:
                    st.markdown("---")
                    st.markdown("### 📈 Rate Comparison Results")
                    
                    for old_rate_col, new_rate_col, rate_name in rate_pairs:
                        st.markdown(f"#### 📊 {rate_name} Comparison: `{old_rate_col}` vs `{new_rate_col}`")
                        
                        # Prepare data for merging
                        old_subset = old_df[[old_code_col, old_rate_col]].copy()
                        new_subset = new_df[[new_code_col, new_rate_col]].copy()
                        
                        merged = pd.merge(
                            old_subset,
                            new_subset,
                            left_on=old_code_col,
                            right_on=new_code_col,
                            how="inner",
                            suffixes=("_old", "_new")
                        )
                        
                        # Calculate percentage change
                        merged["%_change"] = ((merged[f"{new_rate_col}_new"] - merged[f"{old_rate_col}_old"]) /
                                              merged[f"{old_rate_col}_old"]) * 100
                        
                        avg_change = merged["%_change"].mean()
                        
                        # Display summary
                        if avg_change > 0:
                            st.success(f"🟢 **{rate_name}**: New rates are on average **{avg_change:.2f}%** higher than Old rates.")
                        elif avg_change < 0:
                            st.warning(f"🔴 **{rate_name}**: New rates are on average **{abs(avg_change):.2f}%** lower than Old rates.")
                        else:
                            st.info(f"⚪ **{rate_name}**: No average change detected (0.00%).")
                        
                        st.markdown("---")

        except Exception as e:
            st.error(f"❌ Error while processing: {e}")

# ======================================================
# 🧩 PAGE 2: SMART TOP CODE CHECK (WITH COUNTS ✅) - NOW WITH PRE-LOADED EXCEL OPTION
# ======================================================
elif page == "🧩 Smart Top Code Check":
    st.title("🧩 Top Code Checker")
    
    # Clear Results Button
    if st.button("🔄 Clear All & Reset", key="clear_page2"):
        st.rerun()

    # ============== NEW: PRE-LOADED EXCEL OPTION ==============
    st.subheader("📂 Choose Your Top Codes Source")
    
    # Radio button to choose between upload or pre-loaded file
    top_file_option = st.radio(
        "Select Top Codes File Source:",
        ["📤 Upload New File", "📋 Use Pre-loaded Excel (dialer_top_counts_updated.xlsx)"],
        key="top_file_source"
    )
    
    # Initialize variables
    top_df = None
    top_file_name = ""
    
    # Handle file source selection
    if top_file_option == "📤 Upload New File":
        top_file = st.file_uploader("📂 Upload Top Codes File (CSV or Excel)", type=["csv", "xlsx"], key="top")
        if top_file:
            st.success(f"✅ Top Codes File Loaded: **{top_file.name}** ({top_file.size / 1024:.1f} KB)")
            top_df = pd.read_csv(top_file) if top_file.name.endswith(".csv") else pd.read_excel(top_file)
            top_file_name = top_file.name
            
    else:  # Use pre-loaded Excel
        # ⚠️ IMPORTANT: For deployment, this file needs to be included in your GitHub repo
        excel_path = "dialer_top_counts_updated.xlsx"  # Changed to relative path
        
        if os.path.exists(excel_path):
            try:
                top_df = pd.read_excel(excel_path)
                file_size = os.path.getsize(excel_path) / 1024
                top_file_name = "dialer_top_counts_updated.xlsx"
                st.success(f"✅ Pre-loaded Excel File Loaded: **{top_file_name}** ({file_size:.1f} KB)")
                
                # Show preview of the Excel file
                with st.expander("👀 Preview Your Excel Data (First 5 rows)"):
                    st.dataframe(top_df.head())
                    st.info(f"📊 Total rows in Excel: **{len(top_df)}** | Columns: **{len(top_df.columns)}**")
                    
            except Exception as e:
                st.error(f"❌ Error loading pre-loaded Excel file: {e}")
                st.warning("💡 Make sure the file path is correct and the Excel file is accessible.")
        else:
            st.error(f"❌ Pre-loaded Excel file not found at: `{excel_path}`")
            st.warning("💡 Please check the file path or use the upload option instead.")

    # Comparison file uploader (remains the same)
    comp_file = st.file_uploader("📂 Upload Comparison File (CSV or Excel)", type=["csv", "xlsx"], key="comp")
    
    # Show uploaded comparison file name
    if comp_file:
        st.success(f"✅ Comparison File Loaded: **{comp_file.name}** ({comp_file.size / 1024:.1f} KB)")

    # Process files if both are available
    if top_df is not None and comp_file is not None:
        try:
            comp_df = pd.read_csv(comp_file) if comp_file.name.endswith(".csv") else pd.read_excel(comp_file)

            st.subheader("🧠 Select Columns to Compare")
            
            # Display column selection
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**📋 {top_file_name} Columns**")
                top_col = st.selectbox("Top File – Area Code Column", top_df.columns, key="top_col_select")
                count_col = st.selectbox("Top File – Count Column", top_df.columns, key="count_col_select")
                
            with col2:
                st.markdown(f"**📂 {comp_file.name} Columns**")
                comp_col = st.selectbox("Comparison File – Area Code Column", comp_df.columns, key="comp_col_select")

            # Show column preview
            with st.expander("📊 Column Data Preview"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Top File Sample Data:**")
                    st.write(f"Area Code Column ({top_col}): {list(top_df[top_col].head(3))}")
                    st.write(f"Count Column ({count_col}): {list(top_df[count_col].head(3))}")
                with col2:
                    st.write("**Comparison File Sample Data:**")
                    st.write(f"Area Code Column ({comp_col}): {list(comp_df[comp_col].head(3))}")

            if st.button("✅ Run Exact 7-Digit Match"):
                st.info(f"🔍 Processing: **{top_file_name}** vs **{comp_file.name}**")
                
                def clean_code(x):
                    if pd.isna(x):
                        return ""
                    x = re.sub(r"[^\d]", "", str(x).strip())
                    return x[:7]

                top_df[top_col] = top_df[top_col].astype(str).map(clean_code)
                comp_df[comp_col] = comp_df[comp_col].astype(str).map(clean_code)
                
                st.write(f"📊 Top File: {len(top_df)} rows loaded")
                st.write(f"📊 Comparison File: {len(comp_df)} rows loaded")

                top_df = top_df[top_df[top_col].str.len() == 7]
                comp_df = comp_df[comp_df[comp_col].str.len() == 7]
                
                st.write(f"✅ After filtering (7-digit codes only):")
                st.write(f"   - Top File: {len(top_df)} valid rows")
                st.write(f"   - Comparison File: {len(comp_df)} valid rows")

                # ✅ FIX: Remove duplicates from top_df before creating sets
                top_df_unique = top_df[[top_col, count_col]].drop_duplicates(subset=[top_col]).reset_index(drop=True)
                
                st.write(f"🔍 Unique codes in Top File: {len(top_df_unique)}")
                
                # ✅ FIX: Convert to sets properly using .values for pandas Series
                top_codes = set(top_df_unique[top_col].values)
                comp_codes = set(comp_df[comp_col].unique())

                found = top_codes & comp_codes
                missing = top_codes - comp_codes

                st.markdown(f"""
                **📊 Smart Top Code Check Summary**
                ✅ Total Top Codes: {len(top_codes)}  
                🟢 Found in Comparison: {len(found)}  
                🔴 Missing in Comparison: {len(missing)}
                """)

                result_df = top_df_unique.copy()
                result_df["Status"] = result_df[top_col].apply(lambda x: "FOUND" if x in found else "MISSING")

                found_df = result_df[result_df["Status"] == "FOUND"].copy()
                missing_df = result_df[result_df["Status"] == "MISSING"].copy()

                # ✅ Download options (Found or Missing)
                st.subheader("📥 Download Options")
                
                # Extract base name from comparison file (without extension)
                comp_base_name = os.path.splitext(comp_file.name)[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    csv = missing_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label=f"🔴 Download Missing Codes ({len(missing_df)})",
                        data=csv,
                        file_name=f"{comp_base_name}_missing_codes.csv",
                        mime="text/csv"
                    )
                with col2:
                    csv2 = found_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label=f"🟢 Download Matched Codes ({len(found_df)})",
                        data=csv2,
                        file_name=f"{comp_base_name}_matched_codes.csv",
                        mime="text/csv"
                    )

                st.success("✅ Process completed successfully!")
                
                # Show results table
                st.subheader("📋 Results Preview")
                tab1, tab2, tab3 = st.tabs([f"🔍 All Results ({len(result_df)})", f"🟢 Found ({len(found_df)})", f"🔴 Missing ({len(missing_df)})"])
                
                with tab1:
                    st.dataframe(result_df.head(50))
                with tab2:
                    st.dataframe(found_df.head(50))
                with tab3:
                    st.dataframe(missing_df.head(50))

        except Exception as e:
            st.error(f"❌ Error while processing: {e}")
            st.error(f"Debug info: {str(e)}")

