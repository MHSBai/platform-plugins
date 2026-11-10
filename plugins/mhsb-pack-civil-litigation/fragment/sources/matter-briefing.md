<!--
MHSB modification notice (Apache License, Version 2.0, Section 4(b)).
Modified by MHSB Solutions on 2026-11-03.
Original: anthropics/claude-for-legal, litigation-legal/skills/matter-briefing/SKILL.md, commit 4a6c651889c97cc9140580363c73e0eb17379c2b.
Original license: Apache-2.0. The original copyright and license notices are retained.
Change note: Rewritten from the litigation matter briefing into the civil litigation fragment's briefing view for /brief: posture, recent change, next entered date, open questions, staleness and the reassessment prompt are kept; exposure, materiality and the local log reads are removed.
-->

# Civil litigation matter briefing

This note defines the single-matter briefing that the civil litigation pack contributes to `/brief`. The briefing gives the attorney a short read on one matter before a client call, a hearing or a conversation with co-counsel. It reads the record and reports; it predicts no outcome and recommends no strategy.

## Gate

The briefing is produced only for a matter that exists in the platform with a conflicts record. A matter with conflicts status "not run" is refused with the reason, and the attorney is pointed to the intake.

## Briefing shape

1. Coverage statement.
2. Header: matter identifier, stage as recorded, responsible attorney, last activity date, conflicts status. If the last recorded activity is more than 30 days old, the header carries a staleness flag.
3. Summary: one paragraph on the current posture from the recorded notes, naming the pivotal fact if one is recorded.
4. Recent change: the last three to five recorded events, most recent first. A thin history is stated as thin.
5. Next: the next entered date and its category (answer deadline, discovery cutoff, hearing, mediation), other entered dates in the next 30 days, and decisions the record marks as pending.
6. Owners: who is assigned, and any role the fragment expects that is unassigned.
7. Reassessment prompt: questions for the attorney, not answers. Has the stage changed without the record changing? Has a new party, witness or document arisen that needs a conflicts check or a preservation update? Is an entered date now in the warning ladder?
8. Open questions recorded on the matter.
9. Purpose section, only when the user states a purpose: questions to ask, decisions to obtain, updates to record afterwards.
10. Not retrieved.

## Dates

Dates from the docket that the firm has entered govern. The briefing does not compute answer deadlines, discovery cutoffs or appeal windows.

## Register

The briefing states what is recorded and marks what is not. A recently opened matter yields a short briefing, and that is correct.

## After the conversation

Where the briefing is stale, the output notes that the attorney may wish to record what is discussed. The plugin does not record it.
