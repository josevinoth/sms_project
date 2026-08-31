import os
import re
import pypdf


def extract_text_from_pdf(pdf_file_path):
    """
    Extract text content from a PDF file.
    """
    text = ""
    try:
        if not os.path.exists(pdf_file_path):
            return text
        
        reader = pypdf.PdfReader(pdf_file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_file_path}: {e}")
    return text


def clean_vehicle_no(veh_str):
    """
    Normalize vehicle number string for comparison (removes spaces, hyphens, uppercase).
    """
    if not veh_str:
        return ""
    return re.sub(r'[^A-Z0-9]', '', str(veh_str).upper())


def parse_eway_bill_pdf(pdf_file_path):
    """
    Parses an E-Way Bill PDF text and checks for:
    - Presence of Part-A (Invoice/Goods info)
    - Presence of Part-B (Vehicle/Transport details)
    - Extracted E-Way Bill Number
    - Extracted Vehicle Number(s) in Part-B
    """
    pdf_text = extract_text_from_pdf(pdf_file_path)
    text_upper = pdf_text.upper()

    res = {
        'has_part_a': False,
        'has_part_b': False,
        'eway_no': None,
        'vehicles_in_part_b': [],
        'goods_value': None,
        'raw_text': pdf_text
    }

    if not pdf_text:
        return res

    # 1. Check for E-Way Bill or Consolidated E-Way Bill identifier
    is_consolidated = "CONSOLIDATED E-WAY BILL" in text_upper or "CONSOLIDATED EWAY" in text_upper or "FORM EWB-02" in text_upper
    
    if "E-WAY BILL" in text_upper or "PART-A" in text_upper or "GSTIN OF SUPPLIER" in text_upper or is_consolidated:
        res['has_part_a'] = True

    # Extract all 12-digit E-Way Bill or Consolidated E-Way Bill numbers from PDF text
    all_ewbs = re.findall(r'\b(\d{12})\b', text_upper)
    all_ewbs_formatted = re.findall(r'\b(\d{4}\s*\d{4}\s*\d{4})\b', text_upper)
    
    combined_ewbs = set([re.sub(r'\s+', '', e) for e in all_ewbs + all_ewbs_formatted])
    res['all_ewb_numbers'] = list(combined_ewbs)

    eway_match = re.search(r'(?:CONSOLIDATED\s*)?E-WAY\s*BILL\s*(?:NO|NUMBER)?[:\s\n]*(\d{4}[\s\n]*\d{4}[\s\n]*\d{4}|\d{12})', text_upper)
    if not eway_match and combined_ewbs:
        res['eway_no'] = list(combined_ewbs)[0]
    elif eway_match:
        res['eway_no'] = re.sub(r'\s+', '', eway_match.group(1))

    # Extract Value of Goods from PDF
    val_match = re.search(r'VALUE\s*OF\s*GOODS[:\s\n]*(?:RS\.?|INR)?\s*([\d,]+(?:\.\d+)?)', text_upper)
    if val_match:
        try:
            res['goods_value'] = float(val_match.group(1).replace(',', ''))
        except ValueError:
            res['goods_value'] = None

    # 2. Check for Part-B (Vehicle details)
    # GST E-Way Bill Part-B headers or Consolidated EWB Vehicle headers
    part_b_keywords = ["PART-B", "VEHICLE DETAILS", "PART B", "TRANSPORT DETAILS", "MODE OF TRANSPORT", "CONSOLIDATED"]
    has_part_b_header = any(kw in text_upper for kw in part_b_keywords)

    # Regex for standard Indian vehicle numbers (handles standalone e.g. KA-51-AB-2578 or merged table text e.g. RoadKA51AB2578NARASAPURA)
    veh_pattern = r'([A-Z]{2}\s*[-]?\s*\d{1,2}\s*[-]?\s*[A-Z]{1,3}\s*[-]?\s*\d{4})'
    vehicles_found = re.findall(veh_pattern, text_upper)

    cleaned_vehicles = list(set([clean_vehicle_no(v) for v in vehicles_found if len(clean_vehicle_no(v)) >= 8]))

    # Part-B is confirmed ONLY if valid vehicle number(s) exist in Part-B
    if len(cleaned_vehicles) > 0:
        res['has_part_b'] = True
        res['vehicles_in_part_b'] = cleaned_vehicles
        res['is_consolidated'] = is_consolidated
    else:
        res['has_part_b'] = False

    return res


def validate_consignment_eway_bill(consignment_obj):
    """
    Validates a Consignment object against its uploaded E-Way Bill PDF:
    1. Checks if E-Way Bill attachment exists.
    2. Checks if Part-A & Part-B are present in PDF.
    3. Checks if Part-B Vehicle Number matches assigned vehicle number.

    Returns:
    (can_approve: bool, blocking_reasons: list of str, details: dict)
    """
    reasons = []
    details = {}

    from ..models import ConsignmentgoodsInfo

    # Fetch goods record for consignment
    goods_records = ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignment_obj)
    if not goods_records.exists():
        return True, [], {'info': 'No goods attached'}

    assigned_vehicle = clean_vehicle_no(consignment_obj.co_vehicelnumber)

    for goods in goods_records:
        if not goods.cg_ewaybill_att:
            reasons.append(f"Missing E-Way Bill PDF attachment for item (Invoice: {goods.cg_consignerinvoice or 'N/A'}).")
            continue

        file_path = goods.cg_ewaybill_att.path
        ext = os.path.splitext(file_path)[1].lower()

        if ext in ['.jfif', '.jpeg', '.jpg', '.png', '.bmp', '.webp']:
            reasons.append(
                "🛑 PDF UPLOAD REQUIRED: A photo scan (.jfif / .jpg) was uploaded. Even if Part-B is printed on paper, "
                "scanned images cannot be digitally verified by the system and carry a high risk of vehicle mismatch at GST check-posts. "
                "Please download the official E-Way Bill PDF directly from the GST Portal (https://ewaybillgst.gov.in) and upload the .pdf file."
            )
            continue

        parsed = parse_eway_bill_pdf(file_path)

        details['parsed'] = parsed

        if not parsed['has_part_a']:
            reasons.append("Uploaded document is not a valid E-Way Bill PDF or Part-A is unreadable.")
            continue

        if not parsed['has_part_b']:
            reasons.append(
                "🛑 CRITICAL REGULATORY RISK: Uploaded E-Way Bill contains ONLY Part-A! "
                "Part-B (Vehicle Details) is missing. Moving goods without Part-B attracts heavy GST fines (up to 100% tax penalty). "
                "Please update Part-B on the E-Way Bill portal and re-upload the completed PDF."
            )
            continue

        # E-Way Bill Number Match Check (Checks main EWB No or any individual EWB No in Consolidated PDF)
        software_ewb = str(goods.cg_ebillno or '').replace(' ', '').strip()
        pdf_ewb = str(parsed.get('eway_no') or '').replace(' ', '').strip()
        all_pdf_ewbs = parsed.get('all_ewb_numbers', [])

        ewb_matched = (software_ewb and (software_ewb == pdf_ewb or software_ewb in all_pdf_ewbs))

        if software_ewb and not ewb_matched:
            reasons.append(
                f"🛑 E-WAY BILL NUMBER MISMATCH: Entered E-Way Bill No '{goods.cg_ebillno}' does NOT match E-Way Bill No(s) in uploaded PDF ('{parsed.get('eway_no')}'). "
                "Please verify and correct the E-Way Bill Number before approving."
            )
            continue

        # Goods Value Match Check
        sw_val = goods.cg_consignervalue if (goods.cg_consignervalue is not None and goods.cg_consignervalue > 0) else (goods.cg_valueininr or 0.0)
        pdf_val = parsed.get('goods_value')
        if sw_val > 0 and pdf_val is not None and abs(sw_val - pdf_val) > 1.0:
            reasons.append(
                f"🛑 INVOICE VALUE MISMATCH: Entered Software Value '₹{sw_val:,.2f}' does NOT match Goods Value in E-Way Bill PDF ('₹{pdf_val:,.2f}'). "
                "Please correct the Invoice/Goods Value before approving."
            )
            continue

        # If assigned vehicle exists, check if Part-B contains matching vehicle
        if assigned_vehicle:
            if not parsed['vehicles_in_part_b']:
                reasons.append("Part-B vehicle details could not be verified in the uploaded E-Way Bill PDF.")
            elif assigned_vehicle not in parsed['vehicles_in_part_b']:
                found_veh_str = ", ".join(parsed['vehicles_in_part_b'])
                reasons.append(
                    f"🛑 VEHICLE MISMATCH: Assigned Vehicle '{consignment_obj.co_vehicelnumber}' does NOT match Part-B vehicle(s) in E-Way Bill PDF ({found_veh_str}). "
                    "Please update Part-B for the assigned vehicle before approving."
                )

    can_approve = len(reasons) == 0
    return can_approve, reasons, details
