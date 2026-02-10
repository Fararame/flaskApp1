import json
from flask import (jsonify, render_template,
                   request, url_for, flash, redirect)

from sqlalchemy.sql import text
from app import app, db
from app import hw_views  # noqa
from app.models.contact import Contact


@app.route('/')
def home():
    return "Flask says 'Hello world!'"

@app.route('/crash')
def crash():
    return 1/0

@app.route('/db')
def db_connection():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return '<h1>db works.</h1>'
    except Exception as e:
        return '<h1>db is broken.</h1>' + str(e)


@app.route('/lab04')
def lab04_bootstrap():
    return app.send_static_file('lab04_bootstrap.html')

@app.route('/lab10', methods=('GET', 'POST'))
def lab10_phonebook():
    if request.method == 'POST':
        if request.is_json:
            result = request.json
        else:
            result = request.form.to_dict()
        app.logger.debug(str(result))


        id_ = result.get('id', '')
        validated = True
        validated_dict = dict()
        valid_keys = ['firstname', 'lastname', 'phone']


        # Validate the input
        for key in valid_keys:
            app.logger.debug(f"{key}: {result[key]}")
 
            value = result[key].strip()
            if not value or value == 'undefined':
                break
            validated_dict[key] = value


        if len(validated_dict.keys()) != len(valid_keys):
            app.logger.debug('Validated dict: ' + str(validated_dict))
            return lab10_db_contacts()


        try:


            if not id_:  # Create a new contact entry
                entry = Contact(**validated_dict)
                db.session.add(entry)
            else:  # Update an existing contact entry
                contact = Contact.query.get(id_)
                if contact:
                    contact.update(**validated_dict)
                else:
                    return lab10_db_contacts()


            db.session.commit()  # Commit only if everything is successful


            return lab10_db_contacts()


        except Exception as e:
            db.session.rollback()  # Rollback transaction on failure
            app.logger.error(f"Database error: {str(e)}")
            return lab10_db_contacts()


    return app.send_static_file('lab10_phonebook.html')

@app.route("/lab10/contacts")
def lab10_db_contacts():
    contacts = []
    db_contacts = Contact.query.all()


    contacts = list(map(lambda x: x.to_dict(), db_contacts))
    app.logger.debug("DB Contacts: " + str(contacts))


    return jsonify(contacts)

@app.route('/lab10/remove_contact', methods=('GET', 'POST'))
def lab10_remove_contacts():
    app.logger.debug("LAB10 - REMOVE")


    if request.method == 'POST':
        if request.is_json:
            result = request.json
        else:
            result = request.form.to_dict()


        id_ = result.get('id', '')


        if not id_:  # Validate ID
            app.logger.error("Error: No ID provided for removal.")
            return lab10_db_contacts()


        try:


            contact = Contact.query.get(id_)
            if not contact:
                app.logger.error(f"Error: Contact with id {id_} not found.")
                return lab10_db_contacts()


            db.session.delete(contact)


            db.session.commit()  # Commit if successful
            return lab10_db_contacts()


        except Exception as ex:
            db.session.rollback()  # Rollback on failure
            app.logger.error(f"Error removing contact with id {id_}: {ex}")
            return lab10_db_contacts()


    return lab10_db_contacts()