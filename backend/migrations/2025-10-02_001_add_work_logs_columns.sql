-- Migration: add_work_logs_columns
-- Date: 2025-10-02
-- Purpose: Fix Issue #23 - work_logsテーブルに欠落していたカラムを追加
-- Related Issue: #23

-- Issue #23で欠落していたカラムを追加（冪等）
ALTER TABLE work_logs ADD COLUMN IF NOT EXISTS start_time TIME;
ALTER TABLE work_logs ADD COLUMN IF NOT EXISTS end_time TIME;
ALTER TABLE work_logs ADD COLUMN IF NOT EXISTS work_content TEXT;
