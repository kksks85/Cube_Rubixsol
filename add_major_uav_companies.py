# Script to add major UAV companies to the database
from app import create_app, db
from app.models import Company

companies = [
    {"name": "DJI", "country": "China", "website": "https://www.dji.com"},
    {"name": "Parrot", "country": "France", "website": "https://www.parrot.com"},
    {"name": "Skydio", "country": "USA", "website": "https://www.skydio.com"},
    {"name": "Autel Robotics", "country": "China/USA", "website": "https://www.autelrobotics.com"},
    {"name": "Teledyne FLIR", "country": "USA", "website": "https://www.flir.com"},
    {"name": "senseFly", "country": "Switzerland", "website": "https://www.sensefly.com"},
    {"name": "Delair", "country": "France", "website": "https://www.delair.aero"},
    {"name": "AeroVironment", "country": "USA", "website": "https://www.avinc.com"},
]

app = create_app()
with app.app_context():
    for c in companies:
        # Check if company already exists
        existing = Company.query.filter_by(name=c["name"]).first()
        if not existing:
            company = Company(
                name=c["name"],
                country=c["country"],
                website=c.get("website", "")
            )
            db.session.add(company)
            print(f"Added: {c['name']}")
        else:
            print(f"Exists: {c['name']}")
    db.session.commit()
    print("Done.")
