# TODO: integrate this with the main cli such that one can search every aws profile
# defined in .aws/config for the root access keys


def check_root_access_keys(profile):
    session = boto3.Session(profile_name=profile)
    iam = session.client("iam")
    try:
        summary = iam.get_account_summary()
        keys_present = summary["SummaryMap"]["AccountAccessKeysPresent"]
        if keys_present:
            print(f"The root user has access keys in account: {profile}.")
        else:
            print(f"No access keys for root user in account: {profile}.")
    except Exception as e:
        print(f"Error checking account {profile}: {str(e)}")
