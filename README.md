CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    surname VARCHAR NOT NULL,
    father_name VARCHAR NOT NULL,
    fin_kod VARCHAR(7) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    birth_date TIMESTAMP NOT NULL,
    image VARCHAR,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT uq_user_fin_kod UNIQUE (fin_kod),
    CONSTRAINT uq_user_email UNIQUE (email)
);

CREATE TABLE auth (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
    role INTEGER NOT NULL DEFAULT 2,  -- 0: dev, 1: admin, 2: user
    password VARCHAR(255),
    approved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    CONSTRAINT uq_auth_fin_kod UNIQUE (fin_kod),
    CONSTRAINT uq_auth_email UNIQUE (email)
);

-- otp
CREATE TABLE otp (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL,
    otp VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- bios
CREATE TABLE bios (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL UNIQUE REFERENCES auth(fin_kod) ON DELETE CASCADE,
    bio_code TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- bio_translations
CREATE TABLE bio_translations (
    id SERIAL PRIMARY KEY,
    lang_code VARCHAR(2) NOT NULL,
    bio_code TEXT NOT NULL REFERENCES bios(bio_code) ON DELETE CASCADE,
    bio_field TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ
);

-- articles
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL REFERENCES auth(fin_kod) ON DELETE CASCADE,
    article_code TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- article_translations
CREATE TABLE article_translations (
    id SERIAL PRIMARY KEY,
    lang_code VARCHAR(2) NOT NULL,
    article_code TEXT NOT NULL REFERENCES articles(article_code) ON DELETE CASCADE,
    article_field TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

-- publications
CREATE TABLE publications (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL REFERENCES auth(fin_kod) ON DELETE CASCADE,
    publication_code TEXT NOT NULL UNIQUE,
    publication_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- publication_translations
CREATE TABLE publication_translations (
    id SERIAL PRIMARY KEY,
    lang_code VARCHAR(2) NOT NULL,
    publication_code TEXT NOT NULL REFERENCES publications(publication_code) ON DELETE CASCADE,
    publication_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

-- scientific_names
CREATE TABLE scientific_names (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL UNIQUE REFERENCES auth(fin_kod) ON DELETE CASCADE,
    scientific_name_code INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- scientific_name_translations
CREATE TABLE scientific_name_translations (
    id SERIAL PRIMARY KEY,
    lang_code VARCHAR(2) NOT NULL,
    scientific_name_code INTEGER NOT NULL REFERENCES scientific_names(scientific_name_code) ON DELETE CASCADE,
    scientific_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ
);

-- education
CREATE TABLE education (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR NOT NULL UNIQUE,
    edu_code VARCHAR(7) NOT NULL UNIQUE,
    start_date INTEGER NOT NULL,
    end_date INTEGER,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- education_translations
CREATE TABLE education_translations (
    id SERIAL PRIMARY KEY,
    edu_code VARCHAR(7) NOT NULL,
    lang_code VARCHAR(2) NOT NULL,
    title VARCHAR(255) NOT NULL,
    university VARCHAR(255) NOT NULL
);

-- experience
CREATE TABLE experience (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL,
    exp_code VARCHAR(7) NOT NULL UNIQUE,
    start_date INTEGER NOT NULL,
    end_date INTEGER,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- experience_translations
CREATE TABLE experience_translations (
    id SERIAL PRIMARY KEY,
    exp_code VARCHAR(7) NOT NULL,
    lang_code VARCHAR(2) NOT NULL,
    title VARCHAR NOT NULL,
    university VARCHAR NOT NULL
);

-- research_areas
CREATE TABLE research_areas (
    id SERIAL PRIMARY KEY,
    area_code VARCHAR NOT NULL UNIQUE,
    fin_kod VARCHAR(7) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- research_areas_translations
CREATE TABLE research_areas_translations (
    id SERIAL PRIMARY KEY,
    area_code VARCHAR NOT NULL UNIQUE,
    lang_code VARCHAR(2) NOT NULL,
    area VARCHAR NOT NULL
);

-- language
CREATE TABLE language (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL,
    lang_serial VARCHAR,
    language_short_name VARCHAR NOT NULL,
    language_level VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- language_translations
CREATE TABLE language_translations (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL,
    lang_code VARCHAR(2) NOT NULL,
    lang_serial VARCHAR,
    language_name VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- work
CREATE TABLE work (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL,
    work_serial VARCHAR,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- work_translations
CREATE TABLE work_translations (
    id SERIAL PRIMARY KEY,
    work_serial VARCHAR,
    work_place VARCHAR NOT NULL,
    duty VARCHAR,
    language_code VARCHAR(2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- international_coorperations
CREATE TABLE international_coorperations (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL,
    inter_corp_code VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- international_coorperations_translations
CREATE TABLE international_coorperations_translations (
    id SERIAL PRIMARY KEY,
    language_code VARCHAR(2) NOT NULL,
    inter_corp_code VARCHAR NOT NULL,
    inter_corp_name VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- inter_corp_users
CREATE TABLE inter_corp_users (
    id SERIAL PRIMARY KEY,
    inter_corp_code TEXT NOT NULL,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    image TEXT
);

-- links
CREATE TABLE links (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL UNIQUE,
    scopus_url TEXT,
    webofscience_url TEXT,
    google_scholar_url TEXT,
    linkedin_url TEXT
);

-- cv
CREATE TABLE cv (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL UNIQUE,
    cv_path VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    CONSTRAINT uq_cv_fin_kod UNIQUE (fin_kod)
);

-- scientific_degrees
CREATE TABLE scientific_degrees (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL REFERENCES "user"(fin_kod),
    scientific_degree_code VARCHAR(10) NOT NULL,
    scientific_degree_name TEXT NOT NULL
);

-- user_translations
CREATE TABLE user_translations (
    id SERIAL PRIMARY KEY,
    fin_kod VARCHAR(7) NOT NULL,
    language_code VARCHAR(2) NOT NULL,
    scientific_degree_name VARCHAR NOT NULL,
    scientific_name VARCHAR NOT NULL,
    bio VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

