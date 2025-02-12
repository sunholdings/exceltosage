import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import toml


 #Cargar el archivo secrets.toml
secrets = toml.load('.streamlit/secrets.toml')
# Cargar los secretos desde el archivo secrets.toml
try:
    username = st.secrets["auth"]["username"]
    password = st.secrets["auth"]["password"]
except KeyError:
    st.error("Could not load credentials. Make sure the secrets.toml file is configured correctly.")
    st.stop()

# Crear formulario de inicio de sesión
st.markdown("<h2 style='text-align: center; color: black;'>Sign In</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Please enter your credentials to continue</p>", unsafe_allow_html=True)

user_input = st.text_input("Username", placeholder="Enter your username")
pass_input = st.text_input("Password", type="password", placeholder="Enter your password")

# Verificar las credenciales
if user_input and pass_input:
    if user_input == username and pass_input == password:
        st.success("¡You have successfully logged in!")

        # Title of the application
        st.title("Excel File Converter to Sagex3")


        # Program description
        st.write("""
        This program helps you upload an Excel file with registration information and convert it, 
        giving it the proper format to adapt it to the Sagex3 database.
        """)

        # Sidebar for general options
        with st.sidebar:
            # Add the image at the top of the sidebar
            st.image("R.png", use_container_width=True)
            
            st.header("General Options")
            invoice_type = option_menu("Invoice Type", ["Invoice", "Credit Memo"], 
                                    icons=["file-earmark-text", "file-earmark-minus"], 
                                    menu_icon="cast", default_index=0,
                                    styles={
                                        "container": {"padding": "5px", "background-color": "#f0f0f0"},
                                        "icon": {"color": "orange", "font-size": "25px"}, 
                                        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                                        "nav-link-selected": {"background-color": "rgb(4, 196, 217)"}
                                    })
            
            tax_type = option_menu("Tax Type", ["Real Estate", "Business Personal Property", "Rent"], 
                                icons=["building", "briefcase", "house"], 
                                menu_icon="cast", default_index=0,
                                styles={
                                    "container": {"padding": "5px", "background-color": "#f0f0f0"},
                                    "icon": {"color": "orange", "font-size": "25px"}, 
                                    "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                                    "nav-link-selected": {"background-color": "rgb(4, 196, 217)"}
                                })
            
            payment_term_options = ["ACH", "CREDITCARD", "NET0", "NET10", "NET15", "NET20", "NET20ACH", "NET30", "NET30ACH", "NET60", "NET60ACH", "1STMO"]
            payment_term = option_menu("Payment Term", payment_term_options, 
                                    icons=["credit-card", "cash"], 
                                    menu_icon="cast", default_index=0,
                                    styles={
                                        "container": {"padding": "5px", "background-color": "#f0f0f0"},
                                        "icon": {"color": "orange", "font-size": "25px"}, 
                                        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                                        "nav-link-selected": {"background-color": "rgb(4, 196, 217)"}
                                    })


        # Load the accounts Excel file
        accounts_df = pd.read_excel("Accounts.xlsx", dtype=str)

        # Load the analytical dimensions Excel file
        analytical_df = pd.read_excel("Analytical.xlsx", dtype=str)

        # Load the brand codes Excel file
        brand_codes_df = pd.read_excel("Brands.xlsx", dtype=str)

        vendor_id_ab_df = pd.read_excel("VendorID_Rent_AB.xlsx", dtype=str)
        vendor_id_all_df = pd.read_excel("VendorID_Rent_All.xlsx", dtype=str)

        # Verify that the "Brand" column exists in brand_codes_df
        if "Brand" not in brand_codes_df.columns:
            st.error("The 'Brand' column was not found in the Brands.xlsx file.")
        else:
            # File uploader widget for the main Excel file
            uploaded_file = st.file_uploader("Choose an Excel file with registration information", type=["xlsx", "xls"])

            if uploaded_file is not None:
                # Read the main Excel file
                df = pd.read_excel(uploaded_file, dtype=str)  # Read everything as string to avoid format errors

                # Define the template structure in the correct order
                column_order = [
                    "Site", "Company", "Invoice type", "Document no.", "Accounting date", "BP", "Control",
                    "Source date", "Source document", "Currency", "Rate type", "Invoice number", "Pay-by",
                    "Pay-to BP address", "Due date basis", "Payment term", "Early discount/Late charge",
                    "Comments", "Tax rule", "1099 form", "1099 box", "Amt. Subject to 1099", "Line number",
                    "Site 2", "General accounts", "Amount Tax", "1099", "Comment", "Distribution", "Order Information",
                    "Dimension type code", "Analytical Dimension", "Dimension type code1", "Analytical Dimension1",
                    "Dimension type code2", "Analytical Dimension2", "Amount"
                ]
        #--------------------------------------------------------------------------------
                # Verify and process the "CODE" or "CO" column for "Site"
                if "CODE" in df.columns or "CO" in df.columns:
                    column_name = "CODE" if "CODE" in df.columns else "CO"
                    df["Site"] = df[column_name].copy()  # Make a copy of the column
                    missing_sites = df["Site"].isna().sum()  # Count empty values

                    if missing_sites > 0:
                        st.warning(f"⚠️ Missing data in the 'Site' column: {missing_sites} records.")

                    # Concatenate "S" at the beginning of each value in the "Site" column
                    df["Site"] = df["Site"].apply(lambda x: "S" + str(x) if pd.notna(x) else x)

                    # Move "Site" to the first position
                    df = df[["Site"] + [col for col in df.columns if col != "Site"]]
                else:
                    st.warning("⚠️ The 'CODE' or 'CO' column was not found in the file.")
        #--------------------------------------------------------------------------------
                # Copy the values from "Site" to "Site 2"
                df["Site 2"] = df["Site"]
        #--------------------------------------------------------------------------------
                # Verify and process the "CODE" or "CO" column for "Company"
                if "CODE" in df.columns or "CO" in df.columns:
                    column_name = "CODE" if "CODE" in df.columns else "CO"
                    df.rename(columns={column_name: "Company"}, inplace=True)  # Rename if necessary
                    missing_company = df["Company"].isna().sum()  # Count empty values

                    if missing_company > 0:
                        st.warning(f"⚠️ Missing data in the 'Company' column: {missing_company} records.")

                    # Move "Company" to the second position
                    cols = df.columns.tolist()
                    cols.remove("Company")
                    cols.insert(1, "Company")
                    df = df[cols]
                else:
                    st.warning("⚠️ The 'CODE' or 'CO' column was not found in the file.")
        #--------------------------------------------------------------------------------
                # Assign corresponding values in the "Invoice type" column
                if invoice_type == "Invoice":
                    df["Invoice type"] = "INV"
                elif invoice_type == "Credit Memo":
                    df["Invoice type"] = "CRM"
        #--------------------------------------------------------------------------------
                # Assign corresponding values in the "Tax Type" column
                if tax_type == "Real Estate":
                    prefix = "24RETAX-"
                elif tax_type == "Business Personal Property":
                    prefix = "24BPPTAX-"
                elif tax_type == "Rent":
                    # Get the current year and month
                    current_year = pd.Timestamp.now().year
                    current_month = pd.Timestamp.now().strftime('%b').upper()  # Get the month abbreviation in uppercase
                    prefix = f"{current_year}{current_month} RENT- "
        #--------------------------------------------------------------------------------
                # Verify and process the "Store #", "STORE #", "Store#", or "Upload Store" column for "Document no."
                store_column_found = False
                for possible_name in ["Store #", "STORE #", "Store#", "Upload Store"]:
                    if possible_name in df.columns:
                        df["Document no."] = df[possible_name].apply(lambda x: prefix + str(x) if pd.notna(x) else x)
                        store_column_found = True
                        break

                if not store_column_found:
                    st.warning("⚠️ None of the columns 'Store #', 'STORE #', 'Store#' or 'Upload Store' were found in the file.")

                # Handle duplicates in "Document no."
                if "Document no." in df.columns:
                    df["Document no."] = df["Document no."].astype(str)
                    duplicate_counts = df["Document no."].value_counts()
                    for doc_no, count in duplicate_counts.items():
                        if count > 1:
                            suffix = 0
                            for idx in df[df["Document no."] == doc_no].index:
                                df.at[idx, "Document no."] = f"{doc_no}{chr(65 + suffix)}"
                                suffix += 1
        #--------------------------------------------------------------------------------
                # Assign the selected value in the "Payment term" column
                df["Payment term"] = payment_term
        #--------------------------------------------------------------------------------
                # Verify and process the "Draft", "Draft ", "Due", or "Due " column for "Accounting date"
                date_column_found = False
                if "ACH" in payment_term:
                    for possible_name in ["Draft", "Draft "]:
                        if possible_name in df.columns:
                            df["Accounting date"] = pd.to_datetime(df[possible_name], errors="coerce").dt.strftime('%Y%m%d')
                            date_column_found = True
                            break
                    if not date_column_found:
                        st.warning("⚠️ The 'Draft' column was not found. When registering a payment with ACH, it is necessary to use the Draft Day.")
                else:
                    for possible_name in ["Draft", "Draft ", "Due", "Due "]:
                        if possible_name in df.columns:
                            df["Accounting date"] = pd.to_datetime(df[possible_name], errors="coerce").dt.strftime('%Y%m%d')
                            date_column_found = True
                            break
                    if not date_column_found:
                        st.warning("⚠️ None of the columns 'Draft', 'Draft ', 'Due', or 'Due ' were found in the file.")
                    elif "Draft" not in df.columns and "Draft " not in df.columns:
                        st.warning("⚠️ The 'Draft' column was not found. Using the 'Due' column instead.")
        #--------------------------------------------------------------------------------
                df["Control"] = "AP"
        #--------------------------------------------------------------------------------
                # Copy the values from "Accounting date" to "Source date"
                if "Accounting date" in df.columns:
                    df["Source date"] = df["Accounting date"]
        #-------------------------------------------------------------------------------- 
                # Copy the values from "Document no." to "Source document"
                if "Document no." in df.columns:
                    df["Source document"] = df["Document no."]
        #--------------------------------------------------------------------------------
                # Fill all cells in the "Currency" column with the value "USD"
                df["Currency"] = "USD"
        #--------------------------------------------------------------------------------
                df["Rate type"] = 1   
        #--------------------------------------------------------------------------------
                # Fill the "Invoice number" column according to the type of "Invoice type"
                if invoice_type == "Credit Memo":
                    df["Invoice number"] = "X3"
                else:
                    df["Invoice number"] = ""
        #--------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------     
            # Ask the user about the type of tax
                if tax_type in ["Real Estate", "Business Personal Property"]:
                    # Ask the user if they want to use the same BP (Vendor ID) for all records
                    use_same_bp = st.radio("Do you want to use the same BP (Vendor ID) for all records?", ("Yes", "No"))

                    if use_same_bp == "Yes":
                        # Ask the user to type the BP (Vendor ID) for all records
                        bp_value = st.text_input("Enter the BP (Vendor ID) for all records:")
                        df["BP"] = bp_value
                    else:
                        # Ask the user to type the BP (Vendor ID) for each record
                        df["BP"] = ""
                        for index, row in df.iterrows():
                            st.write(f"Please enter the BP (Vendor ID) for the following record:")
                            st.write(f"Store: {row['Store#']} of {row['BRAND']}")
                            st.write(f"Site: {row['Site']}, Company: {row['Company']}")
                            bp_value = st.text_input(f"Enter the BP (Vendor ID) for record {index + 1}:", key=f"bp_{index}")
                            df.at[index, "BP"] = bp_value

                elif tax_type == "Rent":
                    # Ask the user if the store is Applebee's
                    is_applebees = st.radio("Is the store Applebee's?", ("Yes", "No"))

                    unassigned_count = 0

                    if is_applebees == "Yes":
                        # Use the VendorID_Rent_AB DataFrame
                        for index, row in df.iterrows():
                            store_number = row["Store#"]
                            vendor_id_row = vendor_id_ab_df[vendor_id_ab_df["Store#"] == store_number]

                            if not vendor_id_row.empty:
                                vendor_id = vendor_id_row["Vendor_ID"].values[0]
                                df.at[index, "BP"] = vendor_id
                            else:
                                unassigned_count += 1
                    else:
                        # Use the VendorID_Rent_All DataFrame
                        for index, row in df.iterrows():
                            store_number = row["Store#"]
                            vendor_id_row = vendor_id_all_df[vendor_id_all_df["Store#"] == store_number]

                            if not vendor_id_row.empty:
                                vendor_id = vendor_id_row["Vendor ID"].values[0]
                                df.at[index, "BP"] = vendor_id
                            else:
                                unassigned_count += 1

                    if unassigned_count == 0:
                        st.success("All records have been assigned Vendor IDs successfully.")
                    else:
                        st.warning(f"{unassigned_count} records could not be assigned a Vendor ID. Please check the Store#.")
        #--------------------------------------------------------------------------------       
            # Copy the values from "Document no." to "Source document"
                if "BP" in df.columns:
                    df["Pay-by"] = df["BP"]
        #--------------------------------------------------------------------------------
            
                df["Pay-to BP address"] = "MAIN"
        #--------------------------------------------------------------------------------
                # Copy the values from "Source date" to "Due date basis"
                if "Source date" in df.columns:
                    df["Due date basis"] = df["Source date"]
        #--------------------------------------------------------------------------------
                # Ensure the "Early discount/Late charge" column is blank
                df["Early discount/Late charge"] = ""
        #--------------------------------------------------------------------------------
                # Verify and process the "Parcel", "Parcel ", "PARCEL", "Account", or "Account " column for "Comments"
                comment_columns = ["Parcel", "Parcel ", "PARCEL", "Account", "Account ", "Comments"]
                found_comment_column = False

                if tax_type == "Rent":
                    df["Comments"] = 0
                else:
                    for col in comment_columns:
                        if col in df.columns:
                            df["Comments"] = df[col]
                            found_comment_column = True
                            break

                    if not found_comment_column:
                        st.warning("⚠️ None of the columns 'Parcel', 'Parcel ', 'PARCEL', 'Account', or 'Account ' were found in the file, to substitute Comments.")
        #--------------------------------------------------------------------------------    
                # Set the "Tax rule" column to "NTX"
                df["Tax rule"] = "NTX"
        #--------------------------------------------------------------------------------
                # Ensure the "1099 form", "1099 box", and "Amt. Subject to 1099" columns are blank
                df["1099 form"] = ""
                df["1099 box"] = ""
                df["Amt. Subject to 1099"] = ""
        #--------------------------------------------------------------------------------
            # Ask the user if they want to use the same account for all records
                use_same_account = st.radio("Do you want to use the same account for all records?", ("Yes", "No"))

                # Define account options
                account_options = accounts_df["Account"].tolist()

                if use_same_account == "Yes":
                    # Ask the user to select the account for "General accounts"
                    selected_account = st.selectbox("Select the **GL Account** (General accounts):", account_options)
                    account_code = accounts_df.loc[accounts_df["Account"] == selected_account, "Debit"].values[0]
                    df["General accounts"] = account_code
                    st.success(f"Account {selected_account} is valid and has been added to all records.")
                else:
                    # Ask the user to select the account for each record
                    df["General accounts"] = ""
                    for index, row in df.iterrows():
                        st.write(f"Please select the account for the following record:")
                        st.write(f"Store: {row['Store #']} of {row['BRAND']}")
                        st.write(f"Site: {row['Site']}, Company: {row['Company']}")
                        selected_account = st.selectbox(f"Select the account for record {index + 1}:", account_options, key=index)
                        account_code = accounts_df.loc[accounts_df["Account"] == selected_account, "Debit"].values[0]
                        df.at[index, "General accounts"] = account_code
                        st.success(f"Account {selected_account} is valid for record {index + 1} and has been added.")
        #--------------------------------------------------------------------------------   
                # Verify and process the "Amount Paid", "Amount Paid ", or "Total Due" column for "Amount"
                amount_columns = ["Amount Paid", "Amount Paid ", "Total Due","Amount paid","Amount paid "]
                for col in amount_columns:
                    if col in df.columns:
                        df["Amount"] = df[col].astype(float).round(2)
                        break
        #--------------------------------------------------------------------------------
                if "Amount" in df.columns:
                    df["Amount Tax"] = df["Amount"]
                
        #--------------------------------------------------------------------------------   
                df["1099"] = ""
        #--------------------------------------------------------------------------------   
                if "Comments" in df.columns:
                    df["Comment"] = df["Comments"]
        #--------------------------------------------------------------------------------   
                df["Line number"] = 1   
        #--------------------------------------------------------------------------------
                df["Distribution"] = ""     
        #--------------------------------------------------------------------------------   
                df["Order Information"] = 1  
        #--------------------------------------------------------------------------------   
                df["Dimension type code"] = "SUB" 
        #--------------------------------------------------------------------------------   
                # Ask the user if they want to use the same analytical dimension for all records
                use_same_analytical = st.radio("Do you want to use the same Sub Account for all records?", ("Yes", "No"))

                # Define analytical dimension options
                analytical_options = analytical_df["Code"].tolist()

                if use_same_analytical == "Yes":
                    # Ask the user to select the analytical dimension for "Analytical Dimension"
                    selected_analytical = st.selectbox("Select the **Sub Account** (Analytical Dimension):", analytical_options)
                    if not analytical_df[analytical_df["Code"] == selected_analytical].empty:
                        analytical_code = analytical_df.loc[analytical_df["Code"] == selected_analytical, "Ad"].values[0]
                        df["Analytical Dimension"] = analytical_code
                        st.success(f"Sub Account {selected_analytical} is valid and has been added to all records.")
                    else:
                        st.warning(f"⚠️ The selected analytical dimension '{selected_analytical}' was not found in the file.")
                else:
                    # Ask the user to select the analytical dimension for each record
                    df["Analytical Dimension"] = ""
                    for index, row in df.iterrows():
                        st.write(f"Please select the analytical dimension for the following record:")
                        st.write(f"Store: {row['Store #']} of {row['BRAND']}")
                        st.write(f"Site: {row['Site']}, Company: {row['Company']}")
                        selected_analytical = st.selectbox(f"Select the analytical dimension for record {index + 1}:", analytical_options, key=f"analytical_{index}")
                        if not analytical_df[analytical_df["Code"] == selected_analytical].empty:
                            analytical_code = analytical_df.loc[analytical_df["Code"] == selected_analytical, "Ad"].values[0]
                            df.at[index, "Analytical Dimension"] = analytical_code
                            st.success(f"Sub Account {selected_analytical} is valid for record {index + 1} and has been added.")
                        else:
                            st.warning(f"⚠️ The selected analytical dimension '{selected_analytical}' was not found in the file.")
        #--------------------------------------------------------------------------------
                df["Dimension type code1"] = "CAT" 
        #--------------------------------------------------------------------------------
                # Fill the "Analytical Dimension1" column based on the "Brand" column
                brand_columns = ["Brand", "BRAND", "Brand "]
                found_brand_column = False
                for col in brand_columns:
                    if col in df.columns:
                        df["Analytical Dimension1"] = df[col].map(brand_codes_df.set_index("Brand")["Code"]).fillna("")
                        found_brand_column = True
                        break

                if not found_brand_column:
                    st.warning("⚠️ None of the columns 'Brand', 'BRAND', or 'Brand ' were found in the file.")
        #--------------------------------------------------------------------------------
                df["Dimension type code2"] = "LOC"
        #--------------------------------------------------------------------------------
                # Fill the "Analytical Dimension2" column with the values from "Store #", "STORE #", "Store#", or "Upload Store"
                store_columns = ["Store #", "STORE #", "Store#", "Upload Store"]
                for col in store_columns:
                    if col in df.columns:
                        df["Analytical Dimension2"] = df[col]
                        break
        #--------------------------------------------------------------------------------
                # Ensure the DataFrame has all required columns in the correct order
                # Ensure the DataFrame has all required columns in the correct order
                for col in column_order:
                    if col not in df.columns:
                        df[col] = np.nan  # Add missing columns with empty values

                df = df[column_order]  # Reorder columns

                # Display the processed DataFrame
                st.write("Processed DataFrame:")
                st.dataframe(df)

                # Save the modified file as CSV without column names
                output_path = "output.csv"  # Output path
                df.to_csv(output_path, index=False, header=False)

                st.success("✅ File processed successfully.")
                st.download_button(
                    label="Download processed file",
                    data=open(output_path, "rb").read(),
                    file_name="output.csv",
                    mime="text/csv"
                )
    else:
        st.error("Incorrect username or password.")
else:
    st.info("Please enter your credentials to continue.")
