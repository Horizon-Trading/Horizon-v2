-- NEWS EVENTS
insert into public.news_events (
    id,
    provider,
    provider_event_id,
    ticker,
    title,
    url,
    published_at,
    received_at,
    source,
    author,
    event_type,
    summary,
    raw_data
)
values
(
    '11111111-1111-1111-1111-111111111111',
    'seed',
    'seed-nvda-001',
    'NVDA',
    'NVIDIA announces new AI infrastructure partnership',
    'https://example.com/news/nvda-ai-partnership',
    '2026-09-21T13:30:00Z',
    '2026-09-21T13:30:05Z',
    'Example News',
    'Test Author',
    'partnership',
    'NVIDIA announced a new infrastructure partnership focused on AI computing.',
    '{"source":"seed","sentiment":"positive"}'::jsonb
),
(
    '22222222-2222-2222-2222-222222222222',
    'seed',
    'seed-tsla-001',
    'TSLA',
    'Tesla reports stronger than expected quarterly deliveries',
    'https://example.com/news/tsla-deliveries',
    '2026-09-21T14:00:00Z',
    '2026-09-21T14:00:04Z',
    'Example News',
    'Test Author',
    'earnings',
    'Tesla reported quarterly delivery figures above market expectations.',
    '{"source":"seed","sentiment":"positive"}'::jsonb
),
(
    '33333333-3333-3333-3333-333333333333',
    'seed',
    'seed-aapl-001',
    'AAPL',
    'Apple unveils new hardware lineup',
    'https://example.com/news/aapl-product-launch',
    '2026-09-21T15:15:00Z',
    '2026-09-21T15:15:06Z',
    'Example News',
    'Test Author',
    'product_launch',
    'Apple announced a new hardware lineup during a product event.',
    '{"source":"seed","sentiment":"neutral"}'::jsonb
);


-- MARKET SNAPSHOTS
insert into public.market_snapshots (
    id,
    news_event_id,
    ticker,
    price,
    volume,
    relative_volume,
    market_cap,
    float_shares,
    captured_at
)
values
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '11111111-1111-1111-1111-111111111111',
    'NVDA',
    176.42,
    32500000,
    2.85,
    4300000000000,
    24300000000,
    '2026-09-21T13:32:00Z'
),
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    '22222222-2222-2222-2222-222222222222',
    'TSLA',
    318.77,
    41200000,
    1.92,
    1020000000000,
    3210000000,
    '2026-09-21T14:02:00Z'
),
(
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    '33333333-3333-3333-3333-333333333333',
    'AAPL',
    244.18,
    19800000,
    1.34,
    3670000000000,
    15000000000,
    '2026-09-21T15:17:00Z'
);


-- SIGNALS
insert into public.signals (
    id,
    news_event_id,
    market_snapshot_id,
    ticker,
    score,
    confidence,
    expected_return,
    probability_profit,
    created_at
)
values
(
    '99999999-9999-9999-9999-999999999999',
    '11111111-1111-1111-1111-111111111111',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'NVDA',
    82,
    0.84,
    0.021,
    0.71,
    '2026-09-21T13:33:00Z'
),
(
    '88888888-8888-8888-8888-888888888888',
    '22222222-2222-2222-2222-222222222222',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'TSLA',
    74,
    0.73,
    0.015,
    0.64,
    '2026-09-21T14:03:00Z'
),
(
    '77777777-7777-7777-7777-777777777777',
    '33333333-3333-3333-3333-333333333333',
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'AAPL',
    61,
    0.59,
    0.008,
    0.56,
    '2026-09-21T15:18:00Z'
);
