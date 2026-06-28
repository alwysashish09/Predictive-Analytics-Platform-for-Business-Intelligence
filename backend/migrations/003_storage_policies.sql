-- ============================================================
-- Migration 003: Storage Bucket Policies
-- Predictive Analytics Platform for Business Intelligence
-- ============================================================

-- NOTE: Create these storage buckets manually in Supabase Dashboard:
--   1. "datasets"  — for uploaded CSV/Excel files
--   2. "models"    — for serialized .pkl model files
--   3. "reports"   — for generated PDF reports
--
-- Then run these policies in the SQL Editor.

-- ============================================================
-- Datasets bucket — users store files in {user_id}/ prefix
-- ============================================================
CREATE POLICY "Users can upload to datasets bucket"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'datasets'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can read own dataset files"
  ON storage.objects FOR SELECT
  USING (
    bucket_id = 'datasets'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can delete own dataset files"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'datasets'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- ============================================================
-- Models bucket
-- ============================================================
CREATE POLICY "Users can upload to models bucket"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'models'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can read own model files"
  ON storage.objects FOR SELECT
  USING (
    bucket_id = 'models'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can delete own model files"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'models'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- ============================================================
-- Reports bucket
-- ============================================================
CREATE POLICY "Users can upload to reports bucket"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'reports'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can read own report files"
  ON storage.objects FOR SELECT
  USING (
    bucket_id = 'reports'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

CREATE POLICY "Users can delete own report files"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'reports'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );
