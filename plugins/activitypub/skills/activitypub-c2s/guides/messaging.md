# ActivityPub Messaging: Inbox, Outbox, & Side Effects

This document explains how messages are delivered and processed in ActivityPub (Client-to-Server).

## Inbox / Outbox

*   **Outbox**: The endpoint where a user posts Activities (via POST). It can also be read (via GET) to see the user's public activities.
*   **Inbox**: The endpoint where a user receives messages (from other servers or users). In C2S, clients read from here. In S2S, other servers POST here.

## Side Effects (Server Implementations)

When a server receives an Activity in the Outbox (C2S), it must perform specific side effects:

1.  **Validation**: Check authentication, authorization, and object structure.
2.  **ID Generation**: Assign a unique URI to the new object (if applicable, e.g., on `Create`).
3.  **Persistence**: Save the object/activity to the database.
4.  **Federation (Delivery)**:
    *   Analyze `to`, `cc`, and `audience` fields.
    *   Resolve Inboxes for recipients (handling Shared Inboxes for efficiency).
    *   Deliver the Activity to external servers (S2S).
5.  **Collection Updates**: Update the user's `outbox`, `followers`, `likes`, etc., as appropriate.
