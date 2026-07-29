# Custom fields & Rain-specific field mapping

## How custom fields appear in responses

Projects and tasks return a `fields` array of objects:

```json
{ "fieldId": 201, "fieldLabel": "MRR", "fieldValue": 1000, "fieldValueLabel": "1000" }
```

Flatten for display with: `{f["fieldLabel"]: f["fieldValueLabel"] for f in obj.get("fields", [])}`.
`fieldValueLabel` is the human-readable value (use it for reports); `fieldValue` is the raw
value/optionValue (use it when writing).

## Writing custom fields

Updates go through the parent resource (`PUT /projects/{id}`, `PUT /tasks/{id}`, or on create)
wrapped in a `fields` array keyed by `fieldId`:

```json
{ "fields": [ { "fieldId": 17, "fieldValue": "value_here" } ] }
```

`fieldValue` format by field type:

| Field type | fieldValue |
|---|---|
| Text / multiline | string |
| Number | number (e.g. `10000.0`) |
| Yes/No | boolean |
| Date | `"YYYY-MM-DD"` string |
| Single choice | one `optionValue` integer |
| Multiple choice | array of `optionValue` integers, e.g. `[1, 4]` |
| Single user | one `userId` |
| Multi user | array of `userId`s, e.g. `[323, 355]` |

To resolve a label to a `fieldId` (and choice labels to `optionValue`s), call `GET /fields`
and match on `fieldLabel` + `objectType`. Never guess IDs.

## Rain's project custom fields (labels seen in this workspace)

| fieldLabel | Meaning |
|---|---|
| Stage | Onboarding/implementation stage |
| Client Priority | Priority assigned to the client |
| Target Launch Date | Planned go-live |
| Tier | Client tier |
| Region | Client region |
| Notes | Free-form notes — value is HTML; strip tags before showing (`re.sub(r"<[^>]+>", "", s)`) |
| Compliance | Compliance track/status |
| Authorization Flow | Card authorization flow |
| Card Type | Card product type |

## Useful native project fields

- `projectName`, `startDate`, `dueDate`, `status.label`
- `owner.firstName` / `owner.lastName`
- `teamMembers.members[]` — Rain staff on the project
- `teamMembers.customers[]` — client contacts (have `emailId`)
- `createdAt` / `updatedAt` are epoch milliseconds

## Useful native task fields

- `taskName`, `taskDescription` (HTML), `startDate`, `dueDate`, `progress`, `atRisk`
- `status` = `{value, label}`; `type` = TASK | MILESTONE
- `project.projectId`, `phase.phaseId`, `assignees.members[]`, `dependencies[]`
