import pandas as pd

from ..dao import Connection
from ..models import FeedbackSchema, UserModel

adm_database = Connection()


def create_user(User: UserModel):
    SCRIPT_SQL = """
    SELECT lattes_id FROM researcher WHERE
    unaccent(name) ILIKE unaccent(%s) LIMIT 1;
    """

    lattes_id = adm_database.select(SCRIPT_SQL, [User.displayName])

    if lattes_id:
        User.lattes_id = lattes_id[0][0]
    SCRIPT_SQL = """
        INSERT INTO users (display_name, email, uid, photo_url, linkedin, provider, lattes_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
    adm_database.exec(
        SCRIPT_SQL,
        [
            User.displayName,
            User.email,
            User.uid,
            str(User.photoURL) or str(),
            User.linkedin or str(),
            User.provider or str(),
            User.lattes_id or str(),
        ],
    )


def select_user(uid):
    SCRIPT_SQL = """
        SELECT
            u.user_id,
            display_name,
            email,
            uid,
            photo_url,
            linkedin,
            provider,
            u.lattes_id,
            u.institution_id,
            rr.name,
            u.verify
        FROM users u
        LEFT JOIN researcher rr ON rr.lattes_id = u.lattes_id
        WHERE uid = %s
        GROUP BY
            u.user_id,
            display_name,
            email, uid,
            photo_url,
            u.institution_id,
            rr.name;
        """
    registry = adm_database.select(SCRIPT_SQL, [uid])

    data_frame = pd.DataFrame(
        registry,
        columns=[
            "user_id",
            "display_name",
            "email",
            "uid",
            "photo_url",
            "linkedin",
            "provider",
            "lattes_id",
            "institution_id",
            "researcger_name",
            "verify",
        ],
    )

    data_frame = data_frame.merge(users_roles(), on="user_id", how="left")
    data_frame = data_frame.merge(
        users_graduate_program(), on="lattes_id", how="left"
    )
    data_frame = data_frame.merge(
        users_departaments(), on="lattes_id", how="left"
    )

    data_frame.fillna("", inplace=True)
    return data_frame.to_dict(orient="records")


def list_all_users():
    SCRIPT_SQL = """
        SELECT 
            u.user_id,
            display_name,
            email,
            uid,
            photo_url,
            linkedin,
            provider,
            u.lattes_id,
            u.institution_id,
            rr.name,
            u.verify
        FROM users u
        LEFT JOIN researcher rr ON rr.lattes_id = u.lattes_id
        GROUP BY u.user_id, display_name, email, uid, photo_url, u.institution_id, rr.name;
        """
    registry = adm_database.select(SCRIPT_SQL)

    data_frame = pd.DataFrame(
        registry,
        columns=[
            "user_id",
            "display_name",
            "email",
            "uid",
            "photo_url",
            "linkedin",
            "provider",
            "lattes_id",
            "institution_id",
            "researcger_name",
            "verify",
        ],
    )

    data_frame = data_frame.merge(users_roles(), on="user_id", how="left")
    data_frame = data_frame.merge(
        users_graduate_program(), on="lattes_id", how="left"
    )
    data_frame = data_frame.merge(
        users_departaments(), on="lattes_id", how="left"
    )

    data_frame.fillna("", inplace=True)
    return data_frame.to_dict(orient="records")


def update_user(user):
    SCRIPT_SQL = """
    UPDATE users
    SET
    """

    if user.get("linkedin"):
        SCRIPT_SQL += "linkedin = %(linkedin)s,"
    if user.get("lattes_id"):
        SCRIPT_SQL += "lattes_id = %(lattes_id)s,"
    if user.get("institution_id"):
        SCRIPT_SQL += "institution_id = %(institution_id)s,"
    if user.get("verify"):
        SCRIPT_SQL += "verify = %(verify)s,"
    if user.get("email"):
        SCRIPT_SQL += "email = %(email)s,"
    if user.get("photo_url"):
        SCRIPT_SQL += "photo_url = %(photo_url)s,"
    if user.get("provider"):
        SCRIPT_SQL += "provider = %(provider)s,"

    SCRIPT_SQL = f" {SCRIPT_SQL[:-1]} "
    SCRIPT_SQL += "WHERE uid = %(uid)s"

    adm_database.exec(SCRIPT_SQL, user)


def list_users():
    SCRIPT_SQL = """
        SELECT
            u.user_id, display_name, email,
            jsonb_agg(jsonb_build_object('role', rl.role, 'role_id', rl.id)) AS roles,
            photo_url, verify
        FROM users u
        LEFT JOIN users_roles ur ON u.user_id = ur.user_id
        LEFT JOIN roles rl ON rl.id = ur.role_id
        GROUP BY u.user_id;
        """
    registry = adm_database.select(SCRIPT_SQL)
    data_frame = pd.DataFrame(
        registry,
        columns=[
            "user_id",
            "display_name",
            "email",
            "roles",
            "photo_url",
            "verify",
        ],
    )

    return data_frame.to_dict(orient="records")


def create_new_role(role):
    SCRIPT_SQL = """
        INSERT INTO roles (role)
        VALUES (%s)
        """
    adm_database.exec(SCRIPT_SQL, [role[0]["role"]])


def view_roles():
    SCRIPT_SQL = """
        SELECT id, role
        FROM roles
        """
    reg = adm_database.select(SCRIPT_SQL)
    data_frame = pd.DataFrame(reg, columns=["id", "role"])
    return data_frame.to_dict(orient="records")


def update_role(role):
    SCRIPT_SQL = """
        UPDATE roles
        SET role = %s
        WHERE id = %s;
        """
    adm_database.exec(SCRIPT_SQL, [role[0]["role"], role[0]["id"]])


def delete_role(role):
    SCRIPT_SQL = """
        DELETE FROM roles
        WHERE id = %s;
        """
    adm_database.exec(SCRIPT_SQL, [role[0]["id"]])


def create_new_permission(permission):
    SCRIPT_SQL = """
        INSERT INTO permission (role_id, permission)
        VALUES (%s, %s);
        """
    adm_database.exec(
        SCRIPT_SQL, [permission[0]["role_id"], permission[0]["permission"]]
    )


def permissions_view(role_id):
    SCRIPT_SQL = """
    SELECT id, permission AS permission
    FROM permission
    WHERE role_id = %s
    """
    reg = adm_database.select(SCRIPT_SQL, [role_id])
    data_frame = pd.DataFrame(reg, columns=["id", "permission"])
    return data_frame.to_dict(orient="records")


def update_permission(permission):
    SCRIPT_SQL = """
        UPDATE permission
        SET permission = %s
        WHERE id = %s;
        """
    adm_database.exec(
        SCRIPT_SQL, [permission[0]["permission"], permission[0]["id"]]
    )


def delete_permission(permission):
    SCRIPT_SQL = """
        DELETE FROM permission
        WHERE id = %s;
        """
    adm_database.exec(SCRIPT_SQL, [permission[0]["id"]])


def assign_user(user):
    SCRIPT_SQL = """
        UPDATE users SET
        institution_id = %s
        WHERE user_id = %s;

        INSERT INTO users_roles (role_id, user_id)
        VALUES (%s, %s);
        """
    adm_database.exec(
        SCRIPT_SQL,
        [
            user[0]["institution_id"],
            user[0]["user_id"],
            user[0]["role_id"],
            user[0]["user_id"],
        ],
    )


def view_user_roles(uid, role_id):
    SCRIPT_SQL = """
        SELECT
            r.id,
            p.permission
        FROM
            users_roles ur
            LEFT JOIN roles r ON r.id = ur.role_id
            LEFT JOIN permission p ON p.role_id = ur.role_id
            LEFT JOIN users u ON u.user_id = ur.user_id
        WHERE u.uid = %s AND r.id = %s
        """

    reg = adm_database.select(SCRIPT_SQL, [uid, role_id])
    data_frame = pd.DataFrame(reg, columns=["role_id", "permissions"])
    return data_frame.to_dict(orient="records")


def unassign_user(user):
    SCRIPT_SQL = """
        DELETE FROM users_roles
        WHERE role_id = %s AND user_id = %s;
        """
    adm_database.exec(SCRIPT_SQL, [user[0]["role_id"], user[0]["user_id"]])


def users_roles():
    SCRIPT_SQL = """
        SELECT
            u.user_id,
            jsonb_agg(jsonb_build_object('id', r.id, 'role_id', r.role)) AS roles
        FROM users u
        LEFT JOIN users_roles ur ON ur.user_id = u.user_id
        LEFT JOIN roles r ON r.id = ur.role_id
        GROUP BY u.user_id
        """
    registry = adm_database.select(SCRIPT_SQL)

    data_frame = pd.DataFrame(registry, columns=["user_id", "roles"])

    return data_frame


def users_graduate_program():
    SCRIPT_SQL = """
        SELECT
            r.lattes_id,
            jsonb_agg(jsonb_build_object('graduate_program_id', gp.graduate_program_id, 'name', gp.name)) AS graduate_program
        FROM graduate_program_researcher gpr
        LEFT JOIN graduate_program gp ON gp.graduate_program_id = gpr.graduate_program_id
        LEFT JOIN researcher r ON gpr.researcher_id = r.researcher_id
        GROUP BY r.lattes_id
        """
    registry = adm_database.select(SCRIPT_SQL)

    data_frame = pd.DataFrame(
        registry, columns=["lattes_id", "graduate_program"]
    )

    return data_frame


def users_departaments():
    SCRIPT_SQL = """
        SELECT
            r.lattes_id,
            jsonb_agg(jsonb_build_object('name', d.dep_nom, 'dep_id', d.dep_id)) AS departament
        FROM ufmg.departament_researcher dr
        LEFT JOIN ufmg.departament d ON d.dep_id = dr.dep_id
        LEFT JOIN researcher r ON r.researcher_id = dr.researcher_id
        GROUP BY r.lattes_id
        """
    registry = adm_database.select(SCRIPT_SQL)

    data_frame = pd.DataFrame(registry, columns=["lattes_id", "departament"])

    return data_frame


def add_email(email):
    SCRIPT_SQL = """
        INSERT INTO newsletter_subscribers (email)
        VALUES (%s);
    """
    adm_database.exec(SCRIPT_SQL, (email,))


def select_email():
    SCRIPT_SQL = """
        SELECT email, subscribed_at
        FROM newsletter_subscribers;
    """
    registry = adm_database.select(SCRIPT_SQL)
    dataframe = pd.DataFrame(registry, columns=["email", "subscribed_at"])
    return dataframe.to_dict(orient="records")


def delete_email(email):
    SCRIPT_SQL = """
        DELETE FROM newsletter_subscribers
        WHERE email = %s;
    """
    adm_database.exec(SCRIPT_SQL, (email,))


def add_feedback(feedback: FeedbackSchema):
    SCRIPT_SQL = """
        INSERT INTO public.feedback(name, email, rating, description)
        VALUES (%(name)s, %(email)s, %(rating)s, %(description)s);
        """
    adm_database.exec(SCRIPT_SQL, feedback.model_dump())


def add_group_producion(producion):
    SCRIPT_SQL = """
        INSERT INTO public.research_group_production
        (group_id, type, production_id)
        VALUES (%(group_id)s, %(type)s, %(production_id)s);
        """
    adm_database.exec(SCRIPT_SQL, producion)
