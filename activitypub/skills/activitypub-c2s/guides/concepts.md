# ActivityPub Concepts: JSON-LD, Actor, & IDs

This document covers the fundamental data structures and concepts in ActivityPub.

## JSON-LD & Context

ActivityPub objects are JSON-LD documents. They must include the `@context` property.

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Note",
  "content": "Hello world"
}
```

## Actor

An Actor represents a user, group, organization, or application.

```json
{
  "type": "Person",
  "id": "https://social.example/users/alice",
  "name": "Alice",
  "inbox": "https://social.example/users/alice/inbox",
  "outbox": "https://social.example/users/alice/outbox"
}
```

## ID & URI Structure

Every object in ActivityPub must have a unique, persistent URI (ID).

*   `https://social.example/users/{username}` (Actor)
*   `https://social.example/users/{username}/outbox` (Collection)
*   `https://social.example/users/{username}/notes/{uuid}` (Object)
*   `https://social.example/users/{username}/activities/{uuid}` (Activity)
