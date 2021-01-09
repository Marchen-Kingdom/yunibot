import sqlalchemy

metadata = sqlalchemy.MetaData()
clan = sqlalchemy.Table(
    "clan",
    metadata,
    sqlalchemy.Column("group_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("clan_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("server", sqlalchemy.String, nullable=False),
)
member = sqlalchemy.Table(
    "member",
    metadata,
    sqlalchemy.Column(
        "group_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("clan.group_id"),
        primary_key=True,
    ),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nickname", sqlalchemy.String, nullable=False),
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
        sqlalchemy.ForeignKey("clan.group_id"),
    ),
    sqlalchemy.Column(
        "user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("member.user_id")
    ),
    sqlalchemy.Column("time", sqlalchemy.TIMESTAMP, nullable=False),
    sqlalchemy.Column("round", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("boss", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("damage", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("type", sqlalchemy.Integer, nullable=False),
    sqlite_autoincrement=True,
)
