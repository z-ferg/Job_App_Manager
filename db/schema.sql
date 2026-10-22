-- COMPANY
CREATE TABLE company (
    company_id    SERIAL PRIMARY KEY,
    company_name  VARCHAR(255) NOT NULL UNIQUE,
    industry      VARCHAR(100) NULL,
    website       VARCHAR(255) NULL
);

-- STUDENT
CREATE TABLE student (
    student_id  SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    university  VARCHAR(255) NOT NULL,
    major       VARCHAR(255) NOT NULL,
    grad_year   INT NOT NULL,
    CONSTRAINT chk_student_grad_year CHECK (grad_year BETWEEN 2000 AND 2100)
);

-- CAREER_FAIR_EVENT
CREATE TABLE career_fair_event (
    event_id     SERIAL PRIMARY KEY,
    event_name   VARCHAR(255) NOT NULL,
    event_date   TIMESTAMP NULL,
    location     VARCHAR(255) NULL,
    description  TEXT NULL
);

-- RECRUITER
CREATE TABLE recruiter (
    recruiter_id  SERIAL PRIMARY KEY,
    company_id    INT NOT NULL,
    name          VARCHAR(255) NOT NULL,
    email         VARCHAR(255) NULL,
    CONSTRAINT fk_recruiter_company
        FOREIGN KEY (company_id) REFERENCES company (company_id)
);

-- JOB_LISTING
CREATE TABLE job_listing (
    listing_id    SERIAL PRIMARY KEY,
    recruiter_id  INT NULL,
    company_id    INT NOT NULL,
    title         VARCHAR(255) NOT NULL,
    description   TEXT NOT NULL,
    requirements  TEXT NOT NULL,
    posted_date   DATE NOT NULL,
    deadline      DATE NULL,
    CONSTRAINT fk_listing_recruiter
        FOREIGN KEY (recruiter_id) REFERENCES recruiter (recruiter_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_listing_company
        FOREIGN KEY (company_id) REFERENCES company (company_id)
);

-- EVENT_RECRUITERS (junction)
CREATE TABLE event_recruiters (
    recruiter_id  INT NOT NULL,
    event_id      INT NOT NULL,
    PRIMARY KEY (recruiter_id, event_id),
    CONSTRAINT fk_evrec_recruiter
        FOREIGN KEY (recruiter_id) REFERENCES recruiter (recruiter_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_evrec_event
        FOREIGN KEY (event_id) REFERENCES career_fair_event (event_id)
        ON DELETE CASCADE
);

-- ENUM TYPES
CREATE TYPE application_status AS ENUM (
    'Not Applied','Applied','Interviewing','Offer',
    'Accepted','Declined','Rejected','Withdrawn'
);
CREATE TYPE interview_modality_t AS ENUM ('Phone','Video','In Person');
CREATE TYPE interview_type_t AS ENUM ('Behavioral','Technical','Screening');
CREATE TYPE reminder_type_t AS ENUM ('Follow-up','Interview Prep','Deadline','Event Application');

-- APPLICATION
CREATE TABLE application (
    application_id      SERIAL PRIMARY KEY,
    student_id          INT NOT NULL,
    listing_id          INT NULL,
    company_id          INT NULL,
    company_name        VARCHAR(255) NOT NULL,
    role_title          VARCHAR(255) NOT NULL,
    status              application_status NOT NULL,
    date_applied        DATE NULL,
    recruiter_email     VARCHAR(255) NULL,
    notes               TEXT NULL,
    last_followup_date  DATE NULL,
    CONSTRAINT uq_application_student_listing UNIQUE (student_id, listing_id),
    CONSTRAINT chk_application_date_applied
        CHECK (status = 'Not Applied' OR date_applied IS NOT NULL),
    CONSTRAINT fk_application_student
        FOREIGN KEY (student_id) REFERENCES student (student_id),
    CONSTRAINT fk_application_listing
        FOREIGN KEY (listing_id) REFERENCES job_listing (listing_id),
    CONSTRAINT fk_application_company
        FOREIGN KEY (company_id) REFERENCES company (company_id)
);

-- EVENT_REGISTRATION
CREATE TABLE event_registration (
    registration_id    SERIAL PRIMARY KEY,
    student_id         INT NOT NULL,
    event_id           INT NOT NULL,
    registration_date  DATE NOT NULL,
    match_score        REAL NULL,
    CONSTRAINT uq_registration_student_event UNIQUE (student_id, event_id),
    CONSTRAINT fk_registration_student
        FOREIGN KEY (student_id) REFERENCES student (student_id),
    CONSTRAINT fk_registration_event
        FOREIGN KEY (event_id) REFERENCES career_fair_event (event_id),
    CONSTRAINT chk_match_score CHECK (match_score BETWEEN 0 AND 100)
);

-- INTERVIEW
CREATE TABLE interview (
    interview_id        SERIAL PRIMARY KEY,
    application_id      INT NOT NULL,
    recruiter_id        INT NULL,
    round_num           INT NOT NULL,
    interview_modality  interview_modality_t NOT NULL,
    interview_type      interview_type_t NOT NULL,
    interview_date      TIMESTAMP NULL,
    notes               TEXT NULL,
    CONSTRAINT chk_interview_round CHECK (round_num >= 1),
    CONSTRAINT fk_interview_application
        FOREIGN KEY (application_id) REFERENCES application (application_id),
    CONSTRAINT fk_interview_recruiter
        FOREIGN KEY (recruiter_id) REFERENCES recruiter (recruiter_id)
        ON DELETE SET NULL
);

-- REMINDER
CREATE TABLE reminder (
    reminder_id      SERIAL PRIMARY KEY,
    application_id   INT NULL,
    interview_id     INT NULL,
    registration_id  INT NULL,
    reminder_date    TIMESTAMP NOT NULL,
    reminder_type    reminder_type_t NOT NULL,
    completed        BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT chk_reminder_exactly_one_target CHECK (
        num_nonnulls(application_id, interview_id, registration_id) = 1
    ),
    CONSTRAINT fk_reminder_application
        FOREIGN KEY (application_id) REFERENCES application (application_id),
    CONSTRAINT fk_reminder_interview
        FOREIGN KEY (interview_id) REFERENCES interview (interview_id),
    CONSTRAINT fk_reminder_registration
        FOREIGN KEY (registration_id) REFERENCES event_registration (registration_id)
);
