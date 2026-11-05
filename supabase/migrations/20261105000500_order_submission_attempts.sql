alter table public.orders add column submission_attempts integer not null default 0 check(submission_attempts>=0);
alter table public.orders add column limit_price numeric check(limit_price>0);
