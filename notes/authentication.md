# Authentication & Authorization

## Authentication

Authentication verifies the identity of the user. It answers:

- Is bob@example.com a real user within our system?

- Did he provide the correct password?

### Session-based Authentication

**Flow**:

- The client sends their credentials (email and password) to an endpoint.

- The server verifies the credentials.

- If valid, the server creates a session record. That record is stored on the backend, in memory, a database or Redis. The client gets only the session ID as a cookie.

- On each subsequent request, the server looks up the session ID in its store to find out who the user is.

### Token-based Authentication

A token is a string that represents the user's identity. Tokens expire over time.

**Flow**:

- The client sends their credentials (email and password) to an endpoint.

- The server verifies the credentials.

- If the credentials are valid, the server creates and sends back a signed token containing the data itself plus a signature.

- The client chooses how to store the token (cookies, localStorage).

- The client includes the token on every subsequent request typically as a header.

- The server verifies the token's legitimacy (ensuring it is not tempered with) on every request and reads the user ID from the token.

Token-based authentication is stateless (the server stores nothing) unlike `session-based auth`, where the server has to store the per-user session data.

- The server does not need to query the database to verify the user is logged in. Simply the presence and verification of the token proves that the user is logged in. 

- The token carries the information and the signature proves the server issued it and nobody tempered with it.

- Because the server stores nothing, it can't revoke a token before it expires. That's why tokens are short-lived.

### JWT Token

A JWT is a string that contains encoded user information.

A JWT consists of 3 separate segments separated by dots: `Header.Payload.Signature`. All 3 segments are Base64URL encoded strings.

1. **Header**: Declares the algo used to sign the JWT

2. **Payload**: Stores the user information: user ID, name, expiration time

    - The technical terminology for a key-value pair within the payload is called a `claim`.

3. **Signature**: It proves the token has not been tempered with. It is created using a secret key on the server.

### Refresh Token

The access token is a short-lived (10 minutes) token that grants access to the system. The refresh token is longer-lived (7 days) token that grants access to new access token.

### JWT Invalidation

Logout becomes client's responsibility. We can't delete a JWT from a server because the server does n't have it.

- Logout button: Frontend app deletes the JWT token from wherever it is being stored

If a malicious user gets access, they can impersonate as that user. That's why JWTs have a short expiration time.

If backend needs to revoke a JWT before it expires, it must intorduce some form of server-side state.

- Store revoked JWTs in a database/Redis

- On every request, make sure JWT is not found in the revoked collection.

### Reset Password

If the user is authenticated:

- We can define a patch endpoint, where the user provides their new and current passwords

If the user forgets his password:

- User requests a password reset by providing their email to an endpoint

- The server generates a token and sent it to their email

- User clicks the link in the email

- User is taken to an app page that includes the token (usually as query param)

- User completes a form with their new password, submission hits another endpoint and passes the token

- Server verifies the token is valid, unexpired and belongs to user etc. and udpates the password

## Authorization

Authorization is the act of allowing or prohibiting the user from taking an action after they have authenticated. It answers:

- What Bob is allowed to do?