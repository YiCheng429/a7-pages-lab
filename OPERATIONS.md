# A7 release operations

The homepage is rendered by Jekyll from `index.md` and `README.md`. Deploy from **Settings → Pages → GitHub Actions** for the gated release. The original branch-based homepage is preserved in the first commit.

1. Create an expiring **classic** GitHub PAT with **public_repo** under your own account. Store it only as the repository Actions secret **TOKEN**.
2. Run **Update activity log** on main. Verify the commit edits only the marked README section and that its SHA is the head SHA of **Pages release gate**.
3. Open the public homepage. Record the activity and copy the contents of `version.txt`.
4. In **Pages release gate → Run workflow**, check **Demo only: add a broken internal link to the candidate**. The checkout is disposable; main is unchanged.
5. In that run, confirm **Validate artifact** fails on `./__missing-release-gate__.html`; upload and deploy are skipped. Re-read the public `version.txt` and compare it byte-for-byte with step 3.
6. Run **Pages release gate** once with the box unchecked. Confirm green validation and deploy, then confirm the public version matches the new run.

Do not capture a token value, token creation result, or other credentials in evidence screenshots. The validator intentionally checks only local homepage links and anchors; it does not probe external activity URLs.
