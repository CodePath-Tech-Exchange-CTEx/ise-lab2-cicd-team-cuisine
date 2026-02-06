# TODO: Replace with your team name

## Our Team

TODO: Replace with your team members

# Setup

One person needs to follow SETUP.md to complete setup. Ignore this if it is already done for you!

# How to Run the Streamlit App

## Step 1: Clone the repository.

In GitHub, go to your team's repository. Click on "Code" then on "SSH" and copy the output.

Open Cloud Shell by going to https://shell.cloud.google.com. **Make sure you are in the correct Google account!**

In the terminal, type `git clone` and then paste what you copied from GitHub. You should see something like this, with your GitHub org and repository name:

```shell
git clone git@github.com:Github-Org-Name/my-team-repository.git
```

Hit enter, and then use `cd` to change into your team's repository.

```shell
cd my-team-repository
```

## Step 2: Run the Streamlit app.

Run this command in the terminal to install the needed packages.

```shell
pip install -r requirements.txt
```

Run the following command to run the app locally. Follow the URL that is outputted, or in the Cloud Shell Editor, go to the upper right corner and hover over the icons until you find "Web Preview". Then click on "Preview on port 8080." You should see the app!

```shell
streamlit run app.py
```

**Note:** When you make changes, you just
need to refresh the webpage and the new changes should appear (*you do NOT need to rerun the previous command while you are actively making changes*).

## Step 3: Using Docker to run the Streamlit app

Docker simply creates a virtual environment for only your app. This is what we will use to
deploy our app continuously.

Fortunately, we already have a script that builds and starts Docker for us. Run the 
following command to build the container and start the server locally.

```shell
./run-streamlit.sh
```
**Note:** This also outputs the same local URL that the previous command output. The only difference is that instead of running the webapp on *your* Cloud Shell, it is running it *within a Docker container*. Don't worry too much about understanding this now, but **if this command fails, your automatic deployment through GitHub Actions will also fail**.

## Step 4: Manual deployment.

First, make sure someone in your team has gone through the steps in SETUP.md. Make sure you have ***Owners*** permission on the GCP project in IAM.

Run the following command to deploy your webapp.

```shell
./manual-deploy.sh
```

# Making Code Changes

After you are assigned a task in the project, how do you actually make the changes and test them out? Follow these steps:

1. Change into your team's repository in Cloud Shell using `cd`.
2. Run `git pull --rebase` to pull in any of your teammates changes.
3. Make changes to the code in Cloud Shell Editor.
4. Run `streamlit run app.py` to see the changes in action (Step 2 above). Don't use CTRL-C and let this command continuously run.
5. Continue to make changes and refresh the web page with the app to see the new changes.
6. When you are ready to be done, use CTRL-C to stop the `streamlit run` command.
7. Check that your changes work in a container by running `./run-streamlit.sh` and make sure you see your changes.
8. Use git to add, commit, and push your changes. It might be good to run `git pull --rebase` before pushing your changes, or optionally use git branches to avoid conflicts with your teammates.
9. In GitHub, once you push to the main branch, check that the Actions succeeded and deployed your changes.
