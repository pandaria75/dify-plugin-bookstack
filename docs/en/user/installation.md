# Installation

## Scope

This repository currently centers on a Dify Tool plugin for BookStack. A separate Datasource package also exists, but the Tool plugin remains the primary user path.

## Prerequisites

- A Dify environment that supports plugin import.
- A reachable BookStack instance.
- BookStack API credentials created in BookStack.

## Current Installation Flow

1. Build or obtain the plugin package from this repository.
2. Import the package into Dify.
3. Open the BookStack provider settings in Dify.
4. Enter credentials through the Dify UI only.
5. Save the provider configuration.

## Notes

- Dify CLI packaging details are version-sensitive.
- Do not paste production secrets into shared docs, screenshots, or commits.
- Datasource packaging and import follow a separate package path and are documented as a separate capability, not the main Tool-plugin flow.
