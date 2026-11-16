def pick(model, field_name, *keywords, default=None):
    """Return the choice value whose value or label contains a keyword.
    Falls back to the first choice, or `default` for fields without choices."""
    choices = list(model._meta.get_field(field_name).flatchoices)
    if not choices:
        return default
    for kw in keywords:
        for value, label in choices:
            if kw.lower() in str(value).lower() or kw.lower() in str(label).lower():
                return value
    return choices[0][0]