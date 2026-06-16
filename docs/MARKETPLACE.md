# Marketplace Guide

## Current Goal

The long-term goal is to make this plugin eligible for Dify Marketplace submission once the MVP is stable.

## Required Assets

- `manifest.yaml`
- `README.md`
- `PRIVACY.md`
- `_assets/icon.svg`

## Packaging Flow

1. Install the Dify plugin CLI.
2. Validate the plugin locally.
3. Package the repository into a single `.difypkg` file.
4. Test the package in a Dify environment.

## GitHub Release Flow

1. Tag a release.
2. Attach the `.difypkg` artifact.
3. Document the version and changelog.

## Marketplace PR Flow

1. Review the current Marketplace submission requirements.
2. Ensure the README is English-only.
3. Ensure privacy disclosures are complete.
4. Prepare a PR to the Dify plugins repository only when the plugin is stable enough.
