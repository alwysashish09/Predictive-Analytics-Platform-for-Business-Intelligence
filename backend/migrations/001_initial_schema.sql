-- ============================================================
-- Migration 001: Initial Schema
-- Predictive Analytics Platform for Business Intelligence
-- ============================================================

-- 1. User profiles (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Datasets
CREATE TABLE IF NOT EXISTS public.datasets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  file_name TEXT NOT NULL,
  file_url TEXT,
  file_size_bytes BIGINT,
  row_count INTEGER,
  column_count INTEGER,
  column_metadata JSONB DEFAULT '{}',
  status TEXT DEFAULT 'uploaded'
    CHECK (status IN ('uploaded', 'cleaning', 'ready', 'error')),
  problem_type TEXT
    CHECK (problem_type IS NULL OR problem_type IN ('classification', 'regression')),
  target_column TEXT,
  cleaning_log JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Model Runs
CREATE TABLE IF NOT EXISTS public.model_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  dataset_id UUID NOT NULL REFERENCES public.datasets(id) ON DELETE CASCADE,
  model_type TEXT NOT NULL
    CHECK (model_type IN ('random_forest', 'xgboost', 'ensemble')),
  hyperparameters JSONB DEFAULT '{}',
  metrics JSONB DEFAULT '{}',
  feature_importance JSONB DEFAULT '[]',
  model_file_path TEXT,
  status TEXT DEFAULT 'training'
    CHECK (status IN ('training', 'completed', 'failed')),
  training_duration_sec FLOAT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Predictions
CREATE TABLE IF NOT EXISTS public.predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  model_run_id UUID NOT NULL REFERENCES public.model_runs(id) ON DELETE CASCADE,
  input_data JSONB,
  predictions JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. AI Reports
CREATE TABLE IF NOT EXISTS public.ai_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  model_run_id UUID REFERENCES public.model_runs(id),
  dataset_id UUID REFERENCES public.datasets(id),
  report_type TEXT NOT NULL
    CHECK (report_type IN ('insight', 'chat', 'executive_pdf', 'data_summary')),
  content TEXT,
  pdf_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Transformation Logs
CREATE TABLE IF NOT EXISTS public.transformation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_id UUID NOT NULL REFERENCES public.datasets(id) ON DELETE CASCADE,
  step_order INTEGER NOT NULL,
  step_name TEXT NOT NULL,
  description TEXT,
  rows_affected INTEGER,
  status TEXT DEFAULT 'pending'
    CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  details JSONB,
  duration_ms FLOAT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_datasets_user ON public.datasets(user_id);
CREATE INDEX IF NOT EXISTS idx_datasets_status ON public.datasets(status);
CREATE INDEX IF NOT EXISTS idx_model_runs_dataset ON public.model_runs(dataset_id);
CREATE INDEX IF NOT EXISTS idx_model_runs_user ON public.model_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_model ON public.predictions(model_run_id);
CREATE INDEX IF NOT EXISTS idx_predictions_user ON public.predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_transform_logs_dataset ON public.transformation_logs(dataset_id);
CREATE INDEX IF NOT EXISTS idx_ai_reports_user ON public.ai_reports(user_id);

-- ============================================================
-- Updated_at trigger function
-- ============================================================
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER set_datasets_updated_at
  BEFORE UPDATE ON public.datasets
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- ============================================================
-- Auto-create profile on signup
-- ============================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop trigger if exists to allow re-running
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
