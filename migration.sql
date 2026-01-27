-- 기존 poly_events 테이블에 새 컬럼 추가 (마이그레이션)
-- Supabase SQL Editor에서 실행하세요

-- 1. 새 컬럼 추가
ALTER TABLE poly_events ADD COLUMN IF NOT EXISTS volume_24hr NUMERIC;
ALTER TABLE poly_events ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE poly_events ADD COLUMN IF NOT EXISTS outcomes JSONB;
ALTER TABLE poly_events ADD COLUMN IF NOT EXISTS api_created_at TIMESTAMPTZ;

-- 2. 새 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_poly_events_volume_24hr ON poly_events(volume_24hr DESC);
CREATE INDEX IF NOT EXISTS idx_poly_events_category ON poly_events(category);
CREATE INDEX IF NOT EXISTS idx_poly_events_api_created_at ON poly_events(api_created_at DESC);
