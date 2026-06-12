import json
import urllib.request

# The target account to fetch repositories from
GITHUB_USERNAME = "advaithvanand722-gif"

# Where the file will be saved in your repository
OUTPUT_FILE = "projects.json"

def fetch_repositories(username):
    """Fetches public repositories from the GitHub API."""
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
    
    # GitHub requires a User-Agent header for API requests
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "Portfolio-Auto-Fetcher"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
    return []

def format_projects(repos):
    """Filters and formats the raw API data."""
    projects = []
    for repo in repos:
        # Skip the portfolio repository itself to avoid a recursive loop
        if repo.get("name") == "folio" or repo.get("fork"):
            continue
            
        project_info = {
            "name": repo.get("name"),
            "description": repo.get("description") or "No description provided.",
            "url": repo.get("html_url"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count"),
            "last_updated": repo.get("updated_at")
        }
        projects.append(project_info)
    return projects

def main():
    print(f"Fetching repositories for {GITHUB_USERNAME}...")
    raw_repos = fetch_repositories(GITHUB_USERNAME)
    
    if not raw_repos:
        print("No repositories found or API limit reached.")
        return

    processed_projects = format_projects(raw_repos)
    
    # Save the formatted data to the JSON file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(processed_projects, file, indent=4, ensure_ascii=False)
        
    print(f"Success! Generated {OUTPUT_FILE} with {len(processed_projects)} projects.")

if __name__ == "__main__":
    main()