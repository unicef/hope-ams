
[<img src="./docs/src/img/badge.png" style="margin-left: auto;margin-right: auto;width:300px;display:block"/>](./docs/src/img/hope_workspace.png)

# Anomaly Management System (AMS)

---

[![Test](https://github.com/unicef/hope-ams/actions/workflows/test.yml/badge.svg)](https://github.com/unicef/hope-ams/actions/workflows/test.yml)
[![Lint](https://github.com/unicef/hope-ams/actions/workflows/lint.yml/badge.svg)](https://github.com/unicef/hope-ams/actions/workflows/lint.yml)
[![codecov](https://codecov.io/github/unicef/hope-ams/graph/badge.svg?token=FBUB7HML5S)](https://codecov.io/github/unicef/hope-ams)
[![Documentation](https://github.com/unicef/hope-ams/actions/workflows/docs.yml/badge.svg)](https://unicef.github.io/hope-ams/)
[![Docker Pulls](https://img.shields.io/docker/pulls/unicef/hope-ams)](https://hub.docker.com/repository/docker/unicef/hope-ams/tags)


Standalone Django service for rule-based anomaly detection on HOPE payment data.

📖 [Documentation](https://unicef.github.io/hope-ams) · [Contributing](CONTRIBUTING.md)


[<img src="./docs/src/img/dashboard.png" style="margin-left: auto;margin-right: auto;width:500px;display:block"/>](./docs/src/img/hope_workspace.png)


## Components

### Input

| Component | Description  	                                                  |
|-------|-----------------------------------------------------------------|
| Office| Represents UNICEF Country Office,equivalent of HOPE BusinesArea |
| Programme	 | Assistance Programme, same as in HOPE  	                        |
| PaymentPlan	 | Frozen/Serialized HOPE PaymentPlan  	                           |


### Engine

| Component    | Description  	                            |
|--------------|-------------------------------------------|
| Rule         | Logic used to analyse data                |
| RuleConfig	  | Rule configuration, thresholds etc.  	    |
| ProgramRuleConfiguration	 | Custom RuleConfig for specific Programme	 |


## Scope

Anomalies can be performed against PaymentPlan (and included Beneficiaries), or at Household (only) level. Each rule is designed to receive PaymentPlan or Household informations.


## Flows

AMS has two different flows, each pre (analyse) and post (detect) payment.

### Analyse

Analyse flow aims to detect anomalies BEFORE payment is executed to find data mismatch or anomalies in the beneficiary data

### Detect

Detect flow uses payment information to search for anomalies (es. amount mismatch, excessive amount ....)
