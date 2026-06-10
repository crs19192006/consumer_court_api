from unittest import case
from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

from client import (
    get_case_status,
    get_case_details,
    search_by_party_name,
    get_all_states,
    get_district_commissions,
    get_state_commission_id,
    get_district_commission_id,
    get_cause_list
)

# --------------------------------------------------
# FastAPI App Configuration
# --------------------------------------------------

app = FastAPI(
    title="Consumer Court API",
    description="Consumer Court Search API built using e-Jagriti endpoints",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Home Endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Consumer Court API Running"
    }



# Case Status Search
@app.get("/case-status")
def case_status(search_value: str):
    details = get_case_details(search_value)

    if not details.get("data"):
        return {
            "success": False,
            "message": "Case not found"
        }
    
    case = details["data"][0]

    filing_date = datetime.strptime(case["filingDate"],"%d-%m-%Y")
    days_since_filing = (datetime.now() - filing_date).days

    state = case.get("statename", "").strip()
    district = case.get("commissionname")

    if district == "NCDRC":
        state = None
        district = None

    elif district == state:
        district = None

    formatted = {
        "serial_number": 1,
        "complaint_number":case.get("masterCase"),
        "party_1":case.get("complainantName"),
        "party_2":case.get("respondentName"),
        "state":state,
        "district":district,
        "complaint_details":case.get("caseCategoryNameEn"),
        "next_hearing_date":case.get("dtofnexthearing"),
        "status_of_case":case.get("caseStageNameEn"),
        "days_since_filing":days_since_filing
    }

    return {
        "success": True,
        "data": formatted
    }


# Party Search
@app.get("/party-search")
def party_search(
    type: str,
    name: str,
    state: str = None,
    district: str = None
):
    filing_date1 = "2000-01-01"
    filing_date2 = "2035-12-31"

    # National Commission Search
    if type.lower() == "ncdrc":
        commission_type_id = 1
        commission_id = 11000000

    # State Commission Search
    elif type.lower() == "scdrc":

        if not state:
            return {
                "success": False,
                "message": "state is required for scdrc"
            }
        commission_type_id = 2
        commission_id = get_state_commission_id(state)

        if not commission_id:
            return {
                "success": False,
                "message": "state not found"
            }

    # District Commission Search
    elif type.lower() == "dcdrc":

        if not state:
            return {
                "success": False,
                "message": "state is required for dcdrc"
            }

        if not district:
            return {
                "success": False,
                "message": "district is required for dcdrc"
            }

        commission_type_id = 3
        commission_id = get_district_commission_id(state,district)

        if not commission_id:
            return {
                "success": False,
                "message": "district not found"
            }

    # Invalid Type
    else:
        return {
            "success": False,
            "message": "type must be ncdrc, scdrc or dcdrc"
        }

    search_results = search_by_party_name(name,commission_type_id,commission_id,
                                          filing_date1,filing_date2)
    
    state_value = state
    district_value = district

    if type.lower() == "ncdrc":
        state_value = None
        district_value = None

    elif type.lower() == "scdrc":
        district_value = None

    formatted = []
    for index, case in enumerate(search_results, start=1):

        filing_date = datetime.strptime(case["case_filing_date"],"%Y-%m-%d")
        days_since_filing = (datetime.now() - filing_date).days

        formatted.append({
        "serial_number": index,
        "complaint_number":case.get("case_number"),
        "party_1":case.get("complainant_name"),
        "party_2":case.get("respondent_name"),
        "state":state_value,
        "district":district_value,
        "complaint_details":case.get("case_category_name"),
        "next_hearing_date":case.get("date_of_next_hearing"),
        "status_of_case":case.get("case_stage_name"),
        "days_since_filing":days_since_filing
    })

    return {
        "success": True,
        "total_results": len(formatted),
        "data": formatted
    }

# Returns all State Commissions
@app.get("/states", include_in_schema=False)
def states():
    return get_all_states()


# Returns District Commissions
@app.get("/districts/{state_commission_id}", include_in_schema=False)
def districts(state_commission_id: int):
    return get_district_commissions(state_commission_id)

# Returns Districts using State Name
@app.get("/districts-by-state", include_in_schema=False)
def districts_by_state(state: str):
    state_commission_id = get_state_commission_id(state)

    if not state_commission_id:
        return {
            "success": False,
            "message": "State not found"
        }

    return get_district_commissions(state_commission_id)


@app.get("/cause-list")
def cause_list(
    type: str,
    state: str = None,
    district: str = None,
    bench: int = None
):
    
    # National Commission
    if type.lower() == "ncdrc":
        commission_id = 11000000
        if bench:
            cause_list_data = get_cause_list(commission_id,bench)
        else:
            cause_list_data = []
            for bench_no in [1, 2, 3, 4, 5, 6]:
                try:
                    data = get_cause_list(commission_id,bench_no)
                    cause_list_data.extend(data)
                except Exception as e:
                    pass

    # State Commission
    elif type.lower() == "scdrc":
        if not state:
            return {
                "success": False,
                "message": "state is required for scdrc"
            }
        
        commission_id = get_state_commission_id(state)

        if not commission_id:
            return {
                "success": False,
                "message": "state not found"
            }
        
        if bench:
            cause_list_data = get_cause_list(commission_id,bench)
        else:
            cause_list_data = []
            for bench_no in [1, 2, 3, 4, 5, 6]:
                try:
                    data = get_cause_list(commission_id,bench_no)
                    cause_list_data.extend(data)
                except Exception as e:
                    pass

    # District Commission
    elif type.lower() == "dcdrc":
        if not state:
            return {
                "success": False,
                "message": "state is required for dcdrc"
            }

        if not district:
            return {
                "success": False,
                "message": "district is required for dcdrc"
            }

        commission_id = get_district_commission_id(state,district)

        if not commission_id:
            return {
                "success": False,
                "message": "district not found"
            }
        
        if bench:
            cause_list_data = get_cause_list(commission_id,bench)
        else:
            cause_list_data = []
            for bench_no in [1, 2, 3, 4, 5, 6]:
                try:
                    data = get_cause_list(commission_id,bench_no)

                    cause_list_data.extend(data)
                except Exception as e:
                    pass


    else:
        return {
            "success": False,
            "message": "type must be ncdrc, scdrc or dcdrc"
        }

    formatted = []

    for index, case in enumerate(cause_list_data, start=1):
        if type.lower() == "ncdrc":
            state_value = None
            district_value = None

        elif type.lower() == "scdrc":
            state_value = state
            district_value = None

        else:
            state_value = state
            district_value = district

        formatted.append({
            "serial_number": index,
            "complaint_number":case.get("caseNumber"),
            "party_1":", ".join([c.get("complainant_name")
                for c in (case.get("complainantList") or [])
            ]),
            "party_2":", ".join([r.get("respondant_name")
                for r in (case.get("respondantList") or [])
            ]),
            "state":state_value,
            "district":district_value,
            "status_of_case":case.get("caseTypeName")
        })

    return {
        "success": True,
        "total_results": len(formatted),
        "data": formatted
    }


# Health Check
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }