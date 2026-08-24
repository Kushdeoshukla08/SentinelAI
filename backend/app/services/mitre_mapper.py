def map_event_to_mitre(event_type: str):

    mappings = {
        "failed_login": {
            "technique_id": "T1110",
            "technique_name": "Brute Force"
        },
        "password_reset": {
            "technique_id": "T1098",
            "technique_name": "Account Manipulation"
        },
        "login_success": {
            "technique_id": "T1078",
            "technique_name": "Valid Accounts"
        }
    }

    return mappings.get(
        event_type,
        {
            "technique_id": "UNKNOWN",
            "technique_name": "Unknown Technique"
        }
    )