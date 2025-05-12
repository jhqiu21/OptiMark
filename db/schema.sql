-- students: stores student accounts, email optional but unique when present
CREATE TABLE IF NOT EXISTS students (
  id CHAR(8) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NULL,
  password VARCHAR(255) NOT NULL,
  enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY ux_students_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- staff: stores instructor/staff accounts, email optional but unique when present
CREATE TABLE IF NOT EXISTS staff (
  id CHAR(8) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NULL,
  password VARCHAR(255) NOT NULL,
  enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY ux_staff_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- semesters
CREATE TABLE IF NOT EXISTS semesters (
  id CHAR(6) PRIMARY KEY,    -- format: YYYYS#, e.g. 2425S1
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- courses: catalog of course subjects
CREATE TABLE IF NOT EXISTS courses (
  code CHAR(12) PRIMARY KEY,    -- format: DEPT1234-X, e.g. CS1010-A
  name VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- offers: course offerings in specific semesters (composite PK)
CREATE TABLE IF NOT EXISTS offers (
  course_code CHAR(12) NOT NULL,
  semester_id CHAR(6) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (course_code, semester_id),
  FOREIGN KEY (course_code) REFERENCES courses(code) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- offering_instructor: which staff teach each offering
CREATE TABLE IF NOT EXISTS offering_instructor (
  course_code CHAR(12) NOT NULL,
  semester_id CHAR(6) NOT NULL,
  instructor_id CHAR(8) NOT NULL,
  PRIMARY KEY (course_code, semester_id, instructor_id),
  FOREIGN KEY (course_code, semester_id)
    REFERENCES offers(course_code, semester_id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (instructor_id)
    REFERENCES staff(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- offering_students: which students are enrolled in each offering
CREATE TABLE IF NOT EXISTS offering_students (
  course_code CHAR(12) NOT NULL,
  semester_id CHAR(6) NOT NULL,
  student_id CHAR(8) NOT NULL,
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (course_code, semester_id, student_id),
  FOREIGN KEY (course_code, semester_id)
    REFERENCES offers(course_code, semester_id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (student_id)
    REFERENCES students(id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- exams: instances of assessments for a given offering
CREATE TABLE IF NOT EXISTS exams (
  id CHAR(8) PRIMARY KEY,
  course_code CHAR(12) NOT NULL,
  semester_id CHAR(6) NOT NULL,
  name VARCHAR(100) NOT NULL,
  start_time DATETIME,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (course_code, semester_id)
    REFERENCES offers(course_code, semester_id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- upload_batches: batch uploads of answer sheets for an exam
CREATE TABLE IF NOT EXISTS upload_batches (
  id CHAR(8) PRIMARY KEY,
  exam_id CHAR(8) NOT NULL,
  name VARCHAR(255) NOT NULL, 
  uploaded_by CHAR(8) NOT NULL,
  status ENUM('pending','processing','done','failed') NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (exam_id)
    REFERENCES exams(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (uploaded_by)
    REFERENCES staff(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- answer_tasks: individual answer sheet processing records
CREATE TABLE IF NOT EXISTS answer_tasks (
  id CHAR(8) PRIMARY KEY,
  batch_id CHAR(8) NOT NULL,
  student_id CHAR(8) NOT NULL,
  task_name VARCHAR(255) NOT NULL,
  status ENUM('pending','processing','done','failed') NOT NULL DEFAULT 'pending',
  score INT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (batch_id) REFERENCES upload_batches(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (student_id) REFERENCES students(id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- exam_files: files related to exams (no further categorization)
CREATE TABLE IF NOT EXISTS exam_files (
  id CHAR(8) PRIMARY KEY,
  exam_id CHAR(8) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  is_public BOOLEAN NOT NULL DEFAULT FALSE,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  published_at TIMESTAMP NULL,
  FOREIGN KEY (exam_id) REFERENCES exams(id)
      ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
