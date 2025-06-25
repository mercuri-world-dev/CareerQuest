def anonymize_email(email: str) -> str:
    """Remove all but the first two characters of the local and domain parts of an email address."""
    if not email or '@' not in email:
        return email

    local_part, domain_part = email.split('@', 1)
    
    # Anonymize local part
    if len(local_part) > 2:
        local_part = local_part[:2] + '*' * (len(local_part) - 2)
    
    # Anonymize domain part
    if len(domain_part) > 2:
        domain_part = domain_part[:2] + '*' * (len(domain_part) - 2)

    return f"{local_part}@{domain_part}"