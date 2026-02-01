# Azure DevOps Pipeline Report Automation

## Overview:

This project is a Python-based automation solution designed to **fetch warning messages from the latest builds of Azure DevOps pipelines** across multiple projects and generate a consolidated report.

The script helps identify **deprecated versions, configuration warnings, and pipeline issues** that are otherwise time-consuming to track manually across a large number of projects.

**---**

## Environment:

- **Platform:** Azure DevOps  
- **Language:** Python  
- **APIs Used:** Azure DevOps REST APIs  

## Problem Statement:
Many Azure DevOps pipelines generate **deprecated version warnings** and other non-fatal issues during builds.

- These warnings are spread across **multiple projects and pipelines**
- Manually checking warnings across 100 plus projects is time-consuming and inefficient.
- Important warnings are often ignored until they cause build failures.

**---**

## Solution:

This automation script:
- Collects warning messages from **latest pipeline builds**
- Centralizes the data into a **single CSV report**
- Enables teams to **proactively address pipeline warnings**
- Saves significant manual effort and time and add reusability for next time

**---**

## What the Script Does:

The script performs the following steps:

1. Fetches all projects in an Azure DevOps organization
2. Retrieves all pipelines in each project
3. Finds the latest build from a specified branch (default: `develop`)
4. Extracts warning messages from the build timeline
5. Generates a CSV report with warning details
6. Stores the report in the Azure Pipeline artifact staging directory






