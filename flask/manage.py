from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
from app.models.contact import Contact
from app.models.authuser import AuthUser, PrivateContact
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
    db.session.add(AuthUser(email="flask@204212", name='สมชาย ทรงแบด',
                            password=generate_password_hash('1234',
                                                            method='sha256'),
                            avatar_url='https://ui-avatars.com/api/?name=\
สมชาย+ทรงแบด&background=83ee03&color=fff'))
    db.session.add(
        Contact(firstname='สมชาย', lastname='ทรงแบด', phone='081-111-1111'))
    db.session.commit()
    db.session.add(
       PrivateContact(firstname='ส้มโอ', lastname='โอเค',
                      phone='081-111-1112', owner_id=1))
    db.session.commit()



if __name__ == "__main__":
    cli()