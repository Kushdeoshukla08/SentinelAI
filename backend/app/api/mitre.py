from fastapi import APIRouter
from fastapi import Depends

from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/mitre",
    tags=["MITRE ATT&CK"]
)

@router.get("/")
def get_mitre_techniques(
    current_user=Depends(get_current_user)
):

    return [
        {
            "technique_id": "T1110",
            "name": "Brute Force",
            "tactic": "Credential Access"
        },
        {
            "technique_id": "T1078",
            "name": "Valid Accounts",
            "tactic": "Defense Evasion"
        },
        {
            "technique_id": "T1059",
            "name": "Command and Scripting Interpreter",
            "tactic": "Execution"
        }
    ]