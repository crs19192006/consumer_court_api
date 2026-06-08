import requests

BASE_URL = (
    "https://e-jagriti.gov.in/services/case/"
    "caseFilingService/v2/getCaseStatus"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Referer": "https://e-jagriti.gov.in/",
    "Origin": "https://e-jagriti.gov.in",
    "Accept": "application/json, text/plain, */*"
}


def build_params(search_value):
    search_value = search_value.strip()

    # Case Number
    if "/" in search_value:
        return {
            "caseNumber": search_value.upper()
        }

    # e-Daakhil Number
    if search_value.upper().startswith("A"):
        return {
            "fileApplicationNumber": search_value.upper()
        }

    # Filing Reference Number
    return {
        "filingReferenceNumber": search_value
    }


def get_case_status(search_value):
    params = build_params(search_value)

    response = requests.get(
        BASE_URL,
        params=params,
        headers=HEADERS,
        timeout=10
    )

    return response.json()


def search_by_party_name(
    name,
    commission_type_id,
    commission_id,
    filing_date1,
    filing_date2
):
    url = ("https://e-jagriti.gov.in/services/""report/report/getCauseTitleListByCompany")
    response = requests.get(
        url,
        params={
            "commissionTypeId": commission_type_id,
            "commissionId": commission_id,
            "filingDate1": filing_date1,
            "filingDate2": filing_date2,
            "complainant_respondent_name_en": name
        },
        headers=HEADERS,
        timeout=10
    )
    return response.json()


def get_all_states():
    url = (
        "https://e-jagriti.gov.in/services/report/report/"
        "getStateCommissionAndCircuitBench"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    return response.json()


def get_district_commissions(state_commission_id):
    url = (
        "https://e-jagriti.gov.in/services/report/report/"
        "getDistrictCommissionByCommissionId"
    )

    response = requests.get(
        url,
        params={
            "commissionId": state_commission_id
        },
        headers=HEADERS,
        timeout=10
    )

    return response.json()


def get_state_commission_id(state_name):
    states = get_all_states()

    for state in states["data"]:
        if state["commissionNameEn"].lower() == state_name.lower():
            return state["commissionId"]

    return None


def get_district_commission_id(state_name, district_name):
    state_commission_id = get_state_commission_id(state_name)

    if not state_commission_id:
        return None

    districts = get_district_commissions(
        state_commission_id
    )

    for district in districts["data"]:
        if (
            district["commissionNameEn"].lower()
            == district_name.lower()
        ):
            return district["commissionId"]

    return None