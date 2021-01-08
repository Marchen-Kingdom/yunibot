import sqlalchemy

metadata = sqlalchemy.MetaData()
clans = sqlalchemy.Table(
    "clans",
    metadata,
    sqlalchemy.Column("group_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("clan_name", sqlalchemy.String),
    sqlalchemy.Column("server", sqlalchemy.String),
)
members = sqlalchemy.Table(
    "members",
    metadata,
    sqlalchemy.Column(
        "group_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("clans.group_id"),
        primary_key=True,
    ),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nickname", sqlalchemy.String),
)
challenge = sqlalchemy.Table(
    "challenge",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("year", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("month", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(
        "group_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("clans.group_id"),
    ),
    sqlalchemy.Column(
        "user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("members.user_id")
    ),
    sqlalchemy.Column("time", sqlalchemy.TIMESTAMP, nullable=False),
    sqlalchemy.Column("round", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("boss", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("damage", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("type", sqlalchemy.Integer, nullable=False),
    sqlite_autoincrement=True,
)
