# 🔥 FlamesChallenge

A modern reimagining of FlamesChallenge.com — a social voting platform where users vote on trending, local, and national topics, challenge their friends, and climb a leaderboard.

**Live demo:** Once you deploy to GitHub Pages, your URL will be `https://YOUR-USERNAME.github.io/flames-challenge/`

-----

## ✨ What’s improved over the original

|Original (WordPress + SocialV)   |This version                                  |
|---------------------------------|----------------------------------------------|
|Heavy WordPress + Elementor stack|Single HTML file — loads in under 1 second    |
|Generic SocialV theme look       |Custom bold “fire” design system              |
|Slow, plugin-bloated             |Zero dependencies, pure HTML/CSS/JS           |
|Limited mobile experience        |Mobile-first, native share sheet support      |
|Standard polls                   |Animated results, streak system, point bonuses|
|No real-time feel                |Instant voting feedback + live leaderboard    |
|Hard to customize                |Edit one file. That’s it.                     |

-----

## 🚀 Deploy to GitHub Pages (5 minutes)

### Option A: Drag-and-drop (easiest)

1. Go to [github.com/new](https://github.com/new) and create a repo named `flames-challenge`
1. On the new repo page, click **“uploading an existing file”**
1. Drag `index.html` (and this `README.md`) into the upload area, then click **Commit changes**
1. Go to **Settings → Pages** (left sidebar)
1. Under **Source**, select **Deploy from a branch** → **main** → **/ (root)** → **Save**
1. Wait ~1 minute. Your site is live at `https://YOUR-USERNAME.github.io/flames-challenge/`

### Option B: Custom domain (flameschallenge.com)

After Option A is working:

1. In your domain registrar (where you bought flameschallenge.com), add these DNS records:
   
   ```
   A     @    185.199.108.153
   A     @    185.199.109.153
   A     @    185.199.110.153
   A     @    185.199.111.153
   CNAME www  YOUR-USERNAME.github.io
   ```
1. In GitHub: **Settings → Pages → Custom domain** → enter `flameschallenge.com` → Save
1. Check **Enforce HTTPS** once it’s available (can take up to 24 hours)

-----

## 🛠 How it works (technical)

Everything is one file: `index.html`. It contains:

- **HTML** — semantic markup for the landing page, polls, leaderboard, modals
- **CSS** — custom design system with CSS variables (colors, spacing, typography). No frameworks.
- **JavaScript** — vanilla JS, no dependencies. State persists in your browser via `localStorage`.

**Fonts** are loaded from Google Fonts: *Anton* (display) and *DM Sans* (body) and *Bricolage Grotesque* (accents).

### Data model

```js
user    = { name, avatar, points, streak, votes: { pollId: optionIndex } }
poll    = { id, category, question, options: [{label, votes}], hours }
```

All vote data is stored locally in the browser. **For real multi-user voting across devices, see the “Adding a real backend” section below.**

-----

## 🔌 Adding a real backend (Supabase, free tier)

Right now, each visitor sees their own local data. To enable real shared voting + a global leaderboard:

1. Create a free account at [supabase.com](https://supabase.com) and a new project.
1. In the SQL editor, run:
   
   ```sql
   create table polls (
     id text primary key,
     category text,
     question text,
     options jsonb,
     hours_remaining int,
     created_at timestamptz default now()
   );
   
   create table votes (
     id uuid primary key default gen_random_uuid(),
     poll_id text references polls(id),
     user_id text,
     option_index int,
     created_at timestamptz default now(),
     unique(poll_id, user_id)
   );
   
   create table users (
     id text primary key,
     name text,
     avatar text,
     points int default 0,
     streak int default 0
   );
   ```
1. Get your Supabase URL + anon key from **Project Settings → API**.
1. In `index.html`, add the Supabase client in the `<head>`:
   
   ```html
   <script type="module">
     import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
     window.supabase = createClient("YOUR_URL", "YOUR_ANON_KEY");
   </script>
   ```
1. Replace the `localStorage` calls in the script section with Supabase queries. Ask me (“Claude, swap localStorage for Supabase in this file”) and I’ll do the rewrite for you.

-----

## 🎨 Customizing the design

All colors and fonts live as CSS variables at the top of the `<style>` block:

```css
:root {
  --ember: #ff6a2c;       /* main accent — change this to re-theme */
  --flame: #ff3d3d;
  --coral: #ff5e87;
  --gold:  #ffc857;
  --bg:    #0a0705;       /* dark background */
  /* ...etc */
}
```

To change the polls: scroll to the `SEED_POLLS` array in the script section. Each poll is just:

```js
{ id:"p11", category:"trending", question:"Your question?", options:[
  {label:"Option A", votes:0}, {label:"Option B", votes:0}
], hours:24 }
```

-----

## 📱 Features included

- ✅ Mobile-first responsive design
- ✅ Native share sheet (mobile) + clipboard fallback (desktop)
- ✅ Animated vote results
- ✅ Points system (10/vote, +5 majority bonus)
- ✅ Streak tracking
- ✅ Leaderboard with “you” highlighting
- ✅ Three categories: Trending / Local / National
- ✅ Avatar picker, no email required
- ✅ Reduced-motion support (accessibility)
- ✅ Open Graph tags for link previews
- ✅ Subtle fire-themed animations & noise texture

## 📂 File structure

```
flames-challenge/
├── index.html       ← the entire site
└── README.md        ← this file
```

That’s it. Two files. Deploy and go.

-----

Built with 🔥 by Claude. Edit freely.
