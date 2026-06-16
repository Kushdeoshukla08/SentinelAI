def calculate_risk(event_type: str):

    if event_type == "failed_login":
        return 85, "high"

    elif event_type == "password_reset":
        return 40, "medium"

    elif event_type == "login_success":
        return 5, "low"

    return 20, "low"