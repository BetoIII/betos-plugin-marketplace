# Rocketlane API endpoint catalog

Base URL: `https://api.rocketlane.com/api/1.0` unless a row says **v1** (then `https://api.rocketlane.com/api/v1`).
Auth: header `api-key: <key>` on every request.

Per-endpoint docs live at `https://developer.rocketlane.com/reference/<slug>.md` (full index:
`https://developer.rocketlane.com/llms.txt`). When you need an exact request schema that isn't
spelled out below, fetch the doc page before calling — don't guess payload shapes.

## Filters, sorting, pagination (list/search endpoints)

- Filter syntax: `field.operator=value` as query params. Operators: `eq`, `gt`, `lt`, `ge`, `le`,
  `cn` (contains), `nc` (not contains), `oneOf`, `noneOf` (comma-separated values).
- Custom-field filters: `{objectType}.field.{fieldId}.{operator}=value`,
  e.g. `project.field.14.value=2023-12-24`. Operators: `value`, `contains`, `notContains`,
  `greaterThan`, `lessThan`, `greaterThanEqual`, `lessThanEqual`, `isEmpty`, `isNotEmpty`,
  `isTrue`, `isFalse`, `oneOf`, `noneOf`, `isNot`.
- `match=all` (AND, default) or `match=any` (OR) combines multiple filters.
- Sorting: `sortBy=<field>&sortOrder=ASC|DESC` (default DESC).
- Pagination: `pageSize` (max/default 100) + `pageToken`. Response envelope:
  `pagination: { pageSize, hasMore, totalRecordCount, nextPageToken, nextPage }`.
  `nextPageToken` expires after ~15 minutes. **Always call HTTPS even if `nextPage` says http.**
- Extra response fields: `includeFields=<comma,list>` or `includeAllFields=true`.

## Projects

| Method | Path | Purpose / notes | Doc slug |
|---|---|---|---|
| GET | `/projects` | Search. Filters: `projectName.eq/.cn/.nc`, `startDate.*`, `dueDate.*`, `status.eq/.oneOf/.noneOf`, `customerId.*`, `teamMemberId.*`, `companyId.*`, `contractType.*` (FIXED_FEE, TIME_AND_MATERIAL, SUBSCRIPTION, NON_BILLABLE), `inferredProgress.eq` (ON_TRACK, AHEAD_OF_TIME, RUNNING_LATE, NONE), `annualizedRecurringRevenue.*`, `projectFee.*`, `budgetedHours.*`, `allocatedHours.*`, `includeArchive.eq`, `externalReferenceId.eq`. Sort: projectName, startDate, dueDate, annualizedRecurringRevenue, projectFee | get-all-projects |
| POST | `/projects` | Create project | create-project |
| GET | `/projects/{projectId}` | One project (name, dates, owner, status.label, fields[], teamMembers) | get-project |
| PUT | `/projects/{projectId}` | Update (incl. custom fields via `fields[]`) | update-project |
| DELETE | `/projects/{projectId}` | Delete — prefer archive | delete-project |
| POST | `/projects/{projectId}/archive` | Archive (no body, 204) | archiveproject |
| POST | `/projects/{projectId}/add-members` | Body: `{"members":[{userId/emailId}], "customers":[...]}` | add-members |
| POST | `/projects/{projectId}/remove-members` | Remove members/customers | remove-members |
| POST | `/projects/{projectId}/import-template` | Import a template | import-template |
| POST | `/projects/{projectId}/assign-placeholders` | Assign placeholders to a user | assign-placeholders |
| POST | `/projects/{projectId}/unassign-placeholders` | Un-assign placeholders | unassign-placeholders |

## Tasks

| Method | Path | Purpose / notes | Doc slug |
|---|---|---|---|
| GET | `/tasks` | Search. Filters: `projectId.eq`, `phaseId.eq`, `taskName.eq/.cn/.nc`, `startDate.*`, `dueDate.*`, `startDateActual.*`, `dueDateActual.*`, `createdAt.*`/`updatedAt.*` (epoch ms), `effortInMinutes.*`, `progress.*`, `task.status.eq/.oneOf/.noneOf`, `project.status.*`, `externalReferenceId.eq`, `includeArchive.eq`. Sort: taskName, startDate, dueDate, startDateActual, dueDateActual. `includeFields`: phase, assignees, followers, dependencies, type, billable, priority, parent, … | get-all-tasks |
| POST | `/tasks` | Create. Required: `taskName`, `project.projectId`. Optional: `taskDescription` (HTML), `startDate`/`dueDate` (YYYY-MM-DD), `effortInMinutes`, `progress`, `atRisk`, `type` (TASK\|MILESTONE), `phase.phaseId`, `status.value`, `fields[]`, `assignees`, `followers`, `parent.taskId`, `private` | create-task |
| GET | `/tasks/{taskId}` | One task | get-task |
| GET **v1** | `/tasks/{taskId}` | Same, but response includes `attachments[]` (`attachmentId`, `isDeleted`, `createdAt`) — only v1 returns attachments | — |
| PUT | `/tasks/{taskId}` | Update | update-task |
| DELETE | `/tasks/{taskId}` | Delete | delete-task |
| POST | `/tasks/{taskId}/add-assignees` | Body: `{"members":[{userId/emailId}], "placeholders":[...]}` | add-assignee-to-task |
| POST | `/tasks/{taskId}/remove-assignees` | Remove assignees | remove-assignees-from-task |
| POST | `/tasks/{taskId}/add-followers` | Add followers | add-followers-to-task |
| POST | `/tasks/{taskId}/remove-followers` | Remove followers | remove-followers-from-task |
| POST | `/tasks/{taskId}/add-dependencies` | Add dependencies | add-dependencies-to-task |
| POST | `/tasks/{taskId}/remove-dependencies` | Remove dependencies | remove-dependencies-from-task |
| POST | `/tasks/{taskId}/move-phase` | Body: `{"phase":{"phaseId":201}}` | move-task-to-given-phase |

## Attachments (v1 only)

| Method | Path | Purpose / notes |
|---|---|---|
| GET **v1** | `/attachments/{attachmentId}/download` | Binary download; filename in `x-filename` header (fallback: `content-disposition`) |

## Phases

| Method | Path | Doc slug |
|---|---|---|
| GET | `/phases` (filter `projectId.eq=`) | get-all-phases |
| POST | `/phases` | create-phase |
| GET / PUT / DELETE | `/phases/{phaseId}` | get-phase / update-phase / delete-phase |

## Fields (custom-field definitions)

| Method | Path | Purpose | Doc slug |
|---|---|---|---|
| GET | `/fields` | List field definitions: `fieldId`, `fieldLabel`, `objectType` (PROJECT/TASK/…), `fieldOptions[]` (`optionValue`/`optionLabel`). Use this to resolve a label → fieldId before writing | get-all-fields |
| POST | `/fields` | Create a field | create-field |
| GET / PUT / DELETE | `/fields/{fieldId}` | Manage one field | get-field / update-field / delete-field |
| POST | `/fields/{fieldId}/...` | Add/update field options — fetch doc for exact path | add-field-option / update-field-option |

## Users & Placeholders

| Method | Path | Doc slug |
|---|---|---|
| GET | `/users` | get-all-users |
| GET | `/users/{userId}` | get-user |
| GET | `/placeholders` | get-placeholders |

## Time entries

| Method | Path | Purpose / notes | Doc slug |
|---|---|---|---|
| GET | `/time-entries` | List/search. Filters like `date.gt=2023-02-11`, `minutes.eq=250`; `sortBy`/`sortOrder` | get-all-time-entries |
| POST | `/time-entries` | Create. Required: `date` (YYYY-MM-DD), `minutes` (1–1440), plus exactly ONE source: `activityName` \| `task.taskId` \| `projectPhase` \| `project.projectId`. Optional: `billable` (default true), `notes`, `user`, `category`, `fields[]` | create-time-entry |
| POST | `/time-entries/search` | Search (same filter syntax) — fetch doc for exact path/body | search-time-entries |
| GET | `/time-entries/{timeEntryId}` | `includeFields`: notes, sourceType, status, approvedBy, billRate, … | get-time-entry |
| PUT | `/time-entries/{timeEntryId}` | `date` + `minutes` mandatory; can update `activityName`, `notes`, `billable`, `minutes` | update-time-entry |
| DELETE | `/time-entries/{timeEntryId}` | 204 on success | delete-time-entry |
| GET | `/time-entry-categories` | Categories — fetch doc to confirm path | get-time-entry-categories |

## Time-offs

| Method | Path | Doc slug |
|---|---|---|
| GET | `/time-offs` | get-all-timeoffs |
| POST | `/time-offs` | create-timeoff |
| GET / DELETE | `/time-offs/{timeOffId}` | get-timeoff / delete-timeoff |

## Resource allocations

| Method | Path | Doc slug |
|---|---|---|
| GET | `/resource-allocations` | get-all-resource-allocations |

## Spaces & Space documents

| Method | Path | Doc slug |
|---|---|---|
| GET | `/spaces` (filter `projectId.eq=`) | get-all-spaces |
| POST | `/spaces` | create-space |
| GET / PUT / DELETE | `/spaces/{spaceId}` | get-space / update-space / delete-space |
| GET | `/space-documents` | get-all-space-documents |
| POST | `/space-documents` | Body incl. `spaceDocumentName`, `space.id`, `spaceDocumentType` (e.g. EMBEDDED_DOCUMENT), `url` | create-space-document |
| GET / PUT / DELETE | `/space-documents/{documentId}` | get-space-document / update-space-document / delete-space-document |

## Invoices (read-only)

| Method | Path | Doc slug |
|---|---|---|
| GET | `/invoices` | search-invoices |
| GET | `/invoices/{invoiceId}` | get-invoice |
| GET | `/invoices/{invoiceId}/payments` | get-invoice-payments |
| GET | `/invoices/{invoiceId}/line-items` | get-invoice-line-items |
