from fastapi import FastAPI

from client import (
    get_case_status,
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


# --------------------------------------------------
# Home Endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Consumer Court API Running"
    }


# --------------------------------------------------
# Case Status Search
#
# Supports:
# - Case Number
# - Filing Reference Number
# - e-Daakhil Number
# --------------------------------------------------

@app.get("/case-status/{search_value:path}")
def case_status(search_value: str):
    return get_case_status(search_value)


# --------------------------------------------------
# Party Search
#
# Examples:
#
# National:
# type=ncdrc
#
# State:
# type=scdrc
# state=KARNATAKA
#
# District:
# type=dcdrc
# state=KARNATAKA
# district=Bangalore Urban
# --------------------------------------------------

@app.get("/party-search")
def party_search(
    type: str,
    name: str,
    state: str = None,
    district: str = None
):

    # Large date range so user doesn't need
    # to provide dates manually
    filing_date1 = "2000-01-01"
    filing_date2 = "2035-12-31"

    # ------------------------------------------
    # National Commission Search
    # ------------------------------------------

    if type.lower() == "ncdrc":

        commission_type_id = 1
        commission_id = 11000000

    # ------------------------------------------
    # State Commission Search
    # ------------------------------------------

    elif type.lower() == "scdrc":

        if not state:
            return {
                "success": False,
                "message": "state is required for scdrc"
            }

        commission_type_id = 2

        commission_id = get_state_commission_id(
            state
        )

        if not commission_id:
            return {
                "success": False,
                "message": "state not found"
            }

    # ------------------------------------------
    # District Commission Search
    # ------------------------------------------

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

        commission_id = get_district_commission_id(
            state,
            district
        )

        if not commission_id:
            return {
                "success": False,
                "message": "district not found"
            }

    # ------------------------------------------
    # Invalid Type
    # ------------------------------------------

    else:
        return {
            "success": False,
            "message": "type must be ncdrc, scdrc or dcdrc"
        }

    return search_by_party_name(
        name,
        commission_type_id,
        commission_id,
        filing_date1,
        filing_date2
    )


# --------------------------------------------------
# Hidden Helper Endpoint
# Returns all State Commissions
# --------------------------------------------------

@app.get("/states", include_in_schema=False)
def states():
    return get_all_states()


# --------------------------------------------------
# Hidden Helper Endpoint
# Returns District Commissions
# using State Commission ID
# --------------------------------------------------

@app.get("/districts/{state_commission_id}", include_in_schema=False)
def districts(state_commission_id: int):
    return get_district_commissions(
        state_commission_id
    )


# --------------------------------------------------
# Hidden Helper Endpoint
# Returns Districts using State Name
# --------------------------------------------------

@app.get("/districts-by-state", include_in_schema=False)
def districts_by_state(state: str):

    state_commission_id = get_state_commission_id(
        state
    )

    if not state_commission_id:
        return {
            "success": False,
            "message": "State not found"
        }

    return get_district_commissions(
        state_commission_id
    )


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
                    print(f"FETCHING BENCH {bench_no}")
                    data = get_cause_list(commission_id,bench_no)
                    print(f"BENCH {bench_no} CASES:",len(data))
                    cause_list_data.extend(data)
                except Exception as e:
                    print(f"BENCH {bench_no} ERROR:", e)

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
                    print(f"FETCHING BENCH {bench_no}")
                    data = get_cause_list(commission_id,bench_no)
                    print(f"BENCH {bench_no} CASES:",len(data))
                    cause_list_data.extend(data)
                except Exception as e:
                    print(f"BENCH {bench_no} ERROR:", e)



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
                    print(f"FETCHING BENCH {bench_no}")
                    data = get_cause_list(commission_id,bench_no)
                    print(f"BENCH {bench_no} CASES:",len(data))
                    cause_list_data.extend(data)
                except Exception as e:
                    print(f"BENCH {bench_no} ERROR:", e)


    else:
        return {
            "success": False,
            "message": "type must be ncdrc, scdrc or dcdrc"
        }

    formatted = []

    for case in cause_list_data:
        formatted.append({
            "case_number": case.get("caseNumber"),
            "previous_case_number": case.get("previousCaseNumber"),
            "case_type": case.get("caseTypeName"),
            "commission": case.get("commissionName"),
            "state": case.get("stateName"),
            "commission_type": case.get("commissionType"),
            "court_room": case.get("courtRoomName"),
            "cause_list_slot": case.get("causelistTypeName"),
            "hearing_date": case.get("dateOfHearing"),
            "judges": [
                judge.get("judge_name")
                for judge in case.get(
                    "judgeName",
                    []
                )
            ],

            "complainants": [
                complainant.get(
                    "complainant_name"
                )
                for complainant in case.get(
                    "complainantList",
                    []
                )
            ],

            "respondents": [
                respondent.get(
                    "respondant_name"
                )
                for respondent in case.get(
                    "respondantList",
                    []
                )
            ],

            "complainant_advocates": [
                advocate.get(
                    "advocate_name"
                )
                for advocate in (
                    case.get(
                        "complainantAdvocateList"
                    ) or []
                )
            ],

            "respondent_advocates": [
                advocate.get(
                    "advocate_name"
                )
                for advocate in (
                    case.get(
                        "respondantAdvocateList"
                    ) or []
                )
            ]
        })

    return {
        "success": True,
        "total_cases": len(formatted),
        "data": formatted
    }



# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }