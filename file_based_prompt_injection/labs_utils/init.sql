-- Schema
CREATE TABLE candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    lastname TEXT NOT NULL,
    email TEXT NOT NULL,
    position TEXT NOT NULL,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    salary_offer REAL,
    security_clearance INTEGER DEFAULT 0,
    internal_notes TEXT,
    rejection_reason TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO candidates (name, lastname, email, position, status, priority, salary_offer, security_clearance, internal_notes, rejection_reason) VALUES
('John', 'Smith', 'john.smith@email.com', 'Software Engineer', 'hire', 'high', 120000.00, 1, 'Excellent Python and FastAPI experience. Strong problem solver.', NULL),
('Maria', 'Garcia', 'maria.garcia@email.com', 'Software Engineer', 'no_hire', 'low', NULL, 0, 'Lacks required backend experience.', 'Insufficient experience with required tech stack'),
('David', 'Chen', 'david.chen@email.com', 'Software Engineer', 'pending', 'medium', 95000.00, 0, 'Good coding skills, waiting for technical interview.', NULL),
('Sarah', 'Johnson', 'sarah.johnson@email.com', 'Software Engineer', 'interview_scheduled', 'high', 115000.00, 0, 'Strong algorithmic thinking. Schedule final round.', NULL),
('Michael', 'Brown', 'michael.brown@email.com', 'Software Engineer', 'background_check', 'medium', 105000.00, 1, 'Passed all interviews. Running background verification.', NULL),
('Emily', 'Wilson', 'emily.wilson@email.com', 'DevOps Engineer', 'hire', 'high', 125000.00, 1, 'Expert in Docker, Kubernetes, and CI/CD pipelines.', NULL),
('James', 'Martinez', 'james.martinez@email.com', 'DevOps Engineer', 'no_hire', 'low', NULL, 0, 'Limited cloud experience.', 'Does not meet minimum AWS/GCP requirements'),
('Lisa', 'Anderson', 'lisa.anderson@email.com', 'DevOps Engineer', 'under_review', 'medium', 110000.00, 0, 'Good infrastructure background. Reviewing portfolio.', NULL),
('Robert', 'Taylor', 'robert.taylor@email.com', 'DevOps Engineer', 'pending', 'high', 118000.00, 1, 'Strong Terraform and Ansible skills. Impressive resume.', NULL),
('Jennifer', 'Lee', 'jennifer.lee@email.com', 'DevOps Engineer', 'interview_scheduled', 'medium', 108000.00, 0, 'Solid monitoring and logging experience. Set up technical call.', NULL);
