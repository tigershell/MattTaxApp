---
name: sales-marketing
description: "Use this skill to help plan how to get a finished app or product in front of users. This is stage 8 of the development pipeline. Trigger when the user says 'sales', 'marketing', 'how do I get users', 'launch', 'grow this', 'promote the app', 'landing page', 'pricing', 'monetise', 'get customers', 'go to market', 'distribution', or when the app is deployed and the user wants to think about user acquisition. Also use when thinking about pricing models, writing app store descriptions, planning a product launch, or evaluating whether a product has commercial potential."
---

# Sales & Marketing Skill

You are running the **Sales & Marketing** stage — stage 8 of the development pipeline. The app is built and deployed. Your job now is to help Matt think through how to get it in front of real users and, if appropriate, generate revenue from it.

Matt is a developer, not a marketer. This skill should be practical and concrete — not buzzword-heavy. Focus on actions he can actually take as a solo builder, not enterprise marketing theory.

---

## Go-To-Market Thinking

Before choosing tactics, get the fundamentals right. Tactics built on a shaky foundation waste effort.

### 1. Who Are You Reaching?

Revisit the target user from the Product Design Brief. Be specific:

- Where do these people spend time online? (Reddit communities, Facebook groups, LinkedIn, Discord, X/Twitter, specific forums, YouTube)
- What do they search for when they have the problem this app solves?
- Are there influencers, communities, or publications they trust?

The channel should follow the user. Don't pick a channel because it feels familiar — pick it because that's where your user actually is.

### 2. What's the Message?

The message needs to answer the user's real question: *"What's in it for me?"*

Craft a one-liner that covers:
- Who it's for
- What problem it solves
- What makes it different

**Bad:** "A smart productivity app with AI features"
**Good:** "For [specific user]: stop doing [painful task] manually — [app name] does it for you in seconds"

Everything else (landing page, social posts, ads) flows from this one-liner.

### 3. What's the Pricing Model?

Choose a model that fits the product and the user. Don't over-complicate this early.

| Model | When It Works | Risk |
|-------|--------------|------|
| **Free** | Building an audience; open-source; funded elsewhere | No revenue |
| **Freemium** | Clear free value + obvious reason to upgrade | Conversion can be low |
| **One-time purchase** | Desktop apps; tools with clear finite value | No recurring revenue |
| **Subscription (monthly/annual)** | Ongoing value; SaaS; regular usage | Higher bar to convert |
| **Pay-per-use** | Variable usage apps; API-based tools | Complex to implement |

For a first app, starting free or with a low one-time price is often smart — it removes the friction of payment and helps you get your first real users giving feedback.

---

## Distribution Channels

Choose 1-2 channels to focus on at launch. Spreading thin across 6 channels is less effective than doing 2 well.

### Direct Outreach

The most underrated launch tactic for indie developers:

- Find 10-20 people who match your target user description
- Reach out personally (Reddit DM, email, LinkedIn) — explain what you built and why
- Ask them to try it and share feedback — not to buy it
- Real feedback from 10 users is worth more than 1,000 impressions

### Communities & Forums

Find communities where your target user already hangs out:

- Post genuinely helpful content about the problem you're solving — not just "check out my app"
- Share the story of building it — developers and indie builders love build-in-public content
- Relevant subreddits, Discord servers, Facebook groups, Slack communities, Hacker News (Show HN)

**Show HN** (news.ycombinator.com) is particularly effective for developer tools and B2B apps.

### Product Hunt

Good for getting initial visibility and early adopters:

- Plan a launch day (typically Tuesday-Thursday for best traffic)
- Prepare: screenshots, a 60-second demo video, a clear tagline, a personal first comment
- Tell your existing network to support the launch on the day
- Respond to every comment

Product Hunt works best when you already have a small audience. Don't rely on it as the only channel.

### App Stores (if applicable)

For mobile apps or desktop apps:

- Apple App Store, Google Play Store, or Microsoft Store
- Each requires a developer account (annual fee)
- ASO (App Store Optimisation): good title, keyword-rich description, quality screenshots
- Reviews matter enormously — prompt happy users to review

### Content Marketing (longer term)

For driving organic search traffic over time:

- Write articles or short videos about the problem you're solving
- Target long-tail search queries your users would type
- One useful piece of content can drive users for years
- This takes time — don't expect quick results

---

## Landing Page

Every app needs a landing page. It doesn't need to be fancy. It needs to be clear.

**Essential elements:**

1. **Headline** — what it does and who it's for (one sentence)
2. **Subheadline** — the key benefit, a bit more detail
3. **Screenshot or demo** — show it working, don't just describe it
4. **3 key features/benefits** — short, specific, user-focused
5. **Clear CTA** — one button: "Get started free", "Download", "Try it", etc.
6. **Social proof** (if available) — testimonials, user count, press mentions

**Tools for building a landing page quickly:**

- **Carrd** — simple, fast, cheap (~$19/year), great for solo builders
- **Notion + Super.so** — if you're comfortable in Notion
- **GitHub Pages + simple HTML** — free, if comfortable with basic HTML

Avoid spending weeks on a landing page before you have any users.

---

## Measuring Success

Define simple metrics to know if the launch is working:

| Metric | What It Tells You |
|--------|-----------------|
| Signups / downloads | Are people interested enough to try it? |
| Activation rate | Are new users completing the core action? |
| Retention (day 7, day 30) | Are people coming back? |
| Conversion rate (free → paid) | Is the value clear enough to pay for? |
| NPS / feedback | Do users actually like it? |

Start with one or two metrics that matter for your specific model. Don't instrument everything before you have users.

---

## Output: Go-To-Market Plan

Save as `docs/go-to-market.md`:

```markdown
# Go-To-Market Plan — [App Name]

## One-Line Pitch
[Who it's for, what it does, why it's different]

## Target User
[Specific description — not "everyone"]

## Pricing Model
[Chosen model and reasoning]

## Launch Channels
[The 1-2 channels to focus on first, and why]

## Launch Plan
[Ordered steps: what happens before, on, and after launch day]

## Landing Page
[URL or plan to build one]

## Success Metrics
[The 2-3 numbers that tell you if it's working]

## 30-Day Action Plan
[Specific actions, not vague goals]
```

---

## Honest Perspective

Most apps don't get users because the builder underestimates distribution. Building is only half the job. Some honest truths:

- Getting your first 10 real users is harder than building the app
- Marketing is a skill you develop — expect the first few attempts to underperform
- Feedback from real users will change the product — stay flexible
- Distribution is part of building, not separate from it

The goal of this stage is not a perfect marketing strategy. It's to get the app in front of enough real users to know if it's solving a real problem.
