---
name: report
description: 'Lists the report catalog, runs one report now with the coverage statement, or prepares service
  delivery setup. Use when a user asks, for example: "run the incident aging report"; "list available
  reports"; "schedule the monday report"; "set up a weekly report".'
metadata:
  register: document
  connector: firm
  pack: mhsb-operations
  triggers:
  - run the incident aging report
  - list available reports
  - schedule the monday report
  - set up a weekly report
---

# /report

## Promise

Lists the report catalog, runs one report now with the coverage statement, or prepares service delivery setup.

## Inputs

- The request: list the catalog, run a report now, or set up service delivery.
- The report identifier, for a run or a setup.

A question about a client, matter or case goes to the firm connector. The user does not have to name the platform.

## Clarification rule

Ask as many questions as it takes on three points. Never guess any of them.

- Identity. Which client, matter, lead or person is meant. If two records could match, list both and ask.
- Authority. Who may approve or receive the result. If the Firm Profile does not name that person, ask.
- Dates. Which date, and in which time zone. If the record has no date, write "date not established". Name the source and the person who can supply it.

There is no limit on these questions. Go on only when all three are settled.

## Procedure

1. Settle which of the three the user wants.
2. To list, show the operations reports and the firm's pack reports.
3. To run, call the report through the firm connector and show the result.
4. To set up delivery, explain the scheduled task that calls the report by its identifier. Recipients come from the Firm Profile only.
5. Refuse when the report's anchoring field is unmapped.

## Output shape

1. Line 1: the coverage statement.
2. For a list: one line per report with name, cadence and recipients.
3. For a run: the counsel-review line where a date or legal consequence appears, the rows, the data-gaps section and a provenance line per row.
4. For setup: the steps, the report identifier and the recipients on file.
5. Section: not retrieved.

## Coverage statement

Every output opens with a coverage statement. It gives the scope searched, the record count, whether every page was read, and the time of the read. If the connector marks the read as incomplete, give the reason. List each item that could not be read under the heading "not retrieved". A failed or partial read is never shown as an empty result.

## Refusals

This command does not do the following. It says so and stops.

- Legal research, filings or citations.
- Trust account actions.
- Sending anything. A person reviews and sends every draft.
- Deleting, bulk edits or any write to the platform.
- Adding or changing a recipient. That needs an approver-confirmed change request.
- Copying report rows into an email.
