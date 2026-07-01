def calculate_bus_factor(contributors: dict, commits: list):
    """
    Bus Factor: flags any contributor who authored more than
    80% of total commits — meaning if they leave, the project
    is at serious risk.
    """
    total_commits = len(commits)

    if total_commits == 0:
        return {"bus_factor_risks": [], "total_commits": 0}

    risks = []

    for author, count in contributors.items():
        percentage = (count / total_commits) * 100
        if percentage >= 80:
            risks.append({
                "author": author,
                "commits": count,
                "percentage": round(percentage, 1),
                "risk_level": "HIGH" if percentage >= 90 else "MEDIUM"
            })

    # Sort by highest percentage first
    risks.sort(key=lambda x: x["percentage"], reverse=True)

    return {
        "bus_factor_risks": risks,
        "total_commits": total_commits,
        "contributor_breakdown": [
            {
                "author": author,
                "commits": count,
                "percentage": round((count / total_commits) * 100, 1)
            }
            for author, count in sorted(
                contributors.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]
    }
