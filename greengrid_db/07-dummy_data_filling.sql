-- 1. CLEANUP (Optional: Runs in order of dependency)
TRUNCATE pa.comments, pa.maintenance, pa.trees, pa.users, pa.parish, pa.operations CASCADE;

-- 2. FILL pa.operations (The "Lookup" table for maintenance types)
INSERT INTO pa.operations (op_code, op_description) VALUES
(1, 'Pruning (Poda)'),
(2, 'Pest Control (Controle de Pragas)'),
(3, 'Fertilization (Adubação)'),
(4, 'Visual Inspection (Inspeção Visual)'),
(5, 'Removal (Remoção)'),
(6, 'Planting (Plantação)');

-- 3. FILL pa.users (Profiles)
INSERT INTO pa.users (username, first_name, last_name, email) VALUES
('pak_student', 'Ahmed', 'Khan', 'ahmed.k@nova.pt'), -- Based on your MSc student profile
('nature_fan', 'Maria', 'Silva', 'maria.s@example.pt'),
('city_worker', 'João', 'Santos', 'joao.s@lisboa.pt'),
('tree_checker', 'Sofia', 'Mendes', 'sofia.m@example.com');

-- 4. FILL pa.parish (Using the parish shapefile)
INSERT INTO pa.parish (id, freguesia, geometry)
SELECT  id,  freguesia, ST_Multi(geom)
FROM public.lisbon_parishes;

-- 5. FILL pa.trees (The core inventory)
INSERT INTO pa.trees (tree_id, nome_vulga, especie, tipologia, pap, manutencao, ocupacao, local, morada, freguesia, geometry) VALUES
(1, 'Oliveira', 'Olea europaea', 'Tree', 45.0, 'Regular', 'Public', 'Jardim da Estrela', 'Praça da Estrela', 'Estrela', ST_SetSRID(ST_MakePoint(-9.1594, 38.7137), 4326)),
(2, 'Jacarandá', 'Jacaranda mimosifolia', 'Tree', 30.0, 'Regular', 'Public', 'Av. Liberdade', 'Avenida da Liberdade', 'Santo António', ST_SetSRID(ST_MakePoint(-9.1462, 38.7215), 4326)),
(3, 'Pinheiro Manso', 'Pinus pinea', 'Conifer', 60.5, 'Intensive', 'Public', 'Monsanto', 'Estrada de Monsanto', 'Benfica', ST_SetSRID(ST_MakePoint(-9.1850, 38.7400), 4326)),
(4, 'Plátano', 'Platanus x acerifolia', 'Tree', 85.0, 'Regular', 'Public', 'Parque Eduardo VII', 'Alameda Cardeal Cerejeira', 'Avenidas Novas', ST_SetSRID(ST_MakePoint(-9.1510, 38.7280), 4326)),
(5, 'Sobreiro', 'Quercus suber', 'Tree', 40.0, 'Special', 'Private', 'NOVA IMS Campus', 'Campolide', 'Campolide', ST_SetSRID(ST_MakePoint(-9.1550, 38.7320), 4326)),
(6, 'Magnólia', 'Magnolia grandiflora', 'Small Tree', 25.0, 'Regular', 'Public', 'Príncipe Real', 'Praça do Príncipe Real', 'Misericórdia', ST_SetSRID(ST_MakePoint(-9.1480, 38.7160), 4326)),
(7, 'Tília', 'Tilia tomentosa', 'Tree', 50.0, 'Regular', 'Public', 'Campo de Ourique', 'Rua Ferreira Borges', 'Campo de Ourique', ST_SetSRID(ST_MakePoint(-9.1650, 38.7150), 4326)),
(8, 'Cedro', 'Cupressus lusitanica', 'Conifer', 70.0, 'Regular', 'Public', 'Tapada da Ajuda', 'Calçada da Ajuda', 'Ajuda', ST_SetSRID(ST_MakePoint(-9.1850, 38.7080), 4326)),
(9, 'Aroeira', 'Schinus molle', 'Tree', 35.5, 'Regular', 'Public', 'Cais do Sodré', 'Praça do Duque', 'Misericórdia', ST_SetSRID(ST_MakePoint(-9.1440, 38.7060), 4326)),
(10, 'Sobreiro Jovem', 'Quercus suber', 'Sapling', 15.0, 'Frequent', 'Public', 'Belém Riverside', 'Av. Brasília', 'Belém', ST_SetSRID(ST_MakePoint(-9.2000, 38.6960), 4326));

-- 6. FILL pa.maintenance (Linking Trees to Operations)
INSERT INTO pa.maintenance (tree_id, op_code, observation, officer, maint_date) VALUES
(1, 4, 'Routine check, tree appears healthy.', 'Inspector John', '2026-01-10'), -- Tree 1: Visual Inspection
(1, 1, 'Crown thinning performed.', 'Arbor Team A', '2026-02-05'), -- Tree 1: Pruning
(1, 2, 'Applied eco-friendly pesticide.', 'Pest Control Div', '2026-01-20'), -- Tree 1: Pest Control
(1, 4, 'Post-treatment follow-up.', 'Inspector John', '2026-02-11'), -- Tree 1: Visual Inspection
(1, 6, 'Initial planting in urban zone.', 'Green Lisbon Team', '2024-11-15'), -- Tree 1: Planting
(1, 3, 'High-nitrogen fertilizer applied.', 'Maintenance Crew', '2026-02-12'); -- Tree 1: Fertilization
(2, 3, 'Winter fertilization cycle.', 'Maintenance Crew', '2025-12-01'), -- Tree 2: Fertilization
(3, 2, 'Aphid infestation treated.', 'Pest Control Div', '2026-01-20'), -- Tree 3: Pest Control
(5, 4, 'No issues found.', 'Inspector Mary', '2026-02-11'), -- Tree 5: Visual Inspection
(8, 6, 'Replacement tree planted.', 'Green Lisbon Team', '2024-11-15'), -- Tree 8: Planting
(10, 3, 'Soil nutrients replenished.', 'Maintenance Crew', '2026-02-12'); -- Tree 10: Fertilization

-- 7. FILL pa.comments (Linking Users to Trees)
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