def validate_runtime_config(cfg, device, data_type, keys=None):
    errors = []
    device_key = device.lower()
    keys = list(keys or [])

    for section in ("global", "cruise", device_key):
        if section not in cfg:
            errors.append(f"missing section [{section}]")

    if errors:
        raise ValueError("Invalid configuration: " + ", ".join(errors))

    for section in ("header", "split"):
        if section not in cfg[device_key]:
            errors.append(f"missing section [{device_key}.{section}]")

    required_cruise_keys = ("CYCLEMESURE", "PLATEFORME", "INSTITUTE", "TIMEZONE", "CREATOR")
    for key in required_cruise_keys:
        if key not in cfg["cruise"]:
            errors.append(f"missing key cruise.{key}")

    derived_trajectory_keys = {"DAYD", "ETDD", "LATITUDE", "LONGITUDE"}
    split = cfg[device_key].get("split", {})
    for key in keys:
        if key in split:
            continue
        if data_type == "TRAJECTORY" and key in derived_trajectory_keys:
            continue
        errors.append(f"missing key {device_key}.split.{key}")

    if errors:
        raise ValueError("Invalid configuration: " + ", ".join(errors))
