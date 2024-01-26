DROP SEQUENCE IF EXISTS urls_id_seq CASCADE;
DROP TABLE IF EXISTS urls CASCADE;
DROP TABLE IF EXISTS url_checks;

CREATE TABLE urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) UNIQUE,
    created_at date
);

CREATE TABLE url_checks (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id bigint REFERENCES urls (id),
    status_code integer,
    h1 varchar(255),
    title varchar(255),
    description text,
    created_at date
    );


CREATE SEQUENCE urls_id_seq START 1;
