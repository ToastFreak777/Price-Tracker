from ptracker import create_app, db
from ptracker.models import Users, Items, User_items, Price_history
from werkzeug.security import generate_password_hash

app = create_app()

test_password = "abc123"

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    user1 = Users(
        username="Spongebob",
        email="spongebob@bikinibottom.com",
        password_hash=generate_password_hash(test_password),
    )
    user2 = Users(
        username="Patrick",
        email="patrick@bikinibottom.com",
        password_hash=generate_password_hash(test_password),
    )

    item1 = Items(vendor="Amazon", url="https://amazon.com/product/123")

    db.session.add_all([user1, user2, item1])
    db.session.commit()

    print("Database seeded successfully.")
