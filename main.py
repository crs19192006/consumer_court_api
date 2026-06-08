from fastapi import FastAPI
from client import (get_case_status,search_by_party_name,get_all_states,get_district_commissions,
get_state_commission_id,get_district_commission_id)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Consumer Court API Running"}


@app.get("/case-status/{search_value:path}")
def case_status(search_value: str):
    print("Received:", search_value)
    return get_case_status(search_value)


@app.get("/party-search")
def party_search(
    type: str,
    name: str,
    state: str = None,
    district: str = None
):
    filing_date1 = "2000-01-01"
    filing_date2 = "2035-12-31"
    if type.lower() == "ncdrc":
        commission_type_id = 1
        commission_id = 11000000

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

@app.get("/states", include_in_schema=False)
@app.get("/districts/{state_commission_id}", include_in_schema=False)
@app.get("/districts-by-state", include_in_schema=False)

@app.get("/health")
def health():
    return {"status": "healthy"}