TODOs/Roadmap
================================================
Based on the MoSCoW principle. Must haves and should haves are planned to be worked on.

* Features/issues marked with plus (+) are implemented/solved.
* Features/issues marked with minus (-) are yet to be implemented.

Must haves
------------------------------------------------
- Possibly to be able to set the GoogleAuthenticator required for certain users/groups
  to use the two-step verification.
- At the moment, Plone top login link (AJAX overlay) doesn't work with Google Authenticator. Default
  "popupforms.js" has been overridden by a custom one, where the part of login forms being shown in
  an overlay has been commented out. Make Google Authenticator working with overlays.
- Fallback code in GoogleAuthenticator setup and recover.
- When GoogleAuthenticator is skipped (white-listed address or user that doesn't have it enabled),
  the came_from functionality doesn't work.
- On disable two-step verification, redirect user to where he was.
- Get rid of annoying "Sure to leave this page" message when editing the GoogleAuthenticator settings.
- Take away one step from the process. If user confirms his code, immediately log him in.
- Add IP logging and admin helper views for viewing the used IPs.

Should haves
------------------------------------------------

Could haves
------------------------------------------------

Would haves
------------------------------------------------
