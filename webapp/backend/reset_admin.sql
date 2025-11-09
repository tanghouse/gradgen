-- Reset admin account for testing
-- This clears all tier flags and generation counters

-- Show current status
SELECT
    email,
    has_used_free_tier,
    has_purchased_premium,
    premium_generations_used,
    referral_discount_eligible
FROM users
WHERE email = 'admin@gradgen.ai';

-- Reset tier flags
UPDATE users
SET has_used_free_tier = FALSE,
    has_purchased_premium = FALSE,
    premium_generations_used = 0,
    referral_discount_eligible = FALSE
WHERE email = 'admin@gradgen.ai';

-- Show updated status
SELECT
    email,
    has_used_free_tier,
    has_purchased_premium,
    premium_generations_used,
    referral_discount_eligible
FROM users
WHERE email = 'admin@gradgen.ai';

-- Show generation history (preserved)
SELECT
    COUNT(*) as total_jobs,
    SUM(CASE WHEN tier = 'free' THEN 1 ELSE 0 END) as free_jobs,
    SUM(CASE WHEN tier = 'premium' THEN 1 ELSE 0 END) as premium_jobs
FROM generation_jobs
WHERE user_id = (SELECT id FROM users WHERE email = 'admin@gradgen.ai');
