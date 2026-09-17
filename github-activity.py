import sys
import urllib.request
import json
import urllib.error
from urllib.parse import quote


def ambil_event(username: str) -> list | None:
    url = f"https://api.github.com/users/{quote(username, safe='')}/events/public"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            data = data.decode("utf-8")
            json_data = json.loads(data)
            if not isinstance(json_data, list):
                print("Error: expected list, got any idea ?")
                return None
        return json_data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        if e.code == 404:
            print(f"User '{username}' not found.")
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response.")
        return None


def format_event(event: dict) -> str:
    event_type = event.get("type", "Unknown")
    repo_name = (event.get("repo") or {}).get("name", "Unknown")
    if event_type == "PushEvent":
        branch = event.get("payload", {}).get("ref", "").split("/")[-1]
        return f"Pushed to {repo_name} on branch {branch}"
    elif event_type == "CreateEvent":
        ref_type = (event.get("payload") or {}).get("ref_type", "Unknown")
        return f"CreateEvent in {repo_name}: Created {ref_type}"
    elif event_type == "IssuesEvent":
        action = (event.get("payload") or {}).get("action", "Unknown")
        issue_title = (event.get("payload", {}).get("issue") or {}).get("title", "Unknown")
        return f"IssuesEvent in {repo_name}: {action.capitalize()} issue '{issue_title}'"
    else:
        return f"{event_type} in {repo_name}"


def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print("Error: no username provided")
        return
    else:
        username = args[0]
        events = ambil_event(username)
        if events is None:
            return
        if not events:
            print(f"No public events found for user '{username}'.")
            return
        for event in events:
            print(format_event(event))


if __name__ == "__main__":
    main()