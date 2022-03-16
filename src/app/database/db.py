import sqlite3

import click
import pkg_resources
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            "sqlite_db", detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


@click.command("init-db")
@with_appcontext
def init_db():
    db = get_db()

    with current_app.open_resource(pkg_resources.resource_filename("database", "schema.sql")) as f:
        db.executescript(f.read().decode("utf8"))
        print("Database created")


def close_db():
    db = g.pop("db", None)

    if db is not None:
        db.close()
