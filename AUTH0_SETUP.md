# Auth0 setup

Set these environment variables in Vercel and locally:

```text
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_CLIENT_ID=your Auth0 SPA client ID
AUTH0_AUDIENCE=https://ag2-platform-api
```

In Auth0, configure the application URLs to include the exact deployed URL:

- Allowed Callback URLs: `https://YOUR_DOMAIN/login.html`
- Allowed Logout URLs: `https://YOUR_DOMAIN/login.html`
- Allowed Web Origins: `https://YOUR_DOMAIN`

Create an API in Auth0 with identifier equal to `AUTH0_AUDIENCE`, enable RS256 signing, and use a Regular Web Application or SPA client as appropriate. Never commit the client secret or Auth0 management credentials. The frontend receives an access token and the FastAPI backend validates it using Auth0's JWKS endpoint.
