BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE TYPE relationship AS ENUM ('COLABORADOR', 'PERMANENTE');

CREATE TABLE IF NOT EXISTS public.institution(
      institution_id uuid DEFAULT uuid_generate_v4(),
      name VARCHAR(255) NOT NULL,
      acronym VARCHAR(50) UNIQUE,
      lattes_id CHAR(16),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (institution_id)
);

CREATE TABLE IF NOT EXISTS public.researcher(
      researcher_id uuid NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
      name VARCHAR(150) NOT NULL,
      lattes_id VARCHAR(20),
      institution_id uuid NOT NULL,
      extra_field VARCHAR(255),
      status BOOL NOT NULL DEFAULT True,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (lattes_id, institution_id),
      FOREIGN KEY (institution_id) REFERENCES institution (institution_id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS public.graduate_program(
    graduate_program_id uuid NOT NULL DEFAULT uuid_generate_v4(),
    code VARCHAR(100),
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    basic_area VARCHAR(100), 
    cooperation_project VARCHAR(100),
    area VARCHAR(100) NOT NULL,
    modality VARCHAR(100) NOT NULL,
    TYPE VARCHAR(100) NULL,
    rating VARCHAR(5),
    institution_id uuid NOT NULL,
    state character varying(4) DEFAULT 'BA'::character varying,
    city character varying(100) DEFAULT 'Salvador'::character varying,
    region character varying(100) DEFAULT 'Nordeste'::character varying,
    url_image VARCHAR(200) NULL,
    acronym character varying(100),
    description TEXT,
    visible bool DEFAULT FALSE,
    site TEXT,
    coordinator VARCHAR(100), 
    email VARCHAR(100),
    start DATE, 
    phone VARCHAR(20), 
    periodicity VARCHAR(50), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (graduate_program_id),
    FOREIGN KEY (institution_id) REFERENCES institution (institution_id) ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS public.graduate_program_researcher(
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

CREATE TABLE IF NOT EXISTS public.graduate_program_student(
      graduate_program_id uuid NOT NULL,
      researcher_id uuid NOT NULL,
      year INT [],
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (graduate_program_id, researcher_id, year),
      FOREIGN KEY (researcher_id) REFERENCES researcher (researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (graduate_program_id) REFERENCES graduate_program (graduate_program_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS public.weights (
      institution_id uuid,
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
      PRIMARY KEY (institution_id),
      FOREIGN KEY (institution_id) REFERENCES public.institution (institution_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS public.roles (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      role VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.permission (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      role_id UUID REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
      permission VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.incite_graduate_program(
      incite_graduate_program_id uuid NOT NULL DEFAULT uuid_generate_v4(),
      name VARCHAR(255) NOT NULL,
      description VARCHAR(500) NULL,
      link VARCHAR(500) NULL,
      institution_id uuid NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      visible bool DEFAULT FALSE,
      PRIMARY KEY (incite_graduate_program_id),
      FOREIGN KEY (institution_id) REFERENCES institution (institution_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS public.incite_graduate_program_researcher(
      incite_graduate_program_id uuid NOT NULL,
      researcher_id uuid NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (incite_graduate_program_id, researcher_id),
      FOREIGN KEY (researcher_id) REFERENCES researcher (researcher_id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (incite_graduate_program_id) REFERENCES incite_graduate_program (incite_graduate_program_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS public.users (
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
      PRIMARY KEY (user_id),
      FOREIGN KEY (institution_id) REFERENCES public.institution (institution_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS public.users_roles (
      role_id UUID NOT NULL,
      user_id UUID NOT NULL,
      PRIMARY KEY (role_id, user_id),
      FOREIGN KEY (role_id) REFERENCES public.roles (id) ON DELETE CASCADE ON UPDATE CASCADE,
      FOREIGN KEY (user_id) REFERENCES public.users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS public.newsletter_subscribers (
      id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
      email VARCHAR(255) NOT NULL UNIQUE,
      subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    rating INTEGER CHECK (rating >= 0 AND rating <= 10) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE "graduation_program_guidance" (
	id UUID NOT NULL DEFAULT uuid_generate_v4(),
	student_researcher_id UUID NOT NULL,
	supervisor_researcher_id UUID NOT NULL,
	co_supervisor_researcher_id UUID NOT NULL,
	graduate_program_id UUID NOT NULL,
	start_date  DATE NOT NULL,
	planned_date_project DATE NOT NULL,
	done_date_project DATE NULL,
	planned_date_qualification DATE NOT NULL,
	done_date_qualification DATE NULL,
	planned_date_conclusion DATE NOT NULL,
	done_date_conclusion DATE NULL,
	created_at TIMESTAMP NOT NULL DEFAULT now(),
	updated_at TIMESTAMP NULL,
	deleted_at TIMESTAMP NULL,
	PRIMARY KEY ("id"),
	CONSTRAINT "FKsudent_researcher" FOREIGN KEY ("student_researcher_id") REFERENCES "researcher" ("researcher_id") ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT "FKsupervisor_researcher" FOREIGN KEY ("supervisor_researcher_id") REFERENCES "researcher" ("researcher_id") ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT "FKco_supervisor_researcher" FOREIGN KEY ("co_supervisor_researcher_id") REFERENCES "researcher" ("researcher_id") ON UPDATE CASCADE ON DELETE CASCADE,
   CONSTRAINT "FKgraduate_program" FOREIGN KEY ("graduate_program_id") REFERENCES "graduate_program" ("graduate_program_id") ON UPDATE CASCADE ON DELETE CASCADE
);
---

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
    semester_reference VARCHAR(6)                
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
    semester_reference VARCHAR(6)
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
      PRIMARY KEY (dep_id, id),
      FOREIGN KEY (dep_id) REFERENCES ufmg.departament (dep_id) ON DELETE CASCADE ON UPDATE CASCADE
);

COMMIT;

ROLLBACK;