# ActivityPub Activity Types (C2S)

This document details common Activity types sent by clients to the Outbox.

### 1. Create

Used to create a new object (e.g., Note, Article).

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Create",
  "actor": "https://social.example/users/alice",
  "object": {
    "type": "Note",
    "content": "This is a new note",
    "attributedTo": "https://social.example/users/alice",
    "to": ["https://www.w3.org/ns/activitystreams#Public"]
  }
}
```

### 2. Update

Used to modify an existing object.

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Update",
  "actor": "https://social.example/users/alice",
  "object": {
    "id": "https://social.example/users/alice/notes/1",
    "type": "Note",
    "content": "Updated content"
  }
}
```

### 3. Delete

Used to delete an object. Often replaced by a `Tombstone` after deletion.

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Delete",
  "actor": "https://social.example/users/alice",
  "object": "https://social.example/users/alice/notes/1"
}
```

### 4. Follow

Used to subscribe to another actor's updates. Usually requires an `Accept` activity from the target.

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Follow",
  "actor": "https://social.example/users/alice",
  "object": "https://social.example/users/bob"
}
```

### 5. Undo

Used to reverse a previous activity (e.g., Unfollow, Unlike).

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Undo",
  "actor": "https://social.example/users/alice",
  "object": {
    "type": "Follow",
    "actor": "https://social.example/users/alice",
    "object": "https://social.example/users/bob"
  }
}
```

### 6. Like

Used to signal that the actor likes an object.

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Like",
  "actor": "https://social.example/users/alice",
  "object": "https://social.example/users/bob/notes/1"
}
```

### 7. Announce

Used to share/boost/repost an object.

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Announce",
  "actor": "https://social.example/users/alice",
  "object": "https://social.example/users/bob/notes/1"
}
```
