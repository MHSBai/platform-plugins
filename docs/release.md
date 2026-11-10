# Release procedure

Applies to every tag of MHSBai/platform-plugins from 0.1.0 onward.

## Controls

1. Protected main. No direct pushes. Changes arrive by pull request with the `lint`, `tests` and `release-gate` checks green, linear history, signed commits, no force pushes and no deletion. Administrators are included. Until a signed tag exists, main is the only installable ref, so `release-gate` runs `python tools/lint.py --release` on every pull request and every push to main as well as on `v*` tags. `agent-scan` becomes a required check once the `SNYK_TOKEN` secret is set. The job is never skipped: it concludes success only when the scan ran and passed, and fails with the reason when no scan ran, including on a pull request from a fork, which GitHub runs without secrets. A fork pull request therefore stays red until a maintainer pushes its branch to this repository. The commands that set this are in HANDOFF.md.
2. Signed tags. Every release tag is an annotated tag signed with the release key: `git tag -s vX.Y.Z -m "Release X.Y.Z"`. Unsigned tags are not releases. A tag ruleset forbids updating or deleting `v*` tags.
3. Tag-pinned sources. Firms and the directory consume a tag, never a branch. Users add the marketplace as `MHSBai/platform-plugins#vX.Y.Z`; the directory submission tracks the release tag. Within a tag, relative-path plugin sources resolve to the same commit.
4. Second identity with a hardware key. A release requires a second GitHub identity, distinct from the day-to-day account, whose sign-in and signing key sit on a hardware security key. That identity approves the release pull request and creates the signed tag. The day-to-day account cannot create `v*` tags.

## Steps

1. Bump `defaults.version` in `catalog/manifest.yaml`, run `python tools/gen_manifest.py`, and add a CHANGELOG entry written for staff at a firm.
2. Run the release gate locally and paste the output into the pull request:

   ```bash
   python tools/gen_manifest.py --check && python tools/lint.py --release && python -m pytest -q
   ```

   `--release` turns warnings into errors. A synthetic adoption record (decision 0002) fails it, and so does a general availability connector plugin whose endpoint fails `tools/release_check.py` (host outside the recorded edge, or no authenticated `initialize` returning the recorded server name and version) or which lacks a privacy policy or terms of service URL (rule L16, HANDOFF item 8). A pack held at pilot with `PENDING ADOPTION` (decision 0004) is unlisted and does not block a release.
3. Run the firm-name check from outside this repository (HANDOFF item 5) and record zero hits.
4. Merge with the second identity's approval.
5. With the second identity, on the merge commit: `git tag -s vX.Y.Z -m "Release X.Y.Z"` and `git push origin vX.Y.Z`.
6. Verify: `git tag -v vX.Y.Z`, then `claude plugin validate .` on a fresh clone at the tag.
7. `/start` shows the delta from the CHANGELOG once the release is installed; `/check-setup` warns users who remain behind.
