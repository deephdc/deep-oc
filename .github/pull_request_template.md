# Template for adding modules to `MODULES.yml`


## To PR author

* Please fill the following fields:
  - Code repo: `https://github.com/<your-username>/<reponame>`
  - Docker repo: `https://github.com/<your-username>/DEEP-OC-<reponame>`
  - default git branch in your repos: `<branchname>` (default is usually `master` but some users use `main` for example) 

* The change to `MODULES.yml` should look like the following:
> `- module: https://github.com/deephdc/UC-<your-username>-DEEP-OC-<reponame>`

* If you module belongs to the [iMagine project](https://www.imagine-ai.eu/), please remember to include the tag `"vo.imagine-ai.eu"` in the `metadata.json`:
```json
    "keywords": [
        ...,
        "vo.imagine-ai.eu"
    ],
```

* Remember to select :ballot_box_with_check: `Allow edits by mantainers`


## To the PR reviewer
  
In the case the PR is from a **non-deephdc** member, remember you have to perform the following steps for integration:

### 1. Name check

Check the PR change follows the following convention (edit the PR is needed):

> `- module: https://github.com/deephdc/UC-<original_account>-DEEP-OC-<original_repo_name>`

Note: `UC` stands for _User Contributed_.
So for example a user with Docker repo:
- https://github.com/adnaneds/DEEP-OC-unet

should have the following repo in `deephdc`:
- https://github.com/deephdc/UC-adnaneds-DEEP-OC-unet ⬅ This is the repo that should be included in the PR change to `MODULES.yml`

### 2. Fork creation

Create forks of both `Code repo` and `Docker repo` in the `deephdc` organization. 
This is done so that our Jenkins plugin can monitor the changes of the repo (it can only do so for repos inside `deephdc`).

When performming the forks, remember to un-select `Copy the master branch only` as we want to fork all branches.

The forks should use the following naming conventions:
- For code repos: `UC-<original_account>-<original_repo_name>`
- For Docker repos:`UC-<original_account>-DEEP-OC-<original_repo_name>`

For example forking:
- https://github.com/adnaneds/unet
- https://github.com/adnaneds/DEEP-OC-unet

would give the following forks:
- https://github.com/deephdc/UC-adnaneds-unet
- https://github.com/deephdc/UC-adnaneds-DEEP-OC-unet

In case of doubt check the Jenkins badges in the respective `README`s of the repos (code and docker). They should display the expected repo names for `deephdc` forks.

### 3. Keep the forks updated

In order to have the forks updated, so that they continously reflect the changes in upstream, we are going to use [Github Actions](https://github.com/features/actions).
So **for each of the two forks**, go to `Actions` &#8594; `set a workflow yourself`.

Then copy in the editor the following workflow, **remebering to add the corresponding UPSTREAM_REPO**. Following the previous example:
- https://github.com/deephdc/UC-adnaneds-unet ➡ **UPSTREAM_REPO**: https://github.com/adnaneds/unet.git
- https://github.com/deephdc/UC-adnaneds-DEEP-OC-unet ➡ **UPSTREAM_REPO**: https://github.com/adnaneds/DEEP-OC-unet.git

```yaml
# Script is (loosely) based on two references:
# * https://stackoverflow.com/questions/23793062/can-forks-be-synced-automatically-in-github
# * https://stackoverflow.com/questions/69918635/how-to-keep-all-branches-and-tags-in-sync-in-a-fork-or-mirror-repo
# [!] Note: Do not do a force push to not overwrite the .github/workflow/main.yml file.

# We are not using a predefined action (eg. [1]) to not go through the hassle of having to
# manage Github Personal Access Tokens for deephdc.
# [1]: https://github.com/repo-sync/github-sync


name: Sync fork with upstream
on:
  schedule:
     # run at max frequency
    - cron:  '* * * * *'

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:

  build:
    
    runs-on: ubuntu-latest

    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Sync fork with upstream
        run: |
          
          #########################################################
          # YOU SHOULD UPDATE THIS LINE
          #########################################################

          UPSTREAM_REPO=https://github.com/<username>/<reponame>.git

          #########################################################

          # Bot config
          git config user.name 'github-actions[bot]'
          git config user.email 'github-actions[bot]@users.noreply.github.com'
                    
          # Add remote
          git remote add upstream $UPSTREAM_REPO
          git fetch upstream

          # Keep track of branch names
          origin_branches=$(git branch -r | grep -v 'HEAD' | grep 'origin/' | cut -f 2 -d '/')
          upstream_branches=$(git branch -r | grep 'upstream/' | cut -f 2 -d '/')
          
          old_branches=$(comm -13 <(printf '%s\n' "${upstream_branches[@]}" | LC_ALL=C sort) <(printf '%s\n' "${origin_branches[@]}" | LC_ALL=C sort))
          new_branches=$(comm -13 <(printf '%s\n' "${origin_branches[@]}" | LC_ALL=C sort) <(printf '%s\n' "${upstream_branches[@]}" | LC_ALL=C sort))
          existing_branches=$(comm -13 <(printf '%s\n' "${new_branches[@]}" | LC_ALL=C sort) <(printf '%s\n' "${upstream_branches[@]}" | LC_ALL=C sort))
          
           # Delete old branches from origin
          echo "# Deleting old branches ..."
          for tmp_branch in $old_branches; do
            echo "## Processing $tmp_branch ..."
            git push origin --delete $tmp_branch
          done
          
          # Create origin branches for new upstream branches
          echo "# Creating new branches ..."
          for tmp_branch in $new_branches; do
            echo "## Processing $tmp_branch ..."
            git checkout -b $tmp_branch upstream/$tmp_branch
            git push origin
          done
          
          # Merge changes from upstream to origin for existing branches
          echo "# Merging existing branches ..."
          git config --add checkout.defaultRemote origin
          for tmp_branch in $existing_branches; do
            echo "## Processing $tmp_branch ..."
            git checkout $tmp_branch
            git merge --no-edit upstream/$tmp_branch
            git push origin
          done
          
          # Sync tags
          git tag -d $(git tag -l)
          git fetch upstream --tags --quiet
          git push origin --tags --force

       # Keep the workflow running
       # Github automatically disbales a workflow is the repo hasn't seen activity in the last 60 days.
       # This steps will make a dummy commit after 50 days of inactivity to avoid the disabling.
      - uses: gautamkrishnar/keepalive-workflow@v1

```

### 4. Add the module as a git submodule

Clone the `deep-oc` repo and add the module:

```console
git submodule add https://github.com/deephdc/UC-<original_account>-DEEP-OC-<original_repo_name>
```

If the user has a default `<branchname>` different from `master` (eg. `main`), you should add this parameter in the submodule command:

```console
git submodule add -b <branchname> https://github.com/deephdc/UC-<original_account>-DEEP-OC-<original_repo_name>
```

Then commit back and push the changes to the repo.
