-- Migration: add_management_no_to_projects
-- Date: 2025-10-02
-- Purpose: Add management_no column for project identification
-- Related Issue: #23

-- Add management_no column to projects table
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS management_no VARCHAR(50) UNIQUE;

-- Create index for management_no
CREATE INDEX IF NOT EXISTS idx_projects_management_no ON projects(management_no);
