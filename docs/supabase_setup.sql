-- ============================================================================
-- MIGRAÇÃO OFICIAL APLICADA NO SUPABASE — QUIZ COMPETITIVO RUA DA CIÊNCIA
-- Projeto: PPGDTSAProject (saelflamvwfrlhfccfdh) • PPGDTSA • DCSA • UFPel
-- Otimizado para mínimo consumo de banco, Index-Only Scan, zero TOAST bloat e anti-spam
-- ============================================================================

-- 1. Tabela enxuta e fortemente validada do Ranking Competitivo
CREATE TABLE IF NOT EXISTS public.quiz_ranking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_name TEXT NOT NULL CHECK (char_length(btrim(player_name)) BETWEEN 2 AND 40),
  player_age SMALLINT NOT NULL CHECK (player_age BETWEEN 5 AND 110),
  age_group TEXT NOT NULL CHECK (
    age_group IN ('jovem', 'adulto')
    AND ((player_age <= 16 AND age_group = 'jovem') OR (player_age >= 17 AND age_group = 'adulto'))
  ),
  correct_count SMALLINT NOT NULL CHECK (correct_count BETWEEN 0 AND 66),
  questions_answered SMALLINT NOT NULL CHECK (
    questions_answered BETWEEN 1 AND 66
    AND correct_count <= questions_answered
  ),
  reached_challenger BOOLEAN NOT NULL DEFAULT false CHECK (reached_challenger = (correct_count >= 7)),
  total_time_ms INTEGER NOT NULL CHECK (
    total_time_ms >= (questions_answered * 120)
    AND total_time_ms <= 7200000
  ),
  selfie_url TEXT NOT NULL CHECK (
    char_length(selfie_url) BETWEEN 10 AND 512
    AND selfie_url NOT LIKE 'data:%'
    AND (
      selfie_url LIKE 'https://%/storage/v1/object/public/quiz-selfies/selfies/selfie_%'
      OR selfie_url IN (
        './src/assets/vitrine/logos/ppgdtsa_tree.png',
        './src/assets/produtora_busto_hud.jpg'
      )
    )
  ),
  accepted_terms BOOLEAN NOT NULL DEFAULT true CHECK (accepted_terms = true),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Índices cirúrgicos (Covering Index para Index-Only Scan no Top Ranking + Anti-Spam)
CREATE INDEX IF NOT EXISTS idx_quiz_ranking_leaderboard
  ON public.quiz_ranking (correct_count DESC, total_time_ms ASC, created_at ASC)
  INCLUDE (id, player_name, player_age, age_group, questions_answered, reached_challenger, selfie_url);

CREATE INDEX IF NOT EXISTS idx_quiz_ranking_created_at
  ON public.quiz_ranking (created_at DESC);

-- 3. Trigger leve (SECURITY INVOKER) para higienização e bloqueio de requisições repetitivas/spam
CREATE OR REPLACE FUNCTION public.guard_quiz_ranking_insert()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public, pg_temp
AS $$
BEGIN
  NEW.player_name := regexp_replace(btrim(NEW.player_name), '\s+', ' ', 'g');
  NEW.age_group := CASE WHEN NEW.player_age <= 16 THEN 'jovem' ELSE 'adulto' END;
  NEW.reached_challenger := (NEW.correct_count >= 7);

  -- Evita submissões duplicadas/repetitivas seguidas para o mesmo jogador em janela de 10s
  IF EXISTS (
    SELECT 1
    FROM public.quiz_ranking r
    WHERE r.created_at > (now() - interval '10 seconds')
      AND lower(r.player_name) = lower(NEW.player_name)
  ) THEN
    RAISE SQLSTATE 'PGRST' USING
      MESSAGE = '{"code":"QUIZ_DUPLICATE_SUBMIT","message":"Pontuação já enviada recentemente. Aguarde alguns segundos."}',
      DETAIL = '{"status":429,"headers":{"Retry-After":"10"},"status_text":"Too Many Requests"}';
  END IF;

  -- Proteção contra rajadas anômalas (bots/scripts) acima de 35 inserções em 10s
  IF (
    SELECT count(*)
    FROM public.quiz_ranking r
    WHERE r.created_at > (now() - interval '10 seconds')
  ) >= 35 THEN
    RAISE SQLSTATE 'PGRST' USING
      MESSAGE = '{"code":"QUIZ_RATE_LIMIT","message":"Muitas requisições simultâneas. Tente novamente em instantes."}',
      DETAIL = '{"status":429,"headers":{"Retry-After":"10"},"status_text":"Too Many Requests"}';
  END IF;

  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_guard_quiz_ranking_insert ON public.quiz_ranking;
CREATE TRIGGER trg_guard_quiz_ranking_insert
  BEFORE INSERT ON public.quiz_ranking
  FOR EACH ROW
  EXECUTE FUNCTION public.guard_quiz_ranking_insert();

-- 4. Privilégios explícitos na Data API (sem UPDATE e sem DELETE)
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT SELECT, INSERT ON TABLE public.quiz_ranking TO anon, authenticated;
GRANT ALL ON TABLE public.quiz_ranking TO service_role;

-- 5. Row Level Security (RLS)
ALTER TABLE public.quiz_ranking ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "quiz_ranking_public_select" ON public.quiz_ranking;
CREATE POLICY "quiz_ranking_public_select"
  ON public.quiz_ranking
  FOR SELECT
  TO anon, authenticated
  USING (true);

DROP POLICY IF EXISTS "quiz_ranking_public_insert" ON public.quiz_ranking;
CREATE POLICY "quiz_ranking_public_insert"
  ON public.quiz_ranking
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (
    accepted_terms = true
    AND char_length(btrim(player_name)) BETWEEN 2 AND 40
    AND player_age BETWEEN 5 AND 110
    AND correct_count BETWEEN 0 AND 66
    AND questions_answered BETWEEN 1 AND 66
    AND correct_count <= questions_answered
    AND total_time_ms >= (questions_answered * 120)
    AND total_time_ms <= 7200000
    AND selfie_url NOT LIKE 'data:%'
  );

-- 6. Realtime Publication (notifica apenas novos INSERTs para telas abertas no Ranking)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime'
      AND schemaname = 'public'
      AND tablename = 'quiz_ranking'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.quiz_ranking;
  END IF;
END
$$;

-- 7. Bucket Público de Selfies no Storage (limite estrito de 200 KB + entrega via CDN)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'quiz-selfies',
  'quiz-selfies',
  true,
  204800,
  ARRAY['image/jpeg', 'image/webp']
)
ON CONFLICT (id) DO UPDATE
SET public = true,
    file_size_limit = 204800,
    allowed_mime_types = ARRAY['image/jpeg', 'image/webp'];

DROP POLICY IF EXISTS "quiz_selfies_public_insert" ON storage.objects;
CREATE POLICY "quiz_selfies_public_insert"
  ON storage.objects
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (
    bucket_id = 'quiz-selfies'
    AND (storage.foldername(name))[1] = 'selfies'
    AND name ~ '^selfies/selfie_[a-zA-Z0-9_-]{8,64}\.(jpg|webp)$'
  );
