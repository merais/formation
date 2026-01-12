-- Script d'initialisation de la base de données MySQL
-- Création de la base de données et des tables pour le système de gestion de tickets

-- Création de la base de données
CREATE DATABASE IF NOT EXISTS ticket_system;
USE ticket_system;

-- ========================================
-- Table des tickets enrichis
-- ========================================
CREATE TABLE IF NOT EXISTS tickets_enrichis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ticket_id VARCHAR(255) NOT NULL UNIQUE,
    client_id VARCHAR(50) NOT NULL,
    date_creation DATETIME NOT NULL,
    demande TEXT NOT NULL,
    type_demande VARCHAR(50) NOT NULL,
    priorite VARCHAR(20) NOT NULL,
    equipe_assignee VARCHAR(100) NOT NULL,
    timestamp_traitement DATETIME NOT NULL,
    INDEX idx_client (client_id),
    INDEX idx_type (type_demande),
    INDEX idx_priorite (priorite),
    INDEX idx_equipe (equipe_assignee),
    INDEX idx_date_creation (date_creation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Table des statistiques par type de demande
-- ========================================
CREATE TABLE IF NOT EXISTS stats_par_type (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    type_demande VARCHAR(50) NOT NULL,
    equipe_assignee VARCHAR(100) NOT NULL,
    nombre_tickets BIGINT NOT NULL,
    timestamp_calcul DATETIME NOT NULL,
    INDEX idx_type (type_demande),
    INDEX idx_timestamp (timestamp_calcul)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Table des statistiques par priorité
-- ========================================
CREATE TABLE IF NOT EXISTS stats_par_priorite (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    priorite VARCHAR(20) NOT NULL,
    nombre_tickets BIGINT NOT NULL,
    timestamp_calcul DATETIME NOT NULL,
    INDEX idx_priorite (priorite),
    INDEX idx_timestamp (timestamp_calcul)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Table des statistiques par équipe
-- ========================================
CREATE TABLE IF NOT EXISTS stats_par_equipe (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    equipe_assignee VARCHAR(100) NOT NULL,
    total_tickets BIGINT NOT NULL,
    tickets_critiques BIGINT NOT NULL,
    tickets_haute_priorite BIGINT NOT NULL,
    timestamp_calcul DATETIME NOT NULL,
    INDEX idx_equipe (equipe_assignee),
    INDEX idx_timestamp (timestamp_calcul)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Vue pour analyse temps réel
-- ========================================
CREATE OR REPLACE VIEW v_tickets_recents AS
SELECT 
    ticket_id,
    client_id,
    date_creation,
    demande,
    type_demande,
    priorite,
    equipe_assignee,
    timestamp_traitement,
    TIMESTAMPDIFF(MINUTE, date_creation, timestamp_traitement) AS delai_traitement_minutes
FROM tickets_enrichis
WHERE date_creation >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY date_creation DESC;

-- ========================================
-- Vue pour le dashboard de charge par équipe
-- ========================================
CREATE OR REPLACE VIEW v_charge_equipes AS
SELECT 
    equipe_assignee,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN priorite = 'Critique' THEN 1 ELSE 0 END) AS tickets_critiques,
    SUM(CASE WHEN priorite = 'Haute' THEN 1 ELSE 0 END) AS tickets_haute,
    SUM(CASE WHEN priorite = 'Moyenne' THEN 1 ELSE 0 END) AS tickets_moyenne,
    SUM(CASE WHEN priorite = 'Basse' THEN 1 ELSE 0 END) AS tickets_basse,
    AVG(TIMESTAMPDIFF(MINUTE, date_creation, timestamp_traitement)) AS delai_moyen_minutes
FROM tickets_enrichis
GROUP BY equipe_assignee
ORDER BY total_tickets DESC;

-- ========================================
-- Vue pour analyse par type et priorité
-- ========================================
CREATE OR REPLACE VIEW v_analyse_type_priorite AS
SELECT 
    type_demande,
    priorite,
    COUNT(*) AS nombre_tickets,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY type_demande), 2) AS pourcentage_par_type
FROM tickets_enrichis
GROUP BY type_demande, priorite
ORDER BY type_demande, nombre_tickets DESC;

-- Message de confirmation
SELECT 'Base de données initialisée avec succès!' AS status;
