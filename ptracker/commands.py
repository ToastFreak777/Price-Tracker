import click
from flask.cli import with_appcontext
from ptracker.extensions import db
from ptracker.models import User
from werkzeug.security import generate_password_hash

test_password = "abc123"


@click.command("seed-db")
@with_appcontext
def seed_db():
    """Seed the database with initial data."""
    user1 = User(
        username="Spongebob",
        email="spongebob@bikinibottom.com",
        password_hash=generate_password_hash(test_password),
    )
    user2 = User(
        username="Patrick",
        email="patrick@rock.com",
        password_hash=generate_password_hash(test_password),
    )

    db.session.add_all([user1, user2])
    db.session.commit()

    click.echo("Database seeded!")


@click.command("reset-db")
@with_appcontext
def reset_db():
    """Drop and recreate all tables"""
    db.drop_all()
    db.create_all()
    click.echo("Database reset!")
