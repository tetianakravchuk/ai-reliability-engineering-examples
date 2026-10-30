# WPH Interactive Architecture Map

A **sanitized, conceptual**, clickable engineering case study for LinkedIn and recruiting. It does not expose private WPH code, real infrastructure, or internal credentials.

## Run locally

```bash
cd architecture-map
npm install
npm run dev
```

## Deploy to Vercel

Import `tetianakravchuk/ai-reliability-engineering-examples` in Vercel and set **Root Directory** to `architecture-map`. Framework preset: **Vite**. Build command: `npm run build`; output directory: `dist`. Deploy after merging the PR.

## Features

- React Flow zoomable/pannable system map with clickable nodes
- Engineering decisions, risks, validation and hiring skills per node
- Interactive, deterministic 4-step checkpoint race-condition simulation
- Links to public runnable PostgreSQL integration tests
- Responsive design and clear conceptual/synthetic-data disclosures

The failure simulation is illustrative and does **not** execute SQL. Real integration tests are in the repository root. Keep the main WPH repository private.

## LinkedIn publishing

Screen-record a 15–20 second tour of the map, attach the recording to a post, and add the public Vercel URL. LinkedIn does not embed this interactive app in the feed.
