BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

--- Gerenciamento da conta

CREATE TYPE role_type AS ENUM ('ADMIN', 'DEFAULT');

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    orcid_id CHAR(20),
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role role_type NOT NULL DEFAULT 'DEFAULT',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TYPE relationship AS ENUM ('COLABORADOR', 'PERMANENTE');

CREATE TABLE public.institution (
  institution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  acronym VARCHAR(16) UNIQUE,
  lattes_id VARCHAR(16),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP
);

CREATE TABLE public.researcher (
  researcher_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(150) NOT NULL,
  lattes_id VARCHAR(20),
  institution_id UUID NOT NULL,
  extra_field VARCHAR(255),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP,
  UNIQUE (lattes_id, institution_id),
  FOREIGN KEY (institution_id) REFERENCES public.institution(institution_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE public.graduate_program (
  graduate_program_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code VARCHAR(100),
  name VARCHAR(100) NOT NULL,
  name_en VARCHAR(100),
  basic_area VARCHAR(100),
  cooperation_project VARCHAR(100),
  area VARCHAR(100) NOT NULL,
  modality VARCHAR(100) NOT NULL,
  program_type VARCHAR(100),
  rating VARCHAR(5),
  institution_id UUID NOT NULL,
  state VARCHAR(4) DEFAULT 'BA',
  city VARCHAR(100) DEFAULT 'Salvador',
  region VARCHAR(100) DEFAULT 'Nordeste',
  url_image VARCHAR(200),
  acronym VARCHAR(100),
  description TEXT,
  is_visible BOOLEAN DEFAULT FALSE,
  site TEXT,
  coordinator VARCHAR(100),
  email VARCHAR(100),
  start DATE,
  phone VARCHAR(20),
  periodicity VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP,
  FOREIGN KEY (institution_id) REFERENCES public.institution(institution_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE public.graduate_program_researcher (
  graduate_program_id UUID NOT NULL,
  researcher_id UUID NOT NULL,
  year INT[],
  relationship_type relationship,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP,
  PRIMARY KEY (graduate_program_id, researcher_id),
  FOREIGN KEY (researcher_id) REFERENCES public.researcher(researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (graduate_program_id) REFERENCES public.graduate_program(graduate_program_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE public.graduate_program_student (
  graduate_program_id UUID NOT NULL,
  researcher_id UUID NOT NULL,
  year INT[],
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP,
  PRIMARY KEY (graduate_program_id, researcher_id, year),
  FOREIGN KEY (researcher_id) REFERENCES public.researcher(researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (graduate_program_id) REFERENCES public.graduate_program(graduate_program_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE public.weights (
  institution_id UUID PRIMARY KEY,
  a1 NUMERIC(20, 3),
  a2 NUMERIC(20, 3),
  a3 NUMERIC(20, 3),
  a4 NUMERIC(20, 3),
  b1 NUMERIC(20, 3),
  b2 NUMERIC(20, 3),
  b3 NUMERIC(20, 3),
  b4 NUMERIC(20, 3),
  c NUMERIC(20, 3),
  sq NUMERIC(20, 3),
  book NUMERIC(20, 3),
  book_chapter NUMERIC(20, 3),
  software VARCHAR,
  patent_granted VARCHAR,
  patent_not_granted VARCHAR,
  report VARCHAR,
  f1 NUMERIC(20, 3) DEFAULT 0,
  f2 NUMERIC(20, 3) DEFAULT 0,
  f3 NUMERIC(20, 3) DEFAULT 0,
  f4 NUMERIC(20, 3) DEFAULT 0,
  f5 NUMERIC(20, 3) DEFAULT 0,
  FOREIGN KEY (institution_id) REFERENCES public.institution(institution_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE public.roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role VARCHAR(255) NOT NULL
);

CREATE TABLE public.permission (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_id UUID REFERENCES public.roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
  permission VARCHAR(255) NOT NULL
);

-- CREATE TABLE public.users (
--   user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--   display_name VARCHAR(255) NOT NULL,
--   email VARCHAR(255) UNIQUE NOT NULL,
--   uid VARCHAR(255) UNIQUE NOT NULL,
--   photo_url TEXT,
--   lattes_id VARCHAR(255),
--   institution_id UUID,
--   provider VARCHAR(255),
--   linkedin VARCHAR(255),
--   is_verified BOOLEAN DEFAULT FALSE,
--   FOREIGN KEY (institution_id) REFERENCES public.institution(institution_id) ON DELETE SET NULL ON UPDATE CASCADE
-- );

-- CREATE TABLE public.users_roles (
--   role_id UUID NOT NULL,
--   user_id UUID NOT NULL,
--   PRIMARY KEY (role_id, user_id),
--   FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
--   FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
-- );

CREATE TABLE public.newsletter_subscribers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) NOT NULL UNIQUE,
  subscribed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL,
  rating INTEGER CHECK (rating >= 0 AND rating <= 10) NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE public.graduation_program_guidance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_researcher_id UUID NOT NULL,
  supervisor_researcher_id UUID NOT NULL,
  co_supervisor_researcher_id UUID NOT NULL,
  graduate_program_id UUID NOT NULL,
  start_date DATE NOT NULL,
  planned_date_project DATE NOT NULL,
  done_date_project DATE,
  planned_date_qualification DATE NOT NULL,
  done_date_qualification DATE,
  planned_date_conclusion DATE NOT NULL,
  done_date_conclusion DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP,
  deleted_at TIMESTAMP,
  FOREIGN KEY (student_researcher_id) REFERENCES public.researcher(researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (supervisor_researcher_id) REFERENCES public.researcher(researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (co_supervisor_researcher_id) REFERENCES public.researcher(researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (graduate_program_id) REFERENCES public.graduate_program(graduate_program_id) ON DELETE CASCADE ON UPDATE CASCADE
);

---

CREATE SCHEMA IF NOT EXISTS feature;

CREATE TABLE IF NOT EXISTS feature.collection (
    collection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    visible BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS feature.collection_entries(
    collection_id UUID REFERENCES feature.collection(collection_id),
    entry_id UUID NOT NULL,
    type VARCHAR(255) NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES feature.collection(collection_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE SCHEMA IF NOT EXISTS ufmg;


CREATE TABLE IF NOT EXISTS ufmg.researcher (
    researcher_id UUID PRIMARY KEY REFERENCES public.researcher(researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Campos comuns
    full_name VARCHAR(255),
    gender VARCHAR(255),
    status_code VARCHAR(255),
    work_regime VARCHAR(255),
    job_class CHAR,
    job_title VARCHAR(255),
    job_rank VARCHAR(255),
    job_reference_code VARCHAR(255),
    academic_degree VARCHAR(255),
    organization_entry_date DATE,
    last_promotion_date DATE,
    
    -- Novos campos
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
    
    -- Campos que estavam só na tabela antiga
    registration_number VARCHAR(200),            
    ufmg_registration_number VARCHAR(200),       
    semester_reference VARCHAR(6),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP     
);


CREATE TABLE IF NOT EXISTS ufmg.technician (
    technician_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Campos comuns
    full_name VARCHAR(255),
    gender VARCHAR(255),
    status_code VARCHAR(255),
    work_regime VARCHAR(255),
    job_class CHAR,
    job_title VARCHAR(255),
    job_rank VARCHAR(255),
    job_reference_code VARCHAR(255),
    academic_degree VARCHAR(255),
    organization_entry_date DATE,
    last_promotion_date DATE,

    -- Novos campos
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

    -- Campos antigos
    registration_number VARCHAR(255),
    ufmg_registration_number VARCHAR(255),
    semester_reference VARCHAR(6),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ufmg.departament (
    dep_id VARCHAR(20),
    org_cod VARCHAR(3),
    dep_nom VARCHAR(100),
    dep_des TEXT,
    dep_email VARCHAR(100),
    dep_site VARCHAR(100),
    dep_sigla VARCHAR(30),
    dep_tel VARCHAR(20),
    img_data BYTEA,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,

    PRIMARY KEY (dep_id)
);

CREATE TABLE IF NOT EXISTS ufmg.departament_technician (
      dep_id character varying(10),
      technician_id uuid,
      PRIMARY KEY (dep_id, technician_id),
      FOREIGN KEY (dep_id) REFERENCES ufmg.departament (dep_id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (technician_id) REFERENCES ufmg.technician (technician_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ufmg.departament_researcher (
      dep_id VARCHAR(20),
      researcher_id uuid NOT NULL,
      PRIMARY KEY (dep_id, researcher_id),
      FOREIGN KEY (dep_id) REFERENCES ufmg.departament (dep_id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (researcher_id) REFERENCES public.researcher (researcher_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS ufmg.disciplines (
    dep_id VARCHAR(20),
    id VARCHAR(20),
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

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,

    PRIMARY KEY (dep_id, id),
    FOREIGN KEY (dep_id) REFERENCES ufmg.departament (dep_id) ON DELETE CASCADE ON UPDATE CASCADE
);



COMMIT;

ROLLBACK;