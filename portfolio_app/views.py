from django.shortcuts import render

# In a real build these would come from the database (a Project model) or a
# CMS. Hardcoded here so the starter renders immediately with no migrations.
PROJECTS = [
    {
        "title": "Enterprise Network Design & Deployment",
        "category": "Network Infrastructure",
        "summary": "Designed and deployed a small enterprise network — VLAN "
                   "segmentation, switching, and secure, firewalled internet access "
                   "built for reliable day-to-day operations.",
        "tags": ["Networking", "VLANs", "Switching", "Firewall"],
    },
    {
        "title": "Cinema Hall Network & POS Setup",
        "category": "Network + Systems",
        "summary": "Built the full network for a cinema hall: deployed and configured "
                   "POS machines and their software, stood up a localised on-site "
                   "server, and secured the environment behind a firewall.",
        "tags": ["POS Systems", "Local Server", "Firewall", "Networking"],
    },
    {
        "title": "Banking Service Deployment & Server Hardening",
        "category": "Banking Systems",
        "summary": "Deployed and integrated banking service products to industry "
                   "standards — built and hardened application, backup, and test "
                   "servers, configured firewalls and user access, and handled "
                   "deployment and ongoing troubleshooting.",
        "tags": ["Banking", "Server Hardening", "Firewall", "Backup & DR", "Linux"],
    },
    {
        "title": "ISP Reseller Network Provisioning",
        "category": "ISP / FTTH",
        "summary": "Provisioned ISP reseller networks end to end — configured OLTs, "
                   "switches, and routers so connectivity flows correctly through "
                   "reseller infrastructure, and restored outages fast by activating "
                   "alternate routes to bring service back.",
        "tags": ["ISP", "OLT", "Routing", "Switching", "Troubleshooting"],
    },
]


def home(request):
    return render(request, "portfolio_app/home.html", {"projects": PROJECTS[:3]})


def projects(request):
    return render(request, "portfolio_app/projects.html", {"projects": PROJECTS})


def about(request):
    return render(request, "portfolio_app/about.html")
