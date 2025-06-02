CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE TYPE relationship AS ENUM ('COLABORADOR', 'PERMANENTE');

CREATE TABLE IF NOT EXISTS institution(
      institution_id uuid DEFAULT uuid_generate_v4(),
      name VARCHAR(255) NOT NULL,
      acronym VARCHAR(50) UNIQUE,
      lattes_id CHAR(16),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (institution_id)
);

CREATE TABLE IF NOT EXISTS researcher(
      researcher_id uuid NOT NULL DEFAULT uuid_generate_v4(),
      name VARCHAR(150) NOT NULL,
      lattes_id VARCHAR(20),
      institution_id uuid NOT NULL,
      extra_field VARCHAR(255),
      status BOOL NOT NULL DEFAULT True,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (researcher_id),
      UNIQUE (lattes_id, institution_id),
      FOREIGN KEY (institution_id) REFERENCES institution (institution_id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS graduate_program (
    graduate_program_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    code VARCHAR(100) UNIQUE,
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    basic_area VARCHAR(200),
    cooperation_project TEXT,
    area VARCHAR(200),
    modality VARCHAR(100),
    type VARCHAR(100),
    institution_id uuid NOT NULL,
    state VARCHAR(10),
    city VARCHAR(100),
    visible BOOLEAN DEFAULT FALSE,
    site TEXT,
    coordinator VARCHAR(200),
    email VARCHAR(200),
    start DATE,
    phone VARCHAR(50),
    periodicity VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (graduate_program_id),
    FOREIGN KEY (institution_id) REFERENCES institution (institution_id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS graduate_program_researcher(
      graduate_program_id uuid NOT NULL,
      researcher_id uuid NOT NULL,
      year INT [],
      type_ relationship,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (graduate_program_id, researcher_id),
      FOREIGN KEY (researcher_id) REFERENCES researcher (researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (graduate_program_id) REFERENCES graduate_program (graduate_program_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS graduate_program_student(
      graduate_program_id uuid NOT NULL,
      researcher_id uuid NOT NULL,
      year INT [],
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (graduate_program_id, researcher_id, year),
      FOREIGN KEY (researcher_id) REFERENCES researcher (researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (graduate_program_id) REFERENCES graduate_program (graduate_program_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS weights (
      institution_id uuid PRIMARY KEY,
      a1 numeric(20, 3),
      a2 numeric(20, 3),
      a3 numeric(20, 3),
      a4 numeric(20, 3),
      b1 numeric(20, 3),
      b2 numeric(20, 3),
      b3 numeric(20, 3),
      b4 numeric(20, 3),
      c numeric(20, 3),
      sq numeric(20, 3),
      book numeric(20, 3),
      book_chapter numeric(20, 3),
      software character varying,
      patent_granted character varying,
      patent_not_granted character varying,
      report character varying,
      f1 numeric(20, 3) DEFAULT 0,
      f2 numeric(20, 3) DEFAULT 0,
      f3 numeric(20, 3) DEFAULT 0,
      f4 numeric(20, 3) DEFAULT 0,
      f5 numeric(20, 3) DEFAULT 0,
      FOREIGN KEY (institution_id) REFERENCES institution (institution_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS roles (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      role VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS permission (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
      permission VARCHAR(255) NOT NULL,
      UNIQUE (role_id, permission)
);

CREATE TABLE IF NOT EXISTS users (
    user_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    uid VARCHAR(255) UNIQUE NOT NULL,
    photo_url TEXT,
    lattes_id VARCHAR(255),
    institution_id uuid,
    provider VARCHAR(255),
    linkedin VARCHAR(255),
    verify bool DEFAULT FALSE,
    shib_id VARCHAR(255),
    shib_code VARCHAR(255),
    birth_date VARCHAR(10),
    course_level VARCHAR(255),
    first_name VARCHAR(255),
    registration VARCHAR(255),
    gender VARCHAR(50),
    last_name VARCHAR(255),
    email_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    FOREIGN KEY (institution_id) REFERENCES institution (institution_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS users_roles (
      role_id UUID NOT NULL,
      user_id UUID NOT NULL,
      PRIMARY KEY (role_id, user_id),
      FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
      id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
      email VARCHAR(255) NOT NULL UNIQUE,
      subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    rating INTEGER CHECK (rating >= 0 AND rating <= 10) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE SCHEMA IF NOT EXISTS UFMG;

CREATE TABLE IF NOT EXISTS ufmg_admin.researcher (
    researcher_id UUID PRIMARY KEY REFERENCES researcher(researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,

    full_name VARCHAR(255),
    gender VARCHAR(255),
    status_code VARCHAR(255),
    work_regime VARCHAR(255),
    job_class CHAR(25),
    job_title VARCHAR(255),
    job_rank VARCHAR(255),
    job_reference_code VARCHAR(255),
    academic_degree VARCHAR(255),
    organization_entry_date DATE,
    last_promotion_date DATE,

    employment_status_description VARCHAR(255),
    department_name VARCHAR(255),
    career_category VARCHAR(255),
    academic_unit VARCHAR(255),
    unit_code VARCHAR(255),
    function_code VARCHAR(255),
    position_code VARCHAR(255),
    leadership_start_date DATE,
    leadership_end_date DATE,
    current_function_name VARCHAR(255),
    function_location VARCHAR(255),

    registration_number VARCHAR(200),
    ufmg_registration_number VARCHAR(200),
    semester_reference VARCHAR(6)
);

CREATE TABLE IF NOT EXISTS ufmg_admin.technician (
    technician_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    full_name VARCHAR(255),
    gender VARCHAR(255),
    status_code VARCHAR(255),
    work_regime VARCHAR(255),
    job_class CHAR(25),
    job_title VARCHAR(255),
    job_rank VARCHAR(255),
    job_reference_code VARCHAR(255),
    academic_degree VARCHAR(255),
    organization_entry_date DATE,
    last_promotion_date DATE,

    employment_status_description VARCHAR(255),
    department_name VARCHAR(255),
    career_category VARCHAR(255),
    academic_unit VARCHAR(255),
    unit_code VARCHAR(255),
    function_code VARCHAR(255),
    position_code VARCHAR(255),
    leadership_start_date DATE,
    leadership_end_date DATE,
    current_function_name VARCHAR(255),
    function_location VARCHAR(255),

    registration_number VARCHAR(255),
    ufmg_registration_number VARCHAR(255),
    semester_reference VARCHAR(6)
);

CREATE TABLE IF NOT EXISTS ufmg_admin.department (
      dep_id VARCHAR(20) PRIMARY KEY,
      org_cod VARCHAR(3),
      dep_nom VARCHAR(100),
      dep_des TEXT,
      dep_email VARCHAR(100),
      dep_site VARCHAR(100),
      dep_sigla VARCHAR(30),
      dep_tel VARCHAR(20),
      img_data BYTEA
);

CREATE TABLE IF NOT EXISTS ufmg_admin.department_technician (
      dep_id VARCHAR(20),
      technician_id uuid,
      PRIMARY KEY (dep_id, technician_id),
      FOREIGN KEY (dep_id) REFERENCES ufmg_admin.department (dep_id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (technician_id) REFERENCES ufmg_admin.technician (technician_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ufmg_admin.department_researcher (
      dep_id VARCHAR(20),
      researcher_id uuid NOT NULL,
      PRIMARY KEY (dep_id, researcher_id),
      FOREIGN KEY (dep_id) REFERENCES ufmg_admin.department (dep_id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (researcher_id) REFERENCES researcher (researcher_id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS ufmg_admin.disciplines (
      discipline_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
      dep_id VARCHAR(20),
      semester VARCHAR(20),
      department VARCHAR(255),
      academic_activity_code VARCHAR(255),
      academic_activity_name VARCHAR(255),
      academic_activity_ch VARCHAR(255),
      demanding_courses VARCHAR(255),
      oft VARCHAR(50),
      available_slots VARCHAR(50),
      occupied_slots VARCHAR(50),
      percent_occupied_slots VARCHAR(50),
      schedule VARCHAR(255),
      language VARCHAR(50),
      researcher_id uuid [],
      researcher_name VARCHAR [],
      status VARCHAR(50),
      workload VARCHAR [],
      FOREIGN KEY (dep_id) REFERENCES ufmg_admin.department (dep_id) ON DELETE SET NULL ON UPDATE CASCADE
);