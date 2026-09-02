CREATE TABLE clients
(
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  middle_name VARCHAR(100),
  birth_date DATE,
  phone_number VARCHAR(30) UNIQUE NOT NULL,
  metro_station VARCHAR(50),
  notes TEXT,
  gender VARCHAR(10) CHECK (gender IN ('мужской', 'женский')),
  status VARCHAR(20) CHECK (status IN ('новый', 'активный', 'архив')),
  CHECK ((phone_number !='') AND (first_name !='') AND (last_name !=''))
);

CREATE TABLE patients_children
(
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  middle_name VARCHAR(100),
  birth_date DATE,
  first_visit DATE NOT NULL,
  last_visit DATE,
  status VARCHAR(20) CHECK (status IN ('новый', 'активный', 'архив'))
);

CREATE TABLE clients_children
(
  children_id INTEGER NOT NULL REFERENCES patients_children (id),
  client_id INTEGER NOT NULL REFERENCES clients (id),
  relationship VARCHAR(30),
  PRIMARY KEY (children_id, client_id)
);

CREATE TABLE medical_card
(
  id SERIAL PRIMARY KEY,
  patient_id INTEGER NOT NULL UNIQUE REFERENCES patients_children (id) ON DELETE CASCADE,
  anamnesis TEXT
);

CREATE TABLE diagnosis 
(
  id SERIAL PRIMARY KEY,
  patient_id INTEGER NOT NULL REFERENCES patients_children (id),
  diagnosis VARCHAR(100) NOT NULL
);

CREATE TABLE lessons
(
  id SERIAL PRIMARY KEY,
  patient_id INTEGER NOT NULL REFERENCES patients_children (id),
  status VARCHAR (20) CHECK  (status IN ('назначено', 'завершилось', 'пропущено')) NOT NULL,
  date_lesson DATE NOT NULL
);

CREATE TABLE plan_lesson
(
  id SERIAL PRIMARY KEY,
  lesson_id INTEGER NOT NULL UNIQUE REFERENCES lessons (id),
  description TEXT,
  result TEXT,
  rating SMALLINT CHECK (rating BETWEEN 0 AND 5)
);

CREATE TABLE schedule 
(
  id SERIAL PRIMARY KEY,
  lesson_id INTEGER UNIQUE REFERENCES lessons (id),
  date_slot DATE NOT NULL,
  time_slot TIME NOT NULL,
  is_free BOOLEAN NOT NULL
);

CREATE TABLE payments 
(
  id SERIAL PRIMARY KEY,
  client_id INTEGER NOT NULL REFERENCES clients (id),
  lesson_id INTEGER NOT NULL REFERENCES lessons (id),
  total NUMERIC(10, 2) NOT NULL,
  payment_date DATE NOT NULL,
  payment_status VARCHAR(30) NOT NULL CHECK (status IN ('оплачен', 'не оплачен', 'просрочен'))
);

CREATE TABLE potential_clients
(
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  child_name VARCHAR(100),
  phone_number VARCHAR(30) NOT NULL,
  diagnosis TEXT,
  desired_time TEXT,
  request_date DATE NOT NULL DEFAULT CURRENT_DATE,
  notes TEXT
);

