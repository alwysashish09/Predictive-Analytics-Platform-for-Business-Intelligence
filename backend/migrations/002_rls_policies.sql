-- ============================================================
-- Migration 002: Row Level Security Policies
-- Predictive Analytics Platform for Business Intelligence
-- ============================================================

-- ============================================================
-- Enable RLS on all tables
-- ============================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transformation_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- Profiles
-- ============================================================
CREATE POLICY "Users can view own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- Allow insert for the trigger function (SECURITY DEFINER handles this)
CREATE POLICY "Service role can insert profiles"
  ON public.profiles FOR INSERT
  WITH CHECK (true);

-- ============================================================
-- Datasets
-- ============================================================
CREATE POLICY "Users can view own datasets"
  ON public.datasets FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own datasets"
  ON public.datasets FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own datasets"
  ON public.datasets FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own datasets"
  ON public.datasets FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================
-- Model Runs
-- ============================================================
CREATE POLICY "Users can view own model runs"
  ON public.model_runs FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own model runs"
  ON public.model_runs FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own model runs"
  ON public.model_runs FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own model runs"
  ON public.model_runs FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================
-- Predictions
-- ============================================================
CREATE POLICY "Users can view own predictions"
  ON public.predictions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own predictions"
  ON public.predictions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own predictions"
  ON public.predictions FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================
-- AI Reports
-- ============================================================
CREATE POLICY "Users can view own reports"
  ON public.ai_reports FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own reports"
  ON public.ai_reports FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own reports"
  ON public.ai_reports FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================
-- Transformation Logs (access via dataset ownership)
-- ============================================================
CREATE POLICY "Users can view own transformation logs"
  ON public.transformation_logs FOR SELECT
  USING (
    dataset_id IN (
      SELECT id FROM public.datasets WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert transformation logs for own datasets"
  ON public.transformation_logs FOR INSERT
  WITH CHECK (
    dataset_id IN (
      SELECT id FROM public.datasets WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update transformation logs for own datasets"
  ON public.transformation_logs FOR UPDATE
  USING (
    dataset_id IN (
      SELECT id FROM public.datasets WHERE user_id = auth.uid()
    )
  );
