---
tags:
  - docs
  - product
---

# Why a past fire

Snyder is the exam with an answer key. EchoLens is the method you reuse on the next fire.

## Why start with a fire everyone already knows

If we pointed the code at a random forest and it drew a dark blob, we would not know if that blob is real. Snyder has dates and a published perimeter. We can check: did our radar scar land on the real burn? If yes, the method is trustworthy. That is **verification**, not the end product.

## How it works on future data

NISAR keeps flying the same tracks (about every 12 days). When a new fire starts:

1. Take the last pass **before** it and the next pass **after** (or during).
2. Run the same script: dB → despeckle → log-ratio → trust mask → map.
3. You get an outline even if smoke or cloud kills the optical picture.

No new algorithm. New granules in, same steps out. Latency is days (NISAR L2 is typically 36–72 hours), not a live webcam.

## What we are selling

Not “we discovered the Snyder Fire.” Everyone knows that fire.

We are selling: **any two NISAR passes → a briefing a human can use**, proven first on Snyder so judges can see we are not guessing.

Related: [[docs/Product vision]] [[docs/Processing pipeline]]
