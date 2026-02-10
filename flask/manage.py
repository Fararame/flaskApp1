from flask.cli import FlaskGroup


from app import app, db
from app.models.contact import Contact
from migrate_anime import do_migrate_anime




cli = FlaskGroup(app)


@cli.command("migrate_anime")
def migrate_anime():
   do_migrate_anime()





@cli.command("create_db")
def create_db():
    db.reflect()
    db.drop_all()
    db.create_all()
    db.session.commit()




@cli.command("seed_db")
def seed_db():
    # Call migrate_anime as part of seeding
    do_migrate_anime()
    db.session.add(
        Contact(firstname='สมชาย', lastname='ทรงแบด', phone='081-111-1111'))
    db.session.commit()




if __name__ == "__main__":
    cli()