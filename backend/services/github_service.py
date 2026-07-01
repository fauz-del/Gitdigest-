from github import Github, GithubException


def validate_token(token: str):
    """Check the token is valid and return the Github instance."""
    try:
        g = Github(token)
        g.get_user().login
        return g
    except GithubException:
        return None


def get_repo_data(token: str, repo_name: str):
    """
    Fetch commits, contributors and repo metadata from a public repo.
    Returns a dict with everything the PDF builder needs.
    """
    g = validate_token(token)

    if not g:
        return {"error": "Invalid GitHub token"}

    try:
        repo = g.get_repo(repo_name)
    except GithubException:
        return {"error": f"Repo '{repo_name}' not found or is private"}

    # Repo metadata
    metadata = {
        "name": repo.full_name,
        "description": repo.description or "No description provided",
        "language": repo.language or "Not specified",
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "open_issues": repo.open_issues_count,
        "created_at": repo.created_at.strftime("%B %d, %Y"),
        "updated_at": repo.updated_at.strftime("%B %d, %Y"),
    }

    # Fetch commits — capped at 500
    commits = []
    for commit in repo.get_commits()[:500]:
        author = commit.commit.author.name if commit.commit.author else "Unknown"
        date = commit.commit.author.date if commit.commit.author else None
        commits.append({
            "sha": commit.sha[:7],
            "message": commit.commit.message.split("\n")[0],
            "author": author,
            "date": date.strftime("%b %d, %Y %H:%M") if date else "Unknown"
        })

    # Contributor stats
    contributors = {}
    for commit in commits:
        author = commit["author"]
        contributors[author] = contributors.get(author, 0) + 1

    return {
        "repo": repo_name,
        "metadata": metadata,
        "total_commits": len(commits),
        "contributors": contributors,
        "commits": commits
    }
