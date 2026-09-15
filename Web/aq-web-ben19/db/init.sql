CREATE TABLE users (
  id serial primary key,
  username text unique not null,
  password_hash text not null,
  email text not null
);

CREATE TABLE emails (
  id serial primary key,
  user_id int references users(id),
  from_addr text,
  to_addr text,
  subject text,
  body text,
  created_at timestamp default now()
);

CREATE TABLE attachments (
  id serial primary key,
  email_id int references emails(id),
  filename text,
  object_url text,
  object_key text
);

-- create an admin user 
INSERT INTO users (id, username, password_hash, email)
VALUES (999, 'admin', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', 'admin@asismail.local');
