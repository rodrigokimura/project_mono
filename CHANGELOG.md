## 2.0.1 (2022-01-26)

### Fix

- **mono**: suppress warnings on tests

## 2.0.0 (2022-01-25)

### Refactor

- **mono**: squash migrations

### BREAKING CHANGE

- sensitive change, since it changes models on almost every app

## 1.1.19 (2022-01-24)

### Refactor

- **mono**: apply pylint changes

## 1.1.18 (2022-01-24)

### Refactor

- **finance**: apply pylint changes

## 1.1.17 (2022-01-23)

### Refactor

- **finance**: apply pylint changes

## 1.1.16 (2022-01-23)

### Refactor

- **finance**: apply pylint changes

## 1.1.15 (2022-01-23)

### Refactor

- **healthcheck**: apply pylint changes

## 1.1.14 (2022-01-23)

### Refactor

- **notes**: apply pylint changes

## 1.1.13 (2022-01-22)

### Refactor

- **pixel**: apply pylint changes

## 1.1.12 (2022-01-22)

### Refactor

- **project_manager**: apply pylint changes

## 1.1.11 (2022-01-22)

### Refactor

- **project_manager**: apply pylint changes

## 1.1.10 (2022-01-22)

### Refactor

- **restricted_area**: apply pylint changes

## 1.1.9 (2022-01-22)

### Refactor

- **restricted_area**: apply pylint changes

## 1.1.8 (2022-01-22)

### Fix

- **shiper**: add comparison for sorting

## 1.1.7 (2022-01-21)

### Refactor

- **shipper**: apply pylint changes

## 1.1.6 (2022-01-21)

### Refactor

- **todo_lists**: apply pylint changes

## 1.1.5 (2022-01-21)

### Refactor

- **watcher**: apply pylint changes

## 1.1.4 (2022-01-21)

### Refactor

- **mono**: improve pylint score

## 1.1.3 (2022-01-20)

### Refactor

- **makefile**: add command to SSH into prod server

## 1.1.2 (2022-01-20)

### Fix

- **healthcheck**: fix syntax error

## 1.1.1 (2022-01-20)

### Refactor

- **healthcheck**: change way to retrieve last merge commit

## 1.1.0 (2022-01-20)

### Feat

- **healthcheck**: add pull command to mark_as_deployed

### Fix

- **shipper**: change coloring of portmanteaus

## 1.0.0 (2022-01-20)

### Feat

- **healthcheck**: save last commit's SHA to PR instance

### BREAKING CHANGE

- new PR model field

## 0.1.3 (2022-01-20)

### Refactor

- **accounts**: move models, views and routes related to stripe
- remove code dups

## 0.1.2 (2022-01-20)

### Fix

- **mono**: adjust commit command in makefile

### Refactor

- **mono**: change makefile

## 0.1.1 (2022-01-20)

### Refactor

- **mono**: change dependencies in pipfile

## 0.1.0 (2022-01-20)

### Refactor

- **mono**: move common widget from app to project level
- **mono**: move common widgets to higher level
- **project_manager**: remove code duplicate and minor quality issues
- **mono**: add make command to run dev server
- **mono**: add make command to run dev server
- **mono**: remove duplicate code
- **mono**: configure admin email
- **mono**: configure admin email

### Fix

- **shipper**: change coloring of portmanteaus
- **shipper**: update test
- **shipper**: make migrations
- **finance**: fix api call
- **finance**: fix api call
- **finance**: adjust datetime creation
- **finance**: adjust datetime creation
- **finance**: handle no axis
- **finance**: handle no axis
- **finance**: update description and action url for recurrent transaction notification
- **finance**: make migrations
- **finance**: create transaction on recurrent transaction in the past
- **finance**: set proper model ordering
- **finance**: fix chart queryset
- **finance**: fix chart queryset
- **finance**: fix data in chart
- **finance**: fix data in chart
- **finance**: fix format
- **finance**: fix format
- **finance**: fix wrong format
- **finance**: fix wrong format
- **finance**: fix card order template
- **finance**: fix card order template
- **watcher**: prevent use of bfcache making the issues list always up…
- **watcher**: prevent use of bfcache making the issues list always updated
- **finance**: fix missing code
- **finance**: fix missing code
- **finance**: :ambulance: fix wrong code

### Feat

- **shipper**: add portmanteau model
- **shipper**: add portmanteau model
- **finance**: add data labels to donut chart
- **finance**: add data labels to donut chart
- **finance**: :sparkles: add new card to finance homepage
- **notes**: improve layout
- **shipper**: simplify input
- **shipper**: add form
- **shipper**: :sparkles: add new app
- **finance**: implement chart order
- **finance**: implement chart order
- **finance**: add filter to show future transactions
- **finance**: allow chart editing
- **finance**: allow chart editing
- **finance**: add option to delete chart
- **finance**: add modal to create charts
- **finance**: add endpoints to create, edit and delete charts
- **finance**: add title and order fields
- **finance**: add donut chart
- **finance**: add donut chart
- **finance**: allow no category in chart
- **finance**: allow no category in chart
- **finance**: add dynamic charts page
- **finance**: add dynamic charts page
- implement queryset generator for charts
- implement queryset generator for charts
- **mono**: host twemoji
- **mono**: host twemoji
- **restricted_area**: add reporting view and command
- **project_manager**: :sparkles: add buttons to sort projects and boards

### Perf

- **finance**: decrease complexity
