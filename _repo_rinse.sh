#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

git pull
git clean -xfd
git submodule foreach --recursive git clean -xfd
git reset --hard
git submodule foreach --recursive git reset --hard
git submodule update --init --recursive

shopt -s nullglob

old_zips=()
for zip_root in */zips; do
    while IFS= read -r -d '' folder; do
        # Checkouts give files new timestamps, so sort by version instead.
        mapfile -d '' -t zips < <(
            find "$folder" -maxdepth 1 -type f -name '*.zip' -printf '%f\0' |
                LC_ALL=C sort -zVr
        )
        for zip in "${zips[@]:10}"; do
            old_zips+=("$folder/$zip")
        done
    done < <(find "$zip_root" -type d -print0)
done

if (( ${#old_zips[@]} == 0 )); then
    echo "No old ZIP versions to prune."
    exit 0
fi

git rm --ignore-unmatch -- "${old_zips[@]}"

if ! git diff --cached --quiet -- "${old_zips[@]}"; then
    git commit --only -m "Prune old ZIP versions (keep latest 10 per folder)" -- "${old_zips[@]}"
    git push
fi
