# Polymarket Trade Monitor & Wallet Evaluator

## Overview

This Python script monitors new trades on Polymarket and evaluates the wallets involved in those trades based on their trading history, profitability, and win rate. The script sends notifications to a Discord webhook if a wallet meets the predefined criteria, indicating it as a potentially good wallet.

## Features

- **Trade Monitoring**: Continuously monitors new trades on Polymarket.
- **Wallet Evaluation**: Evaluates wallets based on:
  - Win rate threshold.
  - Minimum number of tokens traded.
  - Minimum profit.
- **Discord Notifications**: Sends detailed notifications to a specified Discord webhook if a wallet meets the evaluation criteria.
- **Customizable Parameters**:
  - Profit threshold.
  - Minimum tokens traded.
  - Minimum profit.

## Prerequisites

- Python 3.x
- Required Python libraries:
  - `requests`
  - `time`
  - `datetime`

You can install the required libraries using `pip`:

```bash
pip install requests
