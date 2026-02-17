-- 1. CLEANUP (Optional: Runs in order of dependency)
TRUNCATE pa.comments, pa.maintenance, pa.users CASCADE;

-- 2. FILL pa.users (Profiles)
INSERT INTO pa.users (username, first_name, last_name, email) VALUES
('pak_student', 'Ahmed', 'Khan', 'ahmed.k@nova.pt'), -- Based on your MSc student profile
('nature_fan', 'Maria', 'Silva', 'maria.s@example.pt'),
('city_worker', 'João', 'Santos', 'joao.s@lisboa.pt'),
('tree_checker', 'Sofia', 'Mendes', 'sofia.m@example.com');


-- 3. FILL pa.maintenance (Linking Trees to Operations)
INSERT INTO pa.maintenance (tree_id, op_code, observation, officer, maint_date) VALUES
(1, 4, 'Routine check, tree appears healthy.', 'Inspector John', '2026-01-10'), -- Tree 1: Visual Inspection
(1, 1, 'Crown thinning performed.', 'Arbor Team A', '2026-02-05'), -- Tree 1: Pruning
(1, 2, 'Applied eco-friendly pesticide.', 'Pest Control Div', '2026-01-20'), -- Tree 1: Pest Control
(1, 4, 'Post-treatment follow-up.', 'Inspector John', '2026-02-11'), -- Tree 1: Visual Inspection
(1, 6, 'Initial planting in urban zone.', 'Green Lisbon Team', '2024-11-15'), -- Tree 1: Planting
(1, 3, 'High-nitrogen fertilizer applied.', 'Maintenance Crew', '2026-02-12'), -- Tree 1: Fertilization
(2, 3, 'Winter fertilization cycle.', 'Maintenance Crew', '2025-12-01'), -- Tree 2: Fertilization
(3, 2, 'Aphid infestation treated.', 'Pest Control Div', '2026-01-20'), -- Tree 3: Pest Control
(5, 4, 'No issues found.', 'Inspector Mary', '2026-02-11'), -- Tree 5: Visual Inspection
(8, 6, 'Replacement tree planted.', 'Green Lisbon Team', '2024-11-15'), -- Tree 8: Planting
(10, 3, 'Soil nutrients replenished.', 'Maintenance Crew', '2026-02-12'); -- Tree 10: Fertilization

-- 4. FILL pa.comments (Linking Users to Trees)
INSERT INTO pa.comments (username, tree_id, comment, created_at) VALUES
('pak_student', 5, 'Checking the cork oak on campus today. Looks healthy.', '2026-02-13 09:00:00'),
('nature_fan', 1, 'The old olive tree is looking great after the pruning.', '2026-02-12 14:30:00'),
('tree_checker', 3, 'Found some issues with the bark, needs pest control.', '2026-01-18 10:15:00'),
('city_worker', 10, 'Young tree in Belém, watering completed.', '2026-02-12 17:00:00'),
('pak_student', 2, 'The Jacarandas in Av. Liberdade are iconic.', '2026-02-10 12:00:00'),
('nature_fan', 1, 'Sat under this tree today. The shade is perfect for a summer afternoon.', '2026-02-13 10:00:00'),
('city_worker', 1, 'Verified the species; it is indeed a very old Olea europaea.', '2026-02-13 11:30:00'),
('pak_student', 1, 'Noticed some new growth on the lower branches today. Looking healthy!', '2026-02-13 12:45:00'),
('tree_checker', 1, 'Great spot to study near NOVA IMS. Very peaceful atmosphere.', '2026-02-13 14:20:00'),
('city_worker', 1, 'I hope the city continues to protect these monumental olive trees.', '2026-02-13 15:10:00'),
('nature_fan', 1, 'This tree is my favorite landmark during my morning jogs through the park.', '2026-02-13 16:30:00'),
('nature_fan', 1, 'The lighting on the bark at sunset is absolutely stunning for macro shots.', '2026-02-13 17:15:00'),
('nature_fan', 5, 'I noticed the bark is being harvested. Very cool to see!', '2026-02-12 09:00:00'),
('tree_checker', 5, 'Structural integrity looks good after the high winds.', '2026-02-13 08:45:00');