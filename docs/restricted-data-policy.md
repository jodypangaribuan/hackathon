# Restricted Data and Secret Policy

## Scope

The organizer dataset, raw review exports, annotations, model weights, predictions, local databases, credentials, and runtime secrets must not be added to the public repository unless competition terms explicitly permit publication and the team has completed a privacy/license review.

## Git Policy

The root `.gitignore` excludes:

- `Datasets/` and `Datasets.zip`.
- Raw, interim, processed, annotation, split, and generated ML data.
- Model weights and serialized model formats.
- Experiment caches, logs, local databases, and notebook caches.
- `.env` files, keys, certificates, service-account files, and secret manifests.
- Generated ML-to-app exports.

README files, schemas, configs, source code, and documentation remain trackable.

## Important Existing-Tracking Warning

At the time this policy was created, the workspace Git index already contained files under `Datasets/` and `Datasets.zip`. `.gitignore` prevents new untracked files from being added accidentally, but it does not remove already tracked content or erase Git history.

Before publishing or sharing the repository, the team must decide whether competition terms permit those files to remain tracked. If not, perform a separate reviewed migration to remove them from the index and, if required, rewrite repository history. Do not run history-rewriting commands casually.

## Pre-Commit Secret Check

Before every submission/release:

1. Inspect `git status` and staged changes.
2. Search filenames for `.env`, `secret`, `credential`, `token`, `key`, and service-account patterns.
3. Run a secret scanner if available.
4. Verify generated evidence contains no reviewer identity.
5. Verify model/data artifacts are distributed through the approved submission channel, not public Git.

## Approved Configuration Pattern

Commit `.env.example` with variable names and non-sensitive examples. Supply real values through local `.env`, Colab secrets, or deployment environment variables.
