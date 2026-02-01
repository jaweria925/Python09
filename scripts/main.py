import requests
import os
import csv
import time

ORG_NAME = "abc"
BRANCH_NAME = "develop" 
API_VERSION = "7.2-preview"
BRANCH_REF = f"refs/heads/{BRANCH_NAME}"

token = os.getenv("SYSTEM_ACCESSTOKEN")
headers = {
    "Authorization": f"Bearer {token}"
}

def safe_get(url, retries=5):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException:
            time.sleep(2 * (attempt + 1))
    return None

# fetch projects
def get_projects():
    url = f"https://dev.azure.com/{ORG_NAME}/_apis/projects?api-version={API_VERSION}"
    r = safe_get(url)
    if not r:
        return []
    return [p["name"] for p in r.json().get("value", [])]

# fetch pipeline from projects

def get_pipelines(project):
    url = f"https://dev.azure.com/{ORG_NAME}/{project}/_apis/pipelines?api-version={API_VERSION}"
    r = safe_get(url)
    return r.json().get("value", []) if r else []

# get latest run

def get_latest_develop_build_id(project, pipeline_id):
   
    url = (
        f"https://dev.azure.com/{ORG_NAME}/{project}/_apis/build/builds"
        f"?branchName={BRANCH_REF}"
        f"&definitions={pipeline_id}"   
        f"&$top=1"
        f"&api-version={API_VERSION}"
    )

    r= safe_get(url)
    if not r:
        return None

    builds = r.json().get("value", [])
    if builds:
        return builds[0]["id"]
    return None

# get latest build

def get_build(project, build_id):
    url = f"https://dev.azure.com/{ORG_NAME}/{project}/_apis/build/builds/{build_id}?api-version={API_VERSION}"
    r= safe_get(url)
    return r.json() if r else None

# get warnings

def get_warnings(project, build_id):
    url = f"https://dev.azure.com/{ORG_NAME}/{project}/_apis/build/builds/{build_id}/timeline?api-version={API_VERSION}"
    r = safe_get(url)
    if not r or not r.text or "application/json" not in r.headers.get("Content-Type", ""):
        return []

    try:
        data = r.json()
    except ValueError:
        return []

    warnings = []
    for record in data.get("records", []):
        for issue in record.get("issues", []):
            if issue.get("type") == "warning":
                warnings.append(issue.get("message"))

    return warnings

# generate report

def generate_report(csv_filename="pipeline_warnings.csv"):
    artifact_repo = os.environ.get("BUILD_ARTIFACTSTAGINGDIRECTORY")

    if artifact_repo:
        os.makedirs(artifact_repo, exist_ok=True)
        csv_file_path = os.path.join(artifact_repo, csv_filename)
    
    else:
        csv_file_path = csv_filename
    projects = get_projects()
    if not projects:
        print("No projects found.")
        return

    with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["project_name", "pipeline_name", "build_id", "warnings_message"])

        for project in projects:
            print(f"\nProject: {project}")
            pipelines = get_pipelines(project)

            if not pipelines:
                print("  No YAML pipelines found.")
                continue

            for pipe in pipelines:
                run_id = get_latest_develop_build_id(project, pipe["id"])
                if not run_id:
                    continue

                build = get_build(project, run_id)
                if not build or build.get("sourceBranch") != BRANCH_REF:
                    continue

                warnings = get_warnings(project, run_id)
                if not warnings:
                    continue

                writer.writerow([project, pipe["name"], run_id, "\n".join(warnings)])
                print(f"  {pipe['name']} | Build {run_id} | Warnings: {len(warnings)}")
                time.sleep(0.2)

    print(f"\n CSV GENERATED: {csv_file_path}")

#run report
if __name__ == "__main__":
    generate_report()
