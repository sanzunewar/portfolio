from django.shortcuts import render

# In a real build these would come from the database (a Project model) or a
# CMS. Hardcoded here so the starter renders immediately with no migrations.
PROJECTS = [
    {
        "title": "Project One",
        "summary": "A short description of what this project does and why it matters.",
        "tags": ["Python", "Django", "PostgreSQL"],
        "url": "https://github.com/yourname/project-one",
    },
    {
        "title": "Project Two",
        "summary": "Another project. Replace these with your real work.",
        "tags": ["FastAPI", "React", "Docker"],
        "url": "https://github.com/yourname/project-two",
    },
    {
        "title": "Project Three",
        "summary": "Showcase the range of what you build here.",
        "tags": ["Data", "ML", "Cloud"],
        "url": "https://github.com/yourname/project-three",
    },
]


def home(request):
    return render(request, "portfolio_app/home.html", {"projects": PROJECTS[:3]})


def projects(request):
    return render(request, "portfolio_app/projects.html", {"projects": PROJECTS})


def about(request):
    return render(request, "portfolio_app/about.html")
