BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

--- Gerenciamento da conta

CREATE TYPE role_type AS ENUM ('ADMIN', 'DEFAULT');
CREATE TYPE relationship AS ENUM ('COLABORADOR', 'PERMANENTE');

--- Bloco 1

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    orcid_id CHAR(20),
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role role_type NOT NULL DEFAULT 'DEFAULT',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

--- Bloco 2

CREATE TABLE public.institution (
  institution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  acronym VARCHAR(16) UNIQUE,
  lattes_id VARCHAR(16),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP
);

--- Bloco 3

CREATE TABLE public.roles (
    role_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
);
CREATE TABLE public.permissions (
    permission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP
);
CREATE TABLE public.user_roles (
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES public.users (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (role_id) REFERENCES public.roles (role_id) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE TABLE public.role_permissions (
    role_id UUID NOT NULL,
    permission_id UUID NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES public.roles (role_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES public.permissions (permission_id) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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

    FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS feature.collection_entries(
    collection_id UUID REFERENCES feature.collection(collection_id),
    entry_id UUID NOT NULL,
    type VARCHAR(255) NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES feature.collection(collection_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS feature.stars(
    user_id UUID NOT NULL,
    entry_id UUID NOT NULL,
    type VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

---

COMMIT;

ROLLBACK;