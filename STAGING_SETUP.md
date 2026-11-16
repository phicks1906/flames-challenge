# FlamesChallenge full-app staging — setup and safety gate

This is an isolated preparation branch cloned from production v1389 (November 16, 2026). It is NOT a deployed or data-isolated staging environment.

## Production preservation
- Production repo: phicks1906/flames-challenge; branch: main; domain: flameschallenge.com.
- Do NOT merge this branch into main, change the production CNAME, deploy workflows to the production Supabase project, or use production accounts for testing.
- Never publish this unmodified source to a test URL: the frontend references the production Supabase project.

## Required staging infrastructure
1. Create a separate staging repository from the **exact** current production commit (do not use any standalone A3.x prototype). Keep it private until the production integrations are removed. Do not enable GitHub Pages yet.
2. Remove the copied CNAME (`flameschallenge.com`) from the staging repository. Reserve `test.flameschallenge.com` for a future DNS configuration, or use the staging repository's GitHub Pages project URL after checking root-relative paths.
3. Create a separate Supabase staging project under a user-confirmed organization, after quoting/approving any charges. Restore schema, RLS policies, functions, triggers, and required storage buckets to staging using migrations; NO production user, vote, or media data.
4. In the staging copy, replace every production Supabase project URL and publishable key. Search for the production ref in ALL files, not just the client initializer. Keep service-role keys and vendor secrets out of browser code.
5. Disable or retarget .github/workflows/deploy.yml: it deploys Edge Functions to the production Supabase project on pushes to main. Do not run it in staging until it exclusively targets staging, and does not use production workflow secrets.
6. Isolate or disable write-capable integrations: Bunny CDN/storage, Sightengine callback, outbound email/push, OAuth redirects, moderation callbacks, analytics, scheduled jobs, and any external webhooks. Each must use staging-only endpoints and credentials before test actions.
7. Verify service-worker scope, update checks, cache keys, navigation and absolute asset URLs against the separate staging origin. Check that the GitHub Pages project path works; custom staging subdomain is preferable if root-relative URLs require origin-root hosting.
8. Add visible STAGING identification in the staging UI; preserve production build metadata and never increment production version for a staging-only change.
9. Before allowing sign-ins, content creation, voting, uploads, or notifications, verify network requests reach ONLY the staging backend. Smoke-test new user, returning voter, returning competitor, media, vote receipts, results, and all five tabs.
10. After review and explicit approval, port the approved code changes into the then-current main/index.html, bump production build once, validate, and deploy only on a separate explicit command.

## Status
- Git staging preparation branch: created.
- Independent staging GitHub repository: pending.
- Isolated Supabase staging project: pending user organization and cost confirmation.
- Staging website / DNS: pending.
- Production deployment: unchanged.
