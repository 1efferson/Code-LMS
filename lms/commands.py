# in lms/commands.py
from flask.cli import with_appcontext
import click
from lms import db
from lms.models.user import User

@click.command("promote-admin")
@click.argument("email")
@with_appcontext
def promote_admin(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        click.echo("User not found.")
        return
    user.is_admin = True
    db.session.commit()
    click.echo(f"{user.email} is now an admin.")
