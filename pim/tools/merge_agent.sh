#!/bin/bash
# Merge one agent's worktree branch into master the pim way, with terse output.
#
#   tools/merge_agent.sh BRANCH -m "Merge ...: what was verified" [--push]
#
# Steps, stopping at the first problem:
#  1. we are on master, and pim/ has no uncommitted tracked changes;
#  2. scope: the branch changes nothing outside pim/ since the merge-base;
#  3. prints the files both master and the branch changed since the
#     merge-base (overlap; informational);
#  4. git merge --no-ff -m MSG (a conflict stops here with the merge left in
#     progress and the conflicted files listed: resolve, commit, then rerun
#     with --push --no-merge);
#  5. tools/quick_checks.sh, adding bsv/run_win_tb.sh when the merge touched
#     pim/bsv/Win* or pim/psi/win*;
#  6. with --push: git push origin master, then unlock and remove the
#     branch's worktree and delete the branch with git branch -d (which
#     refuses if the branch is unmerged).
# A failed check leaves the merge commit in place, unpushed, for you to
# fix or undo.  The script never force-pushes or rewrites history.
#
# Exit: 0 done, 1 check failed, 2 usage/precondition, 3 merge conflict.
set -u
BR=""; MSG=""; PUSH=0; MERGE=1
while [ $# -gt 0 ]; do
    case "$1" in
        -m) MSG=$2; shift 2 ;;
        --push) PUSH=1; shift ;;
        --no-merge) MERGE=0; shift ;;
        -*) echo "usage: $0 BRANCH -m MSG [--push] [--no-merge]"; exit 2 ;;
        *) BR=$1; shift ;;
    esac
done
[ -n "$BR" ] || { echo "usage: $0 BRANCH -m MSG [--push] [--no-merge]"; exit 2; }
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel) || exit 2
cd "$ROOT" || exit 2
TRAILER="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

[ "$(git rev-parse --abbrev-ref HEAD)" = master ] || { echo "not on master"; exit 2; }
git rev-parse --verify -q "$BR" >/dev/null || { echo "no branch $BR"; exit 2; }
if git status --porcelain --untracked-files=no -- pim | grep -q .; then
    echo "pim/ has uncommitted changes:"; git status --short --untracked-files=no -- pim
    exit 2
fi

if [ $MERGE = 1 ]; then
    [ -n "$MSG" ] || { echo "need -m MSG"; exit 2; }
    MB=$(git merge-base master "$BR")
    OUT=$(git diff --name-only "$MB" "$BR" | grep -v '^pim/')
    if [ -n "$OUT" ]; then
        echo "SCOPE: branch changes files outside pim/:"; echo "$OUT"; exit 2
    fi
    N=$(git rev-list --count master.."$BR")
    OV=$(comm -12 <(git diff --name-only "$MB" master | sort) \
                  <(git diff --name-only "$MB" "$BR" | sort) 2>/dev/null)
    echo "branch: $N commits ahead; master moved $(git rev-list --count "$MB"..master) since merge-base"
    [ -n "$OV" ] && { echo "overlap (both changed):"; echo "$OV" | sed 's/^/  /'; }
    case "$MSG" in *"$TRAILER"*) ;; *) MSG="$MSG

$TRAILER" ;; esac
    if ! git merge --no-ff -q -m "$MSG" "$BR" >/dev/null 2>&1; then
        C=$(git diff --name-only --diff-filter=U)
        if [ -n "$C" ]; then
            echo "CONFLICT (merge left in progress):"; echo "$C" | sed 's/^/  /'
            exit 3
        fi
        echo "merge failed:"; git merge --no-ff -m "$MSG" "$BR"; exit 3
    fi
    echo "merged: $(git log -1 --format='%h %s')"
fi

CHANGED=$(git diff --name-only HEAD^1 HEAD)
QC_WIN=0
echo "$CHANGED" | grep -Eq '^pim/(bsv/Win|psi/win)' && QC_WIN=1
QC_WIN=$QC_WIN pim/tools/quick_checks.sh || exit 1

if [ $PUSH = 1 ]; then
    git push -q origin master 2>&1 | grep -v '^$' ; echo "pushed: $(git rev-parse --short HEAD)"
    WT=$(git worktree list --porcelain | awk -v b="refs/heads/$BR" '
        /^worktree /{w=substr($0,10)} $0=="branch " b {print w}')
    if [ -n "$WT" ]; then
        git worktree unlock "$WT" 2>/dev/null
        git worktree remove "$WT" || { echo "worktree $WT not removed"; exit 1; }
        echo "removed worktree $WT"
    fi
    git branch -d -q "$BR" && echo "deleted branch $BR"
fi
exit 0
