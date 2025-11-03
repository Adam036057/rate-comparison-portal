import streamlit as st
import pandas as pd
import io
import os
import re

st.set_page_config(page_title="Rate Comparison Portal", layout="wide")

st.sidebar.title("📂 Portal Navigation")
page = st.sidebar.radio("Go to:", ["📊 Rate Comparison", "🧩 Smart Top Code Check", "🏢 Carrier-to-Carrier Comparison"])

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

# ======================================================
# 🏢 PAGE 3: CARRIER-TO-CARRIER COMPARISON
# ======================================================
elif page == "🏢 Carrier-to-Carrier Comparison":
    st.title("🏢 Carrier-to-Carrier Rate Comparison")
    st.markdown("**Compare rates across multiple carriers to find the cheapest and most expensive options!**")
    
    # Clear Results Button
    if st.button("🔄 Clear All & Reset", key="clear_page3"):
        st.rerun()
    
    st.markdown("---")
    st.subheader("📂 Upload Carrier Rate Files")
    st.info("💡 Upload 2-5 carrier files to compare rates side-by-side")
    
    # File uploaders for multiple carriers
    col1, col2 = st.columns(2)
    
    with col1:
        carrier1_file = st.file_uploader("📤 Carrier 1 File", type=["csv", "xlsx"], key="carrier1")
        carrier2_file = st.file_uploader("📤 Carrier 2 File", type=["csv", "xlsx"], key="carrier2")
        carrier3_file = st.file_uploader("📤 Carrier 3 File (Optional)", type=["csv", "xlsx"], key="carrier3")
    
    with col2:
        carrier4_file = st.file_uploader("📤 Carrier 4 File (Optional)", type=["csv", "xlsx"], key="carrier4")
        carrier5_file = st.file_uploader("📤 Carrier 5 File (Optional)", type=["csv", "xlsx"], key="carrier5")
    
    # Collect uploaded files
    carrier_files = []
    if carrier1_file:
        carrier_files.append(("Carrier 1", carrier1_file))
    if carrier2_file:
        carrier_files.append(("Carrier 2", carrier2_file))
    if carrier3_file:
        carrier_files.append(("Carrier 3", carrier3_file))
    if carrier4_file:
        carrier_files.append(("Carrier 4", carrier4_file))
    if carrier5_file:
        carrier_files.append(("Carrier 5", carrier5_file))
    
    if len(carrier_files) >= 2:
        st.success(f"✅ {len(carrier_files)} carrier file(s) uploaded successfully!")
        
        try:
            # Load all carrier dataframes
            carrier_data = []
            for label, file in carrier_files:
                df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
                df.columns = df.columns.str.strip()
                carrier_data.append((label, file.name, df))
            
            st.markdown("---")
            st.subheader("🔧 Configure Carrier Comparison")
            
            # Carrier Names and Column Selection
            st.markdown("#### 📝 Name Your Carriers & Select Columns")
            
            carrier_configs = []
            
            for idx, (default_label, filename, df) in enumerate(carrier_data):
                with st.expander(f"⚙️ Configure {default_label} ({filename})", expanded=(idx == 0)):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        carrier_name = st.text_input(
                            f"Carrier Name",
                            value=default_label,
                            key=f"name_{idx}"
                        )
                    
                    with col2:
                        code_col = st.selectbox(
                            "Code/Prefix Column",
                            df.columns,
                            key=f"code_{idx}"
                        )
                    
                    with col3:
                        rate_col = st.selectbox(
                            "Rate Column",
                            df.columns,
                            key=f"rate_{idx}"
                        )
                    
                    carrier_configs.append({
                        'name': carrier_name,
                        'code_col': code_col,
                        'rate_col': rate_col,
                        'df': df,
                        'filename': filename
                    })
            
            st.markdown("---")
            
            if st.button("🚀 Compare All Carriers", key="compare_carriers"):
                st.info(f"🔍 Comparing {len(carrier_configs)} carriers...")
                
                # Start with first carrier
                base_config = carrier_configs[0]
                result_df = base_config['df'][[base_config['code_col'], base_config['rate_col']]].copy()
                result_df.columns = ['Code', base_config['name']]
                
                # Convert rate to numeric
                result_df[base_config['name']] = pd.to_numeric(result_df[base_config['name']], errors='coerce')
                
                # Merge with other carriers
                for config in carrier_configs[1:]:
                    temp_df = config['df'][[config['code_col'], config['rate_col']]].copy()
                    temp_df.columns = ['Code', config['name']]
                    temp_df[config['name']] = pd.to_numeric(temp_df[config['name']], errors='coerce')
                    
                    result_df = pd.merge(
                        result_df,
                        temp_df,
                        on='Code',
                        how='inner'
                    )
                
                # Remove rows with any NaN values
                result_df = result_df.dropna()
                
                st.write(f"✅ Found **{len(result_df)}** common codes across all carriers")
                
                if len(result_df) > 0:
                    # Get carrier columns (all except 'Code')
                    carrier_cols = [col for col in result_df.columns if col != 'Code']
                    
                    # Find cheapest and most expensive for each code
                    result_df['Cheapest_Carrier'] = result_df[carrier_cols].idxmin(axis=1)
                    result_df['Min_Rate'] = result_df[carrier_cols].min(axis=1)
                    result_df['Most_Expensive_Carrier'] = result_df[carrier_cols].idxmax(axis=1)
                    result_df['Max_Rate'] = result_df[carrier_cols].max(axis=1)
                    result_df['Price_Difference'] = result_df['Max_Rate'] - result_df['Min_Rate']
                    result_df['Percentage_Difference'] = ((result_df['Max_Rate'] - result_df['Min_Rate']) / result_df['Min_Rate']) * 100
                    
                    # Calculate overall statistics
                    st.markdown("---")
                    st.markdown("### 📊 Overall Comparison Summary")
                    
                    # Count wins for each carrier
                    cheapest_counts = result_df['Cheapest_Carrier'].value_counts()
                    expensive_counts = result_df['Most_Expensive_Carrier'].value_counts()
                    
                    # Average rates
                    avg_rates = result_df[carrier_cols].mean().sort_values()
                    
                    # Display metrics
                    cols = st.columns(len(carrier_cols))
                    for idx, carrier in enumerate(carrier_cols):
                        with cols[idx]:
                            cheapest_win_count = cheapest_counts.get(carrier, 0)
                            expensive_count = expensive_counts.get(carrier, 0)
                            avg_rate = avg_rates.get(carrier, 0)
                            
                            st.metric(
                                label=f"🏢 {carrier}",
                                value=f"${avg_rate:.4f}",
                                delta=f"Cheapest: {cheapest_win_count} times"
                            )
                            st.caption(f"🔴 Most Expensive: {expensive_count} times")
                    
                    st.markdown("---")
                    
                    # Overall Winner
                    overall_winner = cheapest_counts.idxmax()
                    overall_loser = expensive_counts.idxmax()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.success(f"🏆 **Best Overall**: {overall_winner}")
                        st.caption(f"Has cheapest rate {cheapest_counts[overall_winner]} times out of {len(result_df)}")
                    
                    with col2:
                        st.error(f"💸 **Most Expensive**: {overall_loser}")
                        st.caption(f"Has highest rate {expensive_counts[overall_loser]} times out of {len(result_df)}")
                    
                    with col3:
                        avg_difference = result_df['Price_Difference'].mean()
                        st.info(f"💰 **Avg Price Difference**: ${avg_difference:.4f}")
                        st.caption(f"Average spread between cheapest & most expensive")
                    
                    st.markdown("---")
                    st.markdown("### 📋 Detailed Comparison Results")
                    
                    # Sort options
                    sort_option = st.selectbox(
                        "Sort results by:",
                        ["Price Difference (High to Low)", "Price Difference (Low to High)", "Code", "Percentage Difference"],
                        key="sort_carrier"
                    )
                    
                    if sort_option == "Price Difference (High to Low)":
                        result_df = result_df.sort_values('Price_Difference', ascending=False)
                    elif sort_option == "Price Difference (Low to High)":
                        result_df = result_df.sort_values('Price_Difference', ascending=True)
                    elif sort_option == "Code":
                        result_df = result_df.sort_values('Code')
                    elif sort_option == "Percentage Difference":
                        result_df = result_df.sort_values('Percentage_Difference', ascending=False)
                    
                    # Display results with formatting
                    st.dataframe(
                        result_df.style.format({
                            **{col: "${:.4f}" for col in carrier_cols},
                            'Min_Rate': "${:.4f}",
                            'Max_Rate': "${:.4f}",
                            'Price_Difference': "${:.4f}",
                            'Percentage_Difference': "{:.2f}%"
                        }).background_gradient(subset=carrier_cols, cmap='RdYlGn_r'),
                        height=400
                    )
                    
                    st.markdown("---")
                    st.markdown("### 📥 Download Options")
                    
                    # Filter options for download
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Download full comparison
                        csv_full = result_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label=f"📊 Download Full Comparison ({len(result_df)} codes)",
                            data=csv_full,
                            file_name="carrier_comparison_full.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Download only codes with significant difference (>10%)
                        significant_df = result_df[result_df['Percentage_Difference'] > 10].copy()
                        csv_significant = significant_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label=f"🔥 Download Significant Differences (>{len(significant_df)} codes, >10% diff)",
                            data=csv_significant,
                            file_name="carrier_comparison_significant_only.csv",
                            mime="text/csv"
                        )
                    
                    # Download carrier summary
                    summary_data = {
                        'Carrier': carrier_cols,
                        'Average_Rate': [avg_rates.get(c, 0) for c in carrier_cols],
                        'Cheapest_Count': [cheapest_counts.get(c, 0) for c in carrier_cols],
                        'Most_Expensive_Count': [expensive_counts.get(c, 0) for c in carrier_cols]
                    }
                    summary_df = pd.DataFrame(summary_data).sort_values('Average_Rate')
                    
                    csv_summary = summary_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📈 Download Carrier Summary",
                        data=csv_summary,
                        file_name="carrier_summary.csv",
                        mime="text/csv"
                    )
                    
                    st.success("✅ Carrier comparison completed successfully!")
                    
                else:
                    st.warning("⚠️ No common codes found across all carriers. Please check your data.")
        
        except Exception as e:
            st.error(f"❌ Error while processing: {e}")
            st.error(f"Debug info: {str(e)}")
    
    elif len(carrier_files) == 1:
        st.warning("⚠️ Please upload at least 2 carrier files to compare.")
    else:
        st.info("👆 Upload at least 2 carrier files above to begin comparison")

