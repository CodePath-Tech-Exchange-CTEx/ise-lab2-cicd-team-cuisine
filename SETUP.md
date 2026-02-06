# SETUP - to be completed by ONE person

## Step 1: Clone the GitHub repository (ONE PERSON).

In GitHub, go to your team's repository. Click on "Code" then on "SSH" and copy the output.

Open Cloud Shell by going to https://shell.cloud.google.com. **Make sure you are in the correct account!**

In the terminal, type `git clone ` and then paste what you copied from GitHub. You should see something like this, with your GitHub org and repository name:

```shell
git clone git@github.com:Github-Org-Name/my-team-repository.git
```

Hit enter, and then use `cd` to change into your team's repository.

```shell
cd my-team-repository
```

## Step 2: Run setup script (ONE PERSON).

**Note:** This only needs to be done ONCE. ***Make sure the person running the code has Owners permission on the GCP project in IAM.***

Fill in the bash variables at the top of `setup.sh`.

* `PROJECT_ID`: The name of your GCP project, such as `melissakohltechx24`.
* `PROJECT_NUMBER`: The project number for the GCP project, found at https://console.cloud.google.com/welcome.
* `SERVICE_NAME`: The website name for your webapp! **NO** uppercase letters or underscores. Use lowercase letters and dashes, such as `our-super-cool-website`.
* `GITHUB_ORG`: The GitHub organization, exactly how it is in the URL when viewing your GitHub repository.
* `GITHUB_REPO`: The GitHub repository with your code.

When all 5 bash variables are filled in (do NOT put "" around any of the values), open your Cloud Shell terminal and run the following:

```shell
./setup.sh
```

This should output something like the following:

```shell
PROJECT_ID: 'melissakohltechx25'
SERVICE_NAME: 'my-ai-shoe-webapp'
SERVICE_REGION: 'us-central1'
SERVICE_ACCOUNT: '354393498738-compute@developer.gserviceaccount.com'
WORKLOAD_IDENTITY_PROVIDER: 'projects/354393498738/locations/global/workloadIdentityPools/github-provider/providers/github-project-repo'
```
## Step 3: Copy output into cloud-run.yml (ONE PERSON).

In step 2, the terminal output should end with a set of variables. Copy the whole block.

Open the file `cloud-run.yml` under the `.github` folder. There are 2 places with **`TODO`** in the file: follow the instructions in each TODO and paste in the output from your terminal into the file.

## Step 4: Run manual-deploy.sh (ONE PERSON).

Make sure you have ***Owners*** permission on the GCP project in IAM.

Fill in the bash variables at the top of `manual-deploy.sh`, using the same values as in Step 2.

Double check that your terminal is in your team repository (the `cd` command from step 1). Then run the following.

```shell
./manual-deploy.sh
```

## Step 5: Commit and push changes to repository (ONE PERSON).

Run the following commands.

```shell
git add .
```

``shell
git commit -m "Set up GitHub Actions."
```

```shell
git push origin main
```

## Step 6: Check that GitHub Actions succeeded.

In GitHub, go to your repository and click on "Actions". Check that the workflows passed. Alternatively, in the main page for your repository, you should see the latest commit message at the top of the files, and either a red X or a green checkmark for the GitHub workflows.
