import pandas as pd
from fuzzywuzzy import fuzz, process # process might be useful later, fuzz is used now
import logging
from datetime import datetime, timedelta
import re # Import regex for vendor cleaning
import os

# Configure basic logging if not already configured elsewhere
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def read_csv(file_path):
    logging.debug(f"Reading CSV file: {file_path}")
    try:
        # Load CSV without initial date parsing
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_dir, '..', file_path)
        df = pd.read_csv(full_path)
        logging.debug(f"CSV DataFrame head before cleaning:\n{df.head()}")
        logging.debug(f"CSV DataFrame dtypes before cleaning:\n{df.dtypes}")

        # Attempt to convert 'date' column to datetime objects after loading
        # errors='coerce' will turn unparseable dates into NaT (Not a Time)
        if 'date' in df.columns:
            # Try multiple common date formats
            df['date'] = pd.to_datetime(df['date'], errors='coerce', infer_datetime_format=True)
        else:
            logging.warning("CSV file does not contain a 'date' column.")

        # Attempt to convert amount, coercing errors to NaN
        if 'amount' in df.columns:
            # Clean amount string before converting (remove currency symbols, commas)
            if df['amount'].dtype == 'object': # Only clean if it's a string type
                 df['amount'] = df['amount'].astype(str).str.replace(r'[$,€£¥]', '', regex=True).str.replace(',', '').str.strip()
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        else:
            logging.warning("CSV file does not contain an 'amount' column.")

        # Handle potential 'N/A' strings or similar placeholders in other columns if needed
        # Example for vendor: df['vendor'] = df['vendor'].replace(['N/A', 'na', ''], None)


        logging.debug(f"CSV DataFrame head after cleaning:\n{df.head()}")
        logging.debug(f"CSV DataFrame dtypes after cleaning:\n{df.dtypes}") # Check if 'date' is now datetime64[ns]
        return df
    except FileNotFoundError:
        logging.error(f"CSV file not found at {file_path}")
        return None
    except Exception as e:
        logging.error(f"Failed to read or process CSV {file_path}: {e}", exc_info=True)
        return None

def normalize_vendor(name):
    """Basic normalization for vendor names."""
    if not isinstance(name, str):
        return ""
    name = name.lower()
    # Remove common business suffixes (add more if needed)
    suffixes = ['inc', 'llc', 'ltd', 'corp', 'co', 'gmbh', 'bv', 'pty', 'sa', 'sas', 'sarl']
    # Use regex to remove suffixes if they appear as whole words at the end
    for suffix in suffixes:
        name = re.sub(r'\b' + suffix + r'\.?$', '', name).strip() # \b for word boundary, \.? for optional dot
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    # Replace multiple spaces with single space
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def calculate_match_score(row, invoice_data, date_tolerance_days=1, amount_tolerance=0.01):
    """
    Calculates match score between a CSV row (Pandas Series) and extracted invoice data (dict).
    Uses stricter matching for date and amount.
    """
    score = 0
    total_weight = 0

    # Increased weights for more reliable fields (Amount, Date)
    weights = {
        'date': 0.60,
        #'amount': 0.40,
        'currency': 0.5, # Currency is usually exact or missing
        'vendor': 0.35  # Vendor matching is inherently fuzzy
    }

    # --- 1. Date Comparison (Stricter) ---
    invoice_date_str = invoice_data.get('date') # Expecting 'YYYY-MM-DD' string or None
    csv_date = row.get('date') # Expecting datetime object or NaT

    invoice_date_obj = None
    if isinstance(invoice_date_str, str):
        try:
            # Handle potential 'N/A' strings explicitly
            if invoice_date_str.upper() == 'N/A':
                 invoice_date_obj = None
                 logging.debug("Invoice date is 'N/A', treating as missing.")
            else:
                 invoice_date_obj = datetime.strptime(invoice_date_str, '%Y-%m-%d')
        except ValueError:
            logging.warning(f"Could not parse invoice date string: '{invoice_date_str}'. Treating as missing.")
            invoice_date_obj = None
    elif invoice_date_str is not None: # Should ideally be string or None
         logging.warning(f"Unexpected invoice date type: {type(invoice_date_str)}. Treating as missing.")
         invoice_date_obj = None

    # Check if CSV date is valid (not NaT) AND invoice date was successfully parsed
    if pd.notna(csv_date) and invoice_date_obj is not None:
        try:
            # Compare dates within tolerance
            time_difference = abs(csv_date - invoice_date_obj)
            if time_difference <= timedelta(days=date_tolerance_days):
                date_score = 100 # Perfect match within tolerance
            else:
                # Optional: Penalize based on difference, or just give 0
                date_score = 0 # Outside tolerance
                # date_score = max(0, 100 - time_difference.days * 10) # Example penalty

            score += date_score * weights['date']
            total_weight += weights['date']
            logging.debug(f"Date comparison: CSV='{csv_date.strftime('%Y-%m-%d')}', Invoice='{invoice_date_obj.strftime('%Y-%m-%d')}', Diff='{time_difference}', Score={date_score}")
        except Exception as e:
             logging.error(f"Unexpected error during date comparison: CSV Date={csv_date}, Invoice Date Obj={invoice_date_obj}. Error: {e}", exc_info=True)

    # Log if skipping
    elif pd.notna(csv_date):
         logging.debug(f"Skipping date score: Invoice date missing or invalid (Data: {invoice_data.get('date')}) for CSV Date {csv_date.strftime('%Y-%m-%d')}")
    elif invoice_date_obj is not None:
         logging.debug(f"Skipping date score: CSV date missing or invalid (value: {row.get('date', 'N/A')}) for Invoice Date {invoice_date_obj.strftime('%Y-%m-%d')}")
    else:
         logging.debug("Skipping date score: Both CSV and Invoice dates are missing or invalid.")


    # --- 2. Amount Comparison (Numerical with Tolerance) ---
    # invoice_amount = invoice_data.get('amount') # Expecting float or None
    # csv_amount = row.get('amount') # Expecting float or NaN

    # # Handle potential "N/A" string in invoice amount if necessary
    # if isinstance(invoice_amount, str) and invoice_amount.upper() == 'N/A':
    #     invoice_amount = None
    #     logging.debug("Invoice amount is 'N/A', treating as missing.")

    # # Check if both amounts are valid numbers
    # if pd.notna(csv_amount) and invoice_amount is not None and isinstance(invoice_amount, (int, float)):
    #     try:
    #         if abs(csv_amount - invoice_amount) <= amount_tolerance:
    #             amount_score = 100 # Exact match within tolerance
    #         else:
    #             # Optional: Use fuzzy comparison as a fallback for slightly off numbers? Or just 0.
    #             # csv_amount_str = "{:.2f}".format(csv_amount)
    #             # invoice_amount_str = "{:.2f}".format(invoice_amount)
    #             # amount_score = fuzz.ratio(csv_amount_str, invoice_amount_str)
    #             amount_score = 0 # Keep it strict for now
    #         score += amount_score * weights['amount']
    #         total_weight += weights['amount']
    #         logging.debug(f"Amount comparison: CSV='{csv_amount:.2f}', Invoice='{invoice_amount:.2f}', Diff='{abs(csv_amount - invoice_amount):.2f}', Score={amount_score}")
    #     except Exception as e:
    #         logging.error(f"Unexpected error during amount comparison: CSV={csv_amount}, Invoice={invoice_amount}. Error: {e}", exc_info=True)
    # # Log skipping reasons
    # elif pd.notna(csv_amount):
    #      logging.debug(f"Skipping amount score: Invoice amount missing or invalid (value: {invoice_data.get('amount', 'N/A')}) for CSV Amount {csv_amount:.2f}")
    # elif invoice_amount is not None:
    #      logging.debug(f"Skipping amount score: CSV amount missing/invalid (value: {row.get('amount', 'N/A')}) for Invoice Amount {invoice_amount:.2f}")
    # else:
    #     logging.debug("Skipping amount score: Both CSV and Invoice amounts are missing or invalid.")


    # --- 3. Currency Comparison (Case-insensitive Exact Match) ---
    invoice_currency = invoice_data.get('currency') # String or None
    csv_currency = row.get('currency') # String or NaN/None

    # Handle potential "N/A" string
    if isinstance(invoice_currency, str) and invoice_currency.upper() == 'N/A':
        invoice_currency = None
        logging.debug("Invoice currency is 'N/A', treating as missing.")
    if isinstance(csv_currency, str) and csv_currency.upper() == 'N/A': # Handle in CSV too if possible
        csv_currency = None

    # Check if both currencies are present (not None/NaN)
    if pd.notna(csv_currency) and invoice_currency is not None and isinstance(invoice_currency, str) and invoice_currency:
        try:
            # Simple exact match (case-insensitive) is usually sufficient for currency
            csv_curr_str = str(csv_currency).upper().strip()
            inv_curr_str = invoice_currency.upper().strip()
            if csv_curr_str == inv_curr_str:
                currency_score = 100
            else:
                # Optional: Could use fuzzy match as fallback if needed, but likely indicates mismatch
                # currency_score = fuzz.ratio(csv_curr_str, inv_curr_str)
                 currency_score = 0
            score += currency_score * weights['currency']
            total_weight += weights['currency']
            logging.debug(f"Currency comparison: CSV='{csv_curr_str}', Invoice='{inv_curr_str}', Score={currency_score}")
        except Exception as e:
            logging.error(f"Unexpected error during currency comparison: CSV={csv_currency}, Invoice={invoice_currency}. Error: {e}", exc_info=True)
    # Log skipping reasons (optional, can be verbose)
    # ...


    # --- 4. Vendor Comparison (Normalized Fuzzy Match) ---
    invoice_vendor = invoice_data.get('vendor') # String or None
    csv_vendor = row.get('vendor') # String or NaN/None

    # Handle potential "N/A" string
    if isinstance(invoice_vendor, str) and invoice_vendor.upper() == 'N/A':
        invoice_vendor = None
        logging.debug("Invoice vendor is 'N/A', treating as missing.")

    # Check if both vendors are present (not None/NaN and not empty strings after potential cleaning)
    if pd.notna(csv_vendor) and invoice_vendor is not None and isinstance(invoice_vendor, str) and invoice_vendor:
        try:
            # Normalize both vendor names before comparison
            norm_csv_vendor = normalize_vendor(str(csv_vendor))
            norm_invoice_vendor = normalize_vendor(invoice_vendor)

            if norm_csv_vendor and norm_invoice_vendor: # Ensure they aren't empty after normalization
                # Using token_set_ratio is good for partial matches and different word order
                vendor_score = fuzz.token_set_ratio(norm_csv_vendor, norm_invoice_vendor)
                score += vendor_score * weights['vendor']
                total_weight += weights['vendor']
                logging.debug(f"Vendor comparison: Norm CSV='{norm_csv_vendor}', Norm Invoice='{norm_invoice_vendor}', Score={vendor_score} (Original CSV='{csv_vendor}', Invoice='{invoice_vendor}')")
            else:
                 logging.debug(f"Skipping vendor score: One or both vendors became empty after normalization (CSV: '{norm_csv_vendor}', Invoice: '{norm_invoice_vendor}')")

        except Exception as e:
            logging.error(f"Unexpected error during vendor comparison: CSV='{csv_vendor}', Invoice='{invoice_vendor}'. Error: {e}", exc_info=True)
    # Log skipping reasons (optional)
    # ...


    # --- Normalize final score ---
    if total_weight > 0:
        # Ensure score doesn't exceed 100 (can happen with rounding if all weights are used and scores are 100)
        final_score = min(100.0, score / total_weight)
        logging.debug(f"Row calculation finished. Final Score: {final_score:.2f} (Raw Score: {score:.2f}, Total Weight: {total_weight:.2f})")
        return round(final_score) # Return rounded score as integer
    else:
        logging.warning("Could not calculate score for row, total_weight is zero (all comparable fields were missing/invalid).")
        return 0

def find_matching_rows(df, invoice_data, threshold=70):
    """Finds matching rows and adds the match_score column."""
    logging.debug(f"Finding matching rows with invoice_data: {invoice_data}")
    if df is None or df.empty:
        logging.warning("DataFrame is empty or None, cannot find matches.")
        return pd.DataFrame() # Return empty DataFrame

    # Ensure invoice_data is not None
    if invoice_data is None:
        logging.warning("Invoice data is None, cannot calculate scores.")
        return pd.DataFrame()

    # Calculate scores using .apply
    # Wrap the lambda call in a try-except block to catch errors from calculate_match_score per row
    def safe_calculate_score(row, invoice_data):
        try:
            # Pass tolerances defined here (or make them global/configurable)
            return calculate_match_score(row, invoice_data, date_tolerance_days=1, amount_tolerance=0.01)
        except Exception as e:
            logging.error(f"Error calculating score for row: {row.to_dict()}. Error: {e}", exc_info=True)
            return 0 # Return 0 score if calculation fails for a row

    df['match_score'] = df.apply(lambda row: safe_calculate_score(row, invoice_data), axis=1)
    logging.debug(f"Match scores calculated (showing first 5):\n{df['match_score'].head()}")

    # Filter by threshold
    matching_df = df[df['match_score'] >= threshold].copy() # Use .copy() to avoid SettingWithCopyWarning
    logging.debug(f"Matching rows found (above threshold {threshold}):\n{matching_df}")

    # Sort by score descending to get best match first
    matching_df.sort_values(by='match_score', ascending=False, inplace=True)

    return matching_df

def get_matching_rows(file_path, invoice_data = {}, threshold=70):
    """Reads CSV, finds matching rows, includes score, and returns as list of dicts."""
    logging.info(f"Getting matching rows for file: {file_path} with invoice_data: {invoice_data}")
    df = read_csv(file_path)
    if df is None:
        return [] # Return empty list if CSV reading failed
    
    # Filter the df for the amount of the invoice.get('amount')
    try:
        # we drop the df where the value is None or empty
        df = df[df['amount'].notna()]
        # we drop the df where the value is None or empty
        df = df[df['amount'] != '']
        # we drop the df where the value is None or empty
        df = df[df['amount'] != 'None']
        # then we convert column amount to float if the type is not float
        df['amount'] = df['amount'].astype(float)

        # also ensure that the invoice_data.get('amount') is a float
        invoice_data['amount'] = float(invoice_data.get('amount'))

        df = df[df['amount'] == invoice_data.get('amount')]
    except:
        logging.warning("Could not filter for amount, continuing...")
        # return an empty dataframe with the same columns as the original dataframe
        return pd.DataFrame(columns=df.columns).to_dict(orient='records')

    matching_df = find_matching_rows(df, invoice_data, threshold)

    # Convert results (including score) to list of dictionaries
    results_list = matching_df.to_dict(orient='records')

    # Ensure date is stringified if it's still a timestamp object and not NaT
    for record in results_list:
        if 'date' in record:
            if pd.notna(record['date']) and isinstance(record['date'], pd.Timestamp):
                 record['date'] = record['date'].strftime('%Y-%m-%d')
            else: # Handle NaT or other non-timestamps by setting to None
                 record['date'] = None
        # Optional: Convert NaN amounts back to None for JSON friendliness
        if 'amount' in record and pd.isna(record['amount']):
            record['amount'] = None
        # Optional: Convert NaN vendors/currencies back to None
        if 'vendor' in record and pd.isna(record['vendor']):
            record['vendor'] = None
        if 'currency' in record and pd.isna(record['currency']):
            record['currency'] = None


    logging.info(f"Final matching rows results (count: {len(results_list)}): {results_list}")
    return results_list # Returns list of matching rows (dicts), including the 'match_score'
