from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing, Rect, String
from io import BytesIO
from datetime import datetime

DARK_BG = colors.HexColor("#0D1117")
GREEN = colors.HexColor("#238636")
GREEN_BRIGHT = colors.HexColor("#3FB950")
RED = colors.HexColor("#F85149")
ORANGE = colors.HexColor("#D29922")
MUTED = colors.HexColor("#8B949E")
TEXT = colors.HexColor("#C9D1D9")
SURFACE = colors.HexColor("#161B22")
BORDER = colors.HexColor("#30363D")
WHITE = colors.white


def make_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=styles["Normal"],
            fontSize=28,
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName="Helvetica-Bold"
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=13,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=6
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=styles["Normal"],
            fontSize=10,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=4
        ),
        "heading": ParagraphStyle(
            "Heading",
            parent=styles["Normal"],
            fontSize=14,
            textColor=GREEN,
            spaceBefore=16,
            spaceAfter=10,
            fontName="Helvetica-Bold"
        ),
        "body": ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            textColor=TEXT,
            spaceAfter=6,
            leading=16
        ),
        "mono": ParagraphStyle(
            "Mono",
            parent=styles["Normal"],
            fontSize=9,
            textColor=TEXT,
            fontName="Courier",
            spaceAfter=4
        ),
        "risk": ParagraphStyle(
            "Risk",
            parent=styles["Normal"],
            fontSize=10,
            textColor=RED,
            spaceAfter=6,
            fontName="Helvetica-Bold"
        ),
        "warning": ParagraphStyle(
            "Warning",
            parent=styles["Normal"],
            fontSize=10,
            textColor=ORANGE,
            spaceAfter=6,
            fontName="Helvetica-Bold"
        ),
        "safe": ParagraphStyle(
            "Safe",
            parent=styles["Normal"],
            fontSize=10,
            textColor=GREEN_BRIGHT,
            spaceAfter=6,
            fontName="Helvetica-Bold"
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER
        ),
    }


def build_contributor_chart(breakdown: list, width: float = 440) -> Drawing:
    bar_height = 20
    gap = 10
    label_width = 130
    bar_max_width = width - label_width - 70
    total_height = len(breakdown) * (bar_height + gap) + 20

    drawing = Drawing(width, total_height)

    for i, contributor in enumerate(breakdown):
        y = total_height - (i + 1) * (bar_height + gap)
        bar_width = max((contributor["percentage"] / 100) * bar_max_width, 2)

        drawing.add(Rect(
            label_width, y,
            bar_max_width, bar_height,
            fillColor=SURFACE,
            strokeColor=BORDER,
            strokeWidth=0.5
        ))

        if contributor["percentage"] >= 80:
            fill_color = RED
        elif contributor["percentage"] >= 50:
            fill_color = ORANGE
        else:
            fill_color = GREEN

        drawing.add(Rect(
            label_width, y,
            bar_width, bar_height,
            fillColor=fill_color,
            strokeColor=None
        ))

        drawing.add(String(
            label_width - 6, y + 6,
            contributor["author"][:20],
            fontSize=8,
            fillColor=TEXT,
            textAnchor="end"
        ))

        drawing.add(String(
            label_width + bar_width + 6, y + 6,
            f'{contributor["percentage"]}%',
            fontSize=8,
            fillColor=MUTED,
            textAnchor="start"
        ))

    return drawing


def build_report(repo_name: str, analytics: dict, metadata: dict, commits: list) -> BytesIO:
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        s = make_styles()
        elements = []
        now = datetime.now().strftime("%B %d, %Y at %H:%M")
        risks = analytics.get("bus_factor_risks", [])
        breakdown = analytics.get("contributor_breakdown", [])

        # near misses: 50-79%
        near_misses = [
            c for c in breakdown
            if 50 <= c["percentage"] < 80
        ]

        # ─── PAGE 1: COVER ───────────────────────────────────────
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph("GitDigest", s["title"]))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(repo_name, s["subtitle"]))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f"Generated on {now}", s["meta"]))
        elements.append(Spacer(1, 1*cm))

        cover_data = [
            ["Total Commits", "Contributors", "Risk Flags"],
            [
                str(analytics.get("total_commits", 0)),
                str(len(breakdown)),
                str(len(risks))
            ]
        ]
        cover_table = Table(cover_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
        cover_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
            ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, 1), DARK_BG),
            ("TEXTCOLOR", (0, 1), (-1, 1), WHITE),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 1), (-1, 1), 22),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWHEIGHT", (0, 0), (0, 0), 28),
            ("ROWHEIGHT", (0, 1), (0, 1), 48),
        ]))
        elements.append(cover_table)
        elements.append(PageBreak())

        # ─── PAGE 2: REPO OVERVIEW ───────────────────────────────
        elements.append(Paragraph("Repository Overview", s["heading"]))
        overview_data = [
            ["Field", "Value"],
            ["Repository", metadata.get("name", repo_name)],
            ["Description", metadata.get("description", "—")],
            ["Primary Language", metadata.get("language", "—")],
            ["Stars", f'{metadata.get("stars", 0):,}'],
            ["Forks", f'{metadata.get("forks", 0):,}'],
            ["Open Issues", f'{metadata.get("open_issues", 0):,}'],
            ["Created", metadata.get("created_at", "—")],
            ["Last Updated", metadata.get("updated_at", "—")],
        ]

        overview_table = Table(overview_data, colWidths=[5*cm, 11.5*cm])
        overview_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
            ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 1), (0, -1), MUTED),
            ("TEXTCOLOR", (1, 1), (1, -1), TEXT),
            ("BACKGROUND", (0, 1), (-1, -1), DARK_BG),
            ("ROWBACKGROUND", (0, 1), (-1, -1), [DARK_BG, SURFACE]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWHEIGHT", (0, 0), (-1, -1), 24),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        elements.append(overview_table)
        elements.append(PageBreak())

        # ─── PAGE 3: CONTRIBUTOR ACTIVITY ────────────────────────
        elements.append(Paragraph("Contributor Activity", s["heading"]))
        elements.append(Paragraph(
            "Commit distribution across all contributors. "
            "Red bars indicate Bus Factor risk (80%+). "
            "Orange bars are worth monitoring (50-79%).",
            s["body"]
        ))
        elements.append(Spacer(1, 0.3*cm))

        if breakdown:
            chart = build_contributor_chart(breakdown[:15])
            elements.append(chart)
            elements.append(Spacer(1, 0.8*cm))

            contrib_data = [["Contributor", "Commits", "% of Total", "Status"]]
            for c in breakdown:
                if c["percentage"] >= 80:
                    status = "HIGH RISK"
                elif c["percentage"] >= 50:
                    status = "WATCH"
                else:
                    status = "Healthy"
                contrib_data.append([
                    c["author"],
                    str(c["commits"]),
                    f'{c["percentage"]}%',
                    status
                ])

            contrib_table = Table(contrib_data, colWidths=[7*cm, 3*cm, 3.5*cm, 3*cm])
            contrib_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
                ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 1), (-1, -1), TEXT),
                ("BACKGROUND", (0, 1), (-1, -1), DARK_BG),
                ("ROWBACKGROUND", (0, 1), (-1, -1), [DARK_BG, SURFACE]),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWHEIGHT", (0, 0), (-1, -1), 22),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]))
            elements.append(contrib_table)

        elements.append(PageBreak())

        # ─── PAGE 4: COMMIT HISTORY ──────────────────────────────
        elements.append(Paragraph("Recent Commit History", s["heading"]))
        elements.append(Paragraph(
            f"Showing the most recent {min(50, len(commits))} commits "
            f"out of {len(commits)} analyzed, sorted newest first.",
            s["body"]
        ))
        elements.append(Spacer(1, 0.3*cm))

        commit_data = [["#", "SHA", "Author", "Date", "Message"]]
        for i, commit in enumerate(commits[:50], 1):
            msg = commit["message"][:55] + "..." if len(commit["message"]) > 55 else commit["message"]
            commit_data.append([
                str(i),
                commit["sha"],
                commit["author"][:15],
                commit["date"],
                msg
            ])

        commit_table = Table(
            commit_data,
            colWidths=[0.8*cm, 1.5*cm, 3*cm, 3.5*cm, 7.7*cm]
        )
        commit_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
            ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("TEXTCOLOR", (0, 1), (-1, -1), TEXT),
            ("FONTNAME", (1, 1), (1, -1), "Courier"),
            ("BACKGROUND", (0, 1), (-1, -1), DARK_BG),
            ("ROWBACKGROUND", (0, 1), (-1, -1), [DARK_BG, SURFACE]),
            ("ALIGN", (0, 0), (1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWHEIGHT", (0, 0), (-1, -1), 18),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(commit_table)
        elements.append(PageBreak())

        # ─── PAGE 5: RISK SUMMARY ────────────────────────────────
        elements.append(Paragraph("Risk Summary", s["heading"]))
        elements.append(Paragraph(
            "The Bus Factor measures how many contributors your project critically depends on. "
            "A Bus Factor of 1 means if one key person becomes unavailable, "
            "critical parts of the codebase may become very difficult to maintain or debug.",
            s["body"]
        ))
        elements.append(Spacer(1, 0.4*cm))

        # Critical risks
        if risks:
            elements.append(Paragraph("Critical Risks (80%+)", s["risk"]))
            for risk in risks:
                elements.append(Paragraph(
                    f'⚠ {risk["author"]} — {risk["risk_level"]} RISK',
                    s["risk"]
                ))
                elements.append(Paragraph(
                    f'{risk["author"]} authored {risk["percentage"]}% of all commits '
                    f'({risk["commits"]} out of {analytics["total_commits"]} commits). '
                    f'If this contributor becomes unavailable, a significant portion '
                    f'of the codebase may lack adequate team familiarity. '
                    f'Recommend: pair programming sessions, code walkthroughs, '
                    f'and improved inline documentation for their areas of ownership.',
                    s["body"]
                ))
                elements.append(Spacer(1, 0.3*cm))
        else:
            elements.append(Paragraph(
                "✓ No critical Bus Factor risks detected.",
                s["safe"]
            ))
            elements.append(Paragraph(
                "No single contributor accounts for 80% or more of total commits. "
                "The codebase appears to have healthy knowledge distribution.",
                s["body"]
            ))

        elements.append(Spacer(1, 0.4*cm))

        # Near misses
        if near_misses:
            elements.append(Paragraph("Worth Monitoring (50–79%)", s["warning"]))
            for c in near_misses:
                elements.append(Paragraph(
                    f'△ {c["author"]} — {c["percentage"]}% of commits ({c["commits"]} commits). '
                    f'Not yet critical but worth ensuring knowledge is being shared '
                    f'with other team members.',
                    s["body"]
                ))
            elements.append(Spacer(1, 0.3*cm))

        # Overall health score
        elements.append(Spacer(1, 0.4*cm))
        elements.append(Paragraph("Overall Health Assessment", s["heading"]))

        top_pct = breakdown[0]["percentage"] if breakdown else 0
        if len(risks) > 0:
            health = "At Risk"
            health_style = s["risk"]
            health_detail = (
                f"The top contributor owns {top_pct}% of commits. "
                f"Immediate action recommended to distribute knowledge across the team."
            )
        elif len(near_misses) > 0:
            health = "Needs Attention"
            health_style = s["warning"]
            health_detail = (
                f"The top contributor owns {top_pct}% of commits. "
                f"No immediate crisis, but knowledge sharing should be prioritized."
            )
        else:
            health = "Healthy"
            health_style = s["safe"]
            health_detail = (
                f"The top contributor owns {top_pct}% of commits across "
                f"{len(breakdown)} contributors. "
                f"Knowledge appears well distributed across the team."
            )

        elements.append(Paragraph(f"Status: {health}", health_style))
        elements.append(Paragraph(health_detail, s["body"]))
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph(
            "Generated by GitDigest · Public repos only · Token never stored",
            s["footer"]
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"ReportLab build error: {e}")
        return None
