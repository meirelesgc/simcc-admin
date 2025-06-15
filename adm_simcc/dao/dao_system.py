import pandas as pd

from ..dao import Connection
from ..models import FeedbackSchema, UserModel

adm_database = Connection()


def create_user(User: UserModel):
    user_columns = [
        "user_id",
        "display_name",
        "email",
        "uid",
        "photo_url",
        "lattes_id",
        "institution_id",
        "provider",
        "linkedin",
        "verify",
    ]

    SCRIPT_SQL = """
    SELECT user_id, display_name, email, uid, photo_url, lattes_id,
           institution_id, provider, linkedin, verify
    FROM users
    WHERE unaccent(display_name) ILIKE unaccent(%(display_name)s)
    LIMIT 1;
    """
    params = {"display_name": User.displayName}
    existing_user = adm_database.select(SCRIPT_SQL, params)

    if existing_user:
        df = pd.DataFrame(existing_user, columns=user_columns)
        return df.to_dict(orient="records")[0]

    SCRIPT_SQL = """
    SELECT lattes_id, institution_id FROM researcher WHERE
    unaccent(name) ILIKE unaccent(%(display_name)s) LIMIT 1;
    """
    researcher = adm_database.select(SCRIPT_SQL, params)

    if researcher:
        User.lattes_id, User.institution_id = researcher[0]
    else:
        User.lattes_id, User.institution_id = None, None

    params = User.model_dump()

    SCRIPT_SQL = """
        INSERT INTO users (display_name, email, uid, photo_url, linkedin,
            provider, lattes_id, birth_date, course_level, first_name,
            registration, gender, last_name, email_status, visible_email,
            institution_id)
        VALUES (%(displayName)s, %(email)s, %(uid)s, %(photoURL)s, %(linkedin)s,
            %(provider)s, %(lattes_id)s, %(birth_date)s, %(course_level)s,
            %(first_name)s, %(registration)s, %(gender)s, %(last_name)s,
            %(email_status)s, %(visible_email)s, %(institution_id)s);
    """
    adm_database.exec(SCRIPT_SQL, params)

    SCRIPT_SQL = """
    SELECT user_id, display_name, email, uid, photo_url, lattes_id,
           institution_id, provider, linkedin, verify
    FROM users
    WHERE uid = %(uid)s
    LIMIT 1;
    """
    user_created = adm_database.select(SCRIPT_SQL, {"uid": params["uid"]})
    df = pd.DataFrame(user_created, columns=user_columns)
    return df.to_dict(orient="records")


def select_user(uid):
    SCRIPT_SQL = """
        WITH dp_menager AS (
            SELECT UNNEST(menagers) AS email , COUNT(*) AS among
            FROM ufmg.departament
            GROUP BY menagers
        ),
        gp_menager AS (
            SELECT UNNEST(menagers) AS email , COUNT(*) AS among
            FROM graduate_program
            GROUP BY menagers
        )
        SELECT u.user_id, u.display_name, u.email, u.uid, u.photo_url, u.linkedin,
            u.provider, u.lattes_id, u.institution_id, u.shib_id, u.shib_code,
            u.birth_date, u.course_level, u.first_name, u.registration, u.gender, 
            u.last_name, u.email_status, rr.name, u.verify, u.visible_email, 
            gp.among, dp.among
        FROM users u
            LEFT JOIN researcher rr
                ON rr.lattes_id = u.lattes_id
            LEFT JOIN gp_menager gp
                ON gp.email = u.email
            LEFT JOIN dp_menager dp
                ON dp.email = u.email
        WHERE u.uid = %(uid)s
        """
    registry = adm_database.select(SCRIPT_SQL, {"uid": uid})
    print(SCRIPT_SQL, {"uid": uid})

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
            "shib_id",
            "shib_code",
            "birth_date",
            "course_level",
            "first_name",
            "registration",
            "gender",
            "last_name",
            "email_status",
            "researcger_name",
            "verify",
            "visible_email",
            "gp_count",
            "dp_count",
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
            u.display_name,
            u.email,
            u.uid,
            u.photo_url,
            u.linkedin,
            u.provider,
            u.lattes_id,
            u.institution_id,
            u.shib_id,
            u.shib_code,
            u.birth_date,
            u.course_level,
            u.first_name,
            u.registration,
            u.gender,
            u.last_name,
            u.email_status,
            rr.name,
            u.verify,
            u.visible_email
        FROM users u
        LEFT JOIN researcher rr ON rr.lattes_id = u.lattes_id
        GROUP BY
            u.user_id,
            u.display_name,
            u.email,
            u.uid,
            u.photo_url,
            u.linkedin,
            u.provider,
            u.lattes_id,
            u.institution_id,
            u.shib_id,
            u.shib_code,
            u.birth_date,
            u.course_level,
            u.first_name,
            u.registration,
            u.gender,
            u.last_name,
            u.email_status,
            rr.name,
            u.verify,
            u.visible_email;
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
            "shib_id",
            "shib_code",
            "birth_date",
            "course_level",
            "first_name",
            "registration",
            "gender",
            "last_name",
            "email_status",
            "researcger_name",
            "verify",
            "visible_email",
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


def update_user(user):  # noqa: PLR0912
    SCRIPT_SQL = """
    UPDATE users
    SET
    """

    if "linkedin" in user:
        SCRIPT_SQL += "linkedin = %(linkedin)s,"
    if "lattes_id" in user:
        SCRIPT_SQL += "lattes_id = %(lattes_id)s,"
    if "institution_id" in user:
        SCRIPT_SQL += "institution_id = %(institution_id)s,"
    if "verify" in user:
        SCRIPT_SQL += "verify = %(verify)s,"
    if "email" in user:
        SCRIPT_SQL += "email = %(email)s,"
    if "photo_url" in user:
        SCRIPT_SQL += "photo_url = %(photo_url)s,"
    if "provider" in user:
        SCRIPT_SQL += "provider = %(provider)s,"
    if "shib_id" in user:  # Adicionado
        SCRIPT_SQL += "shib_id = %(shib_id)s,"
    if "shib_code" in user:  # Adicionado
        SCRIPT_SQL += "shib_code = %(shib_code)s,"
    if "birth_date" in user:  # Adicionado
        SCRIPT_SQL += "birth_date = %(birth_date)s,"
    if "course_level" in user:  # Adicionado
        SCRIPT_SQL += "course_level = %(course_level)s,"
    if "first_name" in user:  # Adicionado
        SCRIPT_SQL += "first_name = %(first_name)s,"
    if "registration" in user:  # Adicionado
        SCRIPT_SQL += "registration = %(registration)s,"
    if "gender" in user:  # Adicionado
        SCRIPT_SQL += "gender = %(gender)s,"
    if "last_name" in user:  # Adicionado
        SCRIPT_SQL += "last_name = %(last_name)s,"
    if "email_status" in user:  # Adicionado
        SCRIPT_SQL += "email_status = %(email_status)s,"
    if "visible_email" in user:  # Adicionado
        SCRIPT_SQL += "visible_email = %(visible_email)s,"

    SCRIPT_SQL = f" {SCRIPT_SQL[:-1]} "
    SCRIPT_SQL += "WHERE uid = %(uid)s"

    adm_database.exec(SCRIPT_SQL, user)


def list_users():
    SCRIPT_SQL = """
        SELECT
            u.user_id,
            u.display_name,
            u.email,
            u.uid,
            u.photo_url,
            u.linkedin,
            u.provider,
            u.lattes_id,
            u.institution_id,
            u.shib_id,
            u.shib_code,
            u.birth_date,
            u.course_level,
            u.first_name,
            u.registration,
            u.gender,
            u.last_name,
            u.email_status,
            jsonb_agg(jsonb_build_object('role', rl.role, 'role_id', rl.id)) AS roles,
            u.verify,
            u.visible_email
        FROM users u
        LEFT JOIN users_roles ur ON u.user_id = ur.user_id
        LEFT JOIN roles rl ON rl.id = ur.role_id
        GROUP BY
            u.user_id,
            u.display_name,
            u.email,
            u.uid,
            u.photo_url
            u.linkedin,
            u.provider,
            u.lattes_id,
            u.institution_id,
            u.shib_id,
            u.shib_code,
            u.birth_date,
            u.course_level,
            u.first_name,
            u.registration,
            u.gender,
            u.last_name,
            u.email_status,
            u.verify,
            u.visible_email;
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
            "shib_id",
            "shib_code",
            "birth_date",
            "course_level",
            "first_name",
            "registration",
            "gender",
            "last_name",
            "email_status",
            "verify",
            "visible_email",
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


def list_feedback():
    SCRIPT_SQL = """
        SELECT id, name,  email,  rating,  description, created_at
        FROM public.feedback;
        """
    registry = adm_database.select(SCRIPT_SQL)
    dataframe = pd.DataFrame(
        registry,
        columns=["id", "name", "email", "rating", "description", "created_at"],
    )
    return dataframe.to_dict(orient="records")


def delete_feedback(feedback_id):
    SCRIPT_SQL = """
        DELETE FROM public.feedback
        WHERE id=%(feedback_id)s;
        """
    adm_database.exec(SCRIPT_SQL, {"feedback_id": feedback_id})
