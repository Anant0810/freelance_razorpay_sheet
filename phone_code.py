# Phone country code to country name mapping
PHONE_CODE_TO_COUNTRY = {
    # North America
    "1": "United States / Canada",
    
    # Europe
    "33": "France",
    "34": "Spain", 
    "39": "Italy",
    "41": "Switzerland",
    "43": "Austria",
    "44": "United Kingdom",
    "45": "Denmark",
    "46": "Sweden",
    "47": "Norway",
    "48": "Poland",
    "49": "Germany",
    
    # Asia Pacific
    "61": "Australia",
    "64": "New Zealand",
    "65": "Singapore",
    "66": "Thailand",
    "81": "Japan",
    "82": "South Korea",
    "84": "Vietnam",
    "86": "China",
    "91": "India",
    "92": "Pakistan",
    "93": "Afghanistan",
    "94": "Sri Lanka",
    "95": "Myanmar",
    "98": "Iran",
    
    # Middle East & Africa
    "20": "Egypt",
    "27": "South Africa",
    "30": "Greece",
    "31": "Netherlands",
    "32": "Belgium",
    "90": "Turkey",
    "212": "Morocco",
    "213": "Algeria",
    "216": "Tunisia",
    "218": "Libya",
    "220": "Gambia",
    "221": "Senegal",
    "222": "Mauritania",
    "223": "Mali",
    "224": "Guinea",
    "225": "Ivory Coast",
    "226": "Burkina Faso",
    "227": "Niger",
    "228": "Togo",
    "229": "Benin",
    "230": "Mauritius",
    "231": "Liberia",
    "232": "Sierra Leone",
    "233": "Ghana",
    "234": "Nigeria",
    "235": "Chad",
    "236": "Central African Republic",
    "237": "Cameroon",
    "238": "Cape Verde",
    "239": "São Tomé and Príncipe",
    "240": "Equatorial Guinea",
    "241": "Gabon",
    "242": "Republic of the Congo",
    "243": "Democratic Republic of the Congo",
    "244": "Angola",
    "245": "Guinea-Bissau",
    "246": "British Indian Ocean Territory",
    "248": "Seychelles",
    "249": "Sudan",
    "250": "Rwanda",
    "251": "Ethiopia",
    "252": "Somalia",
    "253": "Djibouti",
    "254": "Kenya",
    "255": "Tanzania",
    "256": "Uganda",
    "257": "Burundi",
    "258": "Mozambique",
    "260": "Zambia",
    "261": "Madagascar",
    "262": "Réunion / Mayotte",
    "263": "Zimbabwe",
    "264": "Namibia",
    "265": "Malawi",
    "266": "Lesotho",
    "267": "Botswana",
    "268": "Eswatini",
    "269": "Comoros",
    
    # Americas
    "52": "Mexico",
    "53": "Cuba",
    "54": "Argentina",
    "55": "Brazil",
    "56": "Chile",
    "57": "Colombia",
    "58": "Venezuela",
    "51": "Peru",
    "502": "Guatemala",
    "503": "El Salvador",
    "504": "Honduras",
    "505": "Nicaragua",
    "506": "Costa Rica",
    "507": "Panama",
    "508": "Saint Pierre and Miquelon",
    "509": "Haiti",
    "590": "Guadeloupe",
    "591": "Bolivia",
    "592": "Guyana",
    "593": "Ecuador",
    "594": "French Guiana",
    "595": "Paraguay",
    "596": "Martinique",
    "597": "Suriname",
    "598": "Uruguay",
    
    # Additional European codes
    "351": "Portugal",
    "352": "Luxembourg",
    "353": "Ireland",
    "354": "Iceland",
    "355": "Albania",
    "356": "Malta",
    "357": "Cyprus",
    "358": "Finland",
    "359": "Bulgaria",
    "360": "Hungary",
    "370": "Lithuania",
    "371": "Latvia",
    "372": "Estonia",
    "373": "Moldova",
    "374": "Armenia",
    "375": "Belarus",
    "376": "Andorra",
    "377": "Monaco",
    "378": "San Marino",
    "380": "Ukraine",
    "381": "Serbia",
    "382": "Montenegro",
    "383": "Kosovo",
    "385": "Croatia",
    "386": "Slovenia",
    "387": "Bosnia and Herzegovina",
    "389": "North Macedonia",
    
    # Additional Asian codes
    "60": "Malaysia",
    "62": "Indonesia",
    "63": "Philippines",
    "670": "East Timor",
    "672": "Norfolk Island",
    "673": "Brunei",
    "674": "Nauru",
    "675": "Papua New Guinea",
    "676": "Tonga",
    "677": "Solomon Islands",
    "678": "Vanuatu",
    "679": "Fiji",
    "680": "Palau",
    "681": "Wallis and Futuna",
    "682": "Cook Islands",
    "683": "Niue",
    "684": "American Samoa",
    "685": "Samoa",
    "686": "Kiribati",
    "687": "New Caledonia",
    "688": "Tuvalu",
    "689": "French Polynesia",
    "690": "Tokelau",
    "691": "Micronesia",
    "692": "Marshall Islands",
    
    # Russia and surrounding
    "7": "Russia / Kazakhstan",
    "992": "Tajikistan",
    "993": "Turkmenistan",
    "994": "Azerbaijan",
    "995": "Georgia",
    "996": "Kyrgyzstan",
    "998": "Uzbekistan"
}

def get_country_from_phone_code(code):
    """
    Get country name from phone country code.
    
    Args:
        code (str or int): Phone country code (with or without +)
    
    Returns:
        str: Country name or "Unknown country code" if not found
    """
    import re
    
    # Convert to string and remove + and leading zeros
    clean_code = re.sub(r'^\+?0*', '', str(code))
    
    # Try exact match first
    if clean_code in PHONE_CODE_TO_COUNTRY:
        return PHONE_CODE_TO_COUNTRY[clean_code]
    
    # Try matching longer codes by checking prefixes
    # Sort codes by length (longest first) for proper prefix matching
    sorted_codes = sorted(PHONE_CODE_TO_COUNTRY.keys(), key=len, reverse=True)
    
    for phone_code in sorted_codes:
        if clean_code.startswith(phone_code):
            return PHONE_CODE_TO_COUNTRY[phone_code]
    
    return "Unknown country code"

def get_phone_code_from_country(country_name):
    """
    Get phone country code from country name (reverse lookup).
    
    Args:
        country_name (str): Country name to search for
    
    Returns:
        str: Phone code with + prefix or "Country not found" if not found
    """
    normalized_input = country_name.lower().strip()
    
    for code, country in PHONE_CODE_TO_COUNTRY.items():
        normalized_country = country.lower()
        
        # Check for exact match, partial match, or if input contains first part of compound names
        if (normalized_country == normalized_input or 
            normalized_input in normalized_country or
            normalized_input in normalized_country.split('/')[0].strip()):
            return f"+{code}"
    
    return "Country not found"

def search_countries_by_partial_name(partial_name):
    """
    Search for countries by partial name match.
    
    Args:
        partial_name (str): Partial country name to search for
    
    Returns:
        list: List of tuples (phone_code, country_name) matching the partial name
    """
    results = []
    normalized_input = partial_name.lower().strip()
    
    for code, country in PHONE_CODE_TO_COUNTRY.items():
        normalized_country = country.lower()
        if normalized_input in normalized_country:
            results.append((f"+{code}", country))
    
    return results

def get_all_countries():
    """
    Get all available countries and their codes.
    
    Returns:
        dict: Dictionary mapping phone codes to country names
    """
    return {f"+{code}": country for code, country in PHONE_CODE_TO_COUNTRY.items()}

def display_countries_by_region():
    """
    Display countries grouped by region for reference.
    """
    regions = {
        "North America": ["1"],
        "Europe": ["33", "34", "39", "41", "43", "44", "45", "46", "47", "48", "49", 
                  "351", "352", "353", "354", "355", "356", "357", "358", "359", "360",
                  "370", "371", "372", "373", "374", "375", "376", "377", "378", "380",
                  "381", "382", "383", "385", "386", "387", "389", "30", "31", "32"],
        "Asia Pacific": ["60", "61", "62", "63", "64", "65", "66", "81", "82", "84", 
                        "86", "91", "92", "93", "94", "95", "98", "670", "672", "673",
                        "674", "675", "676", "677", "678", "679", "680", "681", "682",
                        "683", "684", "685", "686", "687", "688", "689", "690", "691", "692"],
        "Middle East & Africa": [str(i) for i in range(212, 270)] + ["20", "27", "90"],
        "Americas": ["51", "52", "53", "54", "55", "56", "57", "58"] + 
                   [str(i) for i in range(502, 510)] + [str(i) for i in range(590, 599)],
        "Russia & Former USSR": ["7", "992", "993", "994", "995", "996", "998"]
    }
    
    for region, codes in regions.items():
        print(f"\n=== {region} ===")
        for code in codes:
            if code in PHONE_CODE_TO_COUNTRY:
                print(f"+{code}: {PHONE_CODE_TO_COUNTRY[code]}")


import re
from typing import Optional, Tuple

# Phone country codes (sorted by length, longest first for proper matching)
PHONE_CODES = [
    # 4-digit codes
    "1242", "1246", "1264", "1268", "1284", "1340", "1345", "1441", "1473", "1649", 
    "1664", "1670", "1671", "1684", "1721", "1758", "1767", "1784", "1787", "1809", 
    "1829", "1849", "1868", "1869", "1876", "1939",
    
    # 3-digit codes
    "212", "213", "216", "218", "220", "221", "222", "223", "224", "225", "226", "227", 
    "228", "229", "230", "231", "232", "233", "234", "235", "236", "237", "238", "239", 
    "240", "241", "242", "243", "244", "245", "246", "248", "249", "250", "251", "252", 
    "253", "254", "255", "256", "257", "258", "260", "261", "262", "263", "264", "265", 
    "266", "267", "268", "269", "290", "291", "297", "298", "299", "350", "351", "352", 
    "353", "354", "355", "356", "357", "358", "359", "370", "371", "372", "373", "374", 
    "375", "376", "377", "378", "380", "381", "382", "383", "385", "386", "387", "389", 
    "420", "421", "423", "500", "501", "502", "503", "504", "505", "506", "507", "508", 
    "509", "590", "591", "592", "593", "594", "595", "596", "597", "598", "599", "670", 
    "672", "673", "674", "675", "676", "677", "678", "679", "680", "681", "682", "683", 
    "684", "685", "686", "687", "688", "689", "690", "691", "692", "850", "852", "853", 
    "855", "856", "880", "886", "960", "961", "962", "963", "964", "965", "966", "967", 
    "968", "970", "971", "972", "973", "974", "975", "976", "977", "992", "993", "994", 
    "995", "996", "998",
    
    # 2-digit codes
    "20", "27", "30", "31", "32", "33", "34", "36", "39", "40", "41", "43", "44", "45", 
    "46", "47", "48", "49", "51", "52", "53", "54", "55", "56", "57", "58", "60", "61", 
    "62", "63", "64", "65", "66", "81", "82", "84", "86", "90", "91", "92", "93", "94", 
    "95", "98",
    
    # 1-digit codes
    "1", "7"
]

def extract_phone_code(phone_number: Optional[str]) -> Tuple[Optional[str], str]:
    """
    Extract phone country code from a phone number with comprehensive error handling.
    
    Args:
        phone_number (Optional[str]): Phone number string (e.g., "+918637864927", "918637864927")
    
    Returns:
        Tuple[Optional[str], str]: A tuple containing:
            - Phone code with + prefix (e.g., "+91") or None if not found/error
            - Status message describing the result or error
    
    Examples:
        >>> extract_phone_code("+918637864927")
        ("+91", "Success")
        
        >>> extract_phone_code("918637864927")
        ("+91", "Success")
        
        >>> extract_phone_code(None)
        (None, "Error: Phone number is None")
        
        >>> extract_phone_code("123")
        (None, "Error: No valid phone code found")
    """
    try:
        # Handle None input
        if phone_number is None:
            return None, "Error: Phone number is None"
        
        # Handle non-string inputs
        if not isinstance(phone_number, str):
            try:
                phone_number = str(phone_number)
            except Exception as e:
                return None, f"Error: Cannot convert input to string - {str(e)}"
        
        # Handle empty string
        if not phone_number.strip():
            return None, "Error: Phone number is empty"
        
        # Clean the phone number - remove all non-digit characters except +
        cleaned_number = re.sub(r'[^\d+]', '', phone_number.strip())
        
        # Handle empty result after cleaning
        if not cleaned_number:
            return None, "Error: No digits found in phone number"
        
        # Remove leading + if present
        if cleaned_number.startswith('+'):
            number_without_plus = cleaned_number[1:]
        else:
            number_without_plus = cleaned_number
        
        # Handle too short numbers
        if len(number_without_plus) < 4:  # Minimum viable phone number length
            return None, "Error: Phone number too short"
        
        # Handle too long numbers (international standard max is around 15 digits)
        if len(number_without_plus) > 15:
            return None, "Error: Phone number too long"
        
        # Try to match phone codes (longest first)
        for code in PHONE_CODES:
            if number_without_plus.startswith(code):
                # Verify remaining digits form a reasonable phone number
                remaining_digits = number_without_plus[len(code):]
                if len(remaining_digits) >= 3:  # Minimum local number length
                    return f"+{code}", "Success"
        
        # If no code found, return error
        return None, "Error: No valid phone code found"
        
    except AttributeError as e:
        return None, f"Error: Invalid phone number format - {str(e)}"
    except Exception as e:
        return None, f"Error: Unexpected error occurred - {str(e)}"

def extract_phone_code_simple(phone_number: Optional[str]) -> Optional[str]:
    """
    Simplified version that returns only the phone code or None.
    
    Args:
        phone_number (Optional[str]): Phone number string
    
    Returns:
        Optional[str]: Phone code with + prefix or None if error/not found
    """
    result, _ = extract_phone_code(phone_number)
    return result

def validate_and_extract_phone_code(phone_number: Optional[str], 
                                   return_details: bool = False) :
    """
    Validate phone number and extract code with optional detailed error reporting.
    
    Args:
        phone_number (Optional[str]): Phone number to process
        return_details (bool): If True, returns tuple with code and status message
    
    Returns:
        Optional[str] or Tuple[Optional[str], str]: Phone code or tuple with details
    """
    if return_details:
        return extract_phone_code(phone_number)
    else:
        return extract_phone_code_simple(phone_number)
