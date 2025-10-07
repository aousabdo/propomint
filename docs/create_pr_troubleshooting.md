# Troubleshooting the "Create PR" Step

When the GitHub "Create PR" automation fails, it is usually because the
local environment is missing authentication or the working branch has not
been pushed. The checklist below walks you through the common causes and
provides commands you can run locally to fix them.

## 1. Make sure the branch exists on GitHub

The PR workflow can only create a pull request for a branch that is
published to the remote repository.

```bash
git status -sb            # Confirm you are on the expected branch
git remote -v             # Verify the remote named "origin" points to GitHub
git push -u origin <branch-name>
```

If the branch was created locally, the final `git push` with the `-u`
flag establishes the upstream tracking reference that `gh pr create` and
other automations expect.

## 2. Authenticate the GitHub CLI

The CLI needs an access token that has the `repo` scope. Re-run the
login wizard if you are unsure whether the token is valid.

```bash
gh auth status            # Shows the currently authenticated user
gh auth login             # Regenerates the token if the status command fails
```

If your organization requires SSO, make sure the token is authorized for
that organization. GitHub will show a link in the terminal that you need
to approve in the browser.

## 3. Provide required metadata

Autom automations often rely on the PR title and body. When the
non-interactive job does not supply them, the API call fails with
validation errors. Always pass the title and body explicitly:

```bash
gh pr create \
  --title "Improve agent prompts" \
  --body  "## Summary\n- …" \
  --base main \
  --head <branch-name>
```

Make sure `<branch-name>` matches the branch you pushed in step 1.

## 4. Inspect detailed error messages

Run the command with verbose logging enabled to surface the underlying
HTTP error. This makes it easy to spot missing permissions or
validation issues.

```bash
gh pr create --verbose
```

The verbose output includes the exact REST endpoint and response payload.
Common issues include:

* `404 Not Found` – the branch name is wrong or the repository slug is
  misconfigured.
* `422 Validation Failed` – the PR already exists or the target branch
  matches the base branch.
* `401 Unauthorized` – the token has expired or lacks the `repo` scope.

## 5. Re-run the job locally before automating

Before retrying the automation, confirm that you can create a PR manually
from your workstation using the same command. Once the manual run
succeeds, copy the working command into the CI/CD script or agent prompt.

## 6. Optional: scriptable health check

If you orchestrate the workflow through an agent, add a lightweight
pre-flight check that verifies authentication and branch publishing
before attempting to create the PR. A minimal example:

```bash
set -euo pipefail

if ! gh auth status >/dev/null 2>&1; then
  echo "❌ GitHub CLI is not authenticated. Run 'gh auth login'." >&2
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if ! git ls-remote --exit-code --heads origin "${BRANCH}" >/dev/null; then
  echo "🔄 Pushing branch ${BRANCH} to origin" >&2
  git push -u origin "${BRANCH}"
fi

gh pr create --title "$TITLE" --body "$BODY" --base "$BASE" --head "$BRANCH"
```

Embedding this check prevents the PR step from failing repeatedly and
surfacing only generic error text in the agent transcript.
