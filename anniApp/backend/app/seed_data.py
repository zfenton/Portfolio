from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import Base, Activity, ActivityOption, AppConfig

# Edit this list freely between deploys — the sync will add, update,
# and remove activities/options in the DB to match what is defined here.
ACTIVITIES_DATA = [
    {
        "order": 1,
        "question": "Where should we go for our anniversary celebration?",
        "options": [
            {"order": 1, "option_text": "Beach Town"},
            {"order": 2, "option_text": "Redwood Hike"},
        ]
    },
    {
        "order": 2,
        "question": "Where should we snack up for the drive?",
        "options": [
            {"order": 1, "option_text": "Gas Station"},
            {"order": 2, "option_text": "Grocery Store"},
        ]
    },
    {
        "order": 3,
        "question": "Where should we get lunch?",
        "options": [
            {"order": 1, "option_text": "Old Reliable"},
            {"order": 2, "option_text": "Somewhere new"},

        ]
    },
    {
        "order": 4,
        "question": "What gift should we get eachother?",
        "options": [
            {"order": 1, "option_text": "Something to wear"},
            {"order": 2, "option_text": "Something to read"},
        ]
    },
    {
        "order": 5,
        "question": "Now it's time for dinner; should we dress up or relax the style?",
        "options": [
            {"order": 1, "option_text": "Dress Up"},
            {"order": 2, "option_text": "Dress Down"},
        ]
    },
    {
        "order": 6,
        "question": "How should we close out the night?",
        "options": [
            {"order": 1, "option_text": "Fancy cocktails"},
            {"order": 2, "option_text": "Beer and wings"},
        ]
    }
]


def sync_database():
    """
    Syncs the database with ACTIVITIES_DATA on every startup.
    - Creates tables if they don't exist.
    - Adds new activities/options defined in code but missing from DB.
    - Updates question text and option text if they've changed.
    - Removes activities/options that are no longer defined in code.
    - Ensures an AppConfig row exists.
    """
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        desired_orders = {a["order"] for a in ACTIVITIES_DATA}

        # Remove activities no longer in ACTIVITIES_DATA
        for activity in db.query(Activity).all():
            if activity.order not in desired_orders:
                print(f"Removing activity order={activity.order}: '{activity.question}'")
                db.delete(activity)

        db.flush()

        for activity_data in ACTIVITIES_DATA:
            activity = db.query(Activity).filter_by(order=activity_data["order"]).first()

            if activity is None:
                # New activity — create it
                activity = Activity(
                    order=activity_data["order"],
                    question=activity_data["question"],
                    is_active=True
                )
                db.add(activity)
                db.flush()
                print(f"Added activity order={activity.order}: '{activity.question}'")
            elif activity.question != activity_data["question"]:
                # Question text changed — update it
                print(f"Updating activity order={activity.order} question")
                activity.question = activity_data["question"]

            # Sync options for this activity
            desired_option_orders = {o["order"] for o in activity_data["options"]}

            # Remove options no longer defined
            for option in list(activity.options):
                if option.order not in desired_option_orders:
                    print(f"  Removing option order={option.order}: '{option.option_text}'")
                    db.delete(option)

            for option_data in activity_data["options"]:
                option = next(
                    (o for o in activity.options if o.order == option_data["order"]),
                    None
                )
                if option is None:
                    option = ActivityOption(
                        activity_id=activity.id,
                        option_text=option_data["option_text"],
                        order=option_data["order"]
                    )
                    db.add(option)
                    print(f"  Added option order={option_data['order']}: '{option_data['option_text']}'")
                elif option.option_text != option_data["option_text"]:
                    print(f"  Updating option order={option.order} text")
                    option.option_text = option_data["option_text"]

        # Ensure AppConfig exists
        if db.query(AppConfig).count() == 0:
            db.add(AppConfig(is_voting_closed=False, voting_end_time=None))
            print("Created AppConfig")

        db.commit()
        print("Database sync complete.")

    except Exception as e:
        print(f"Error during database sync: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    sync_database()
